from data_model.types.metatype.base_type import *
from data_model.types.metatype.complex import *
from data_model.actual_data.track import TrackInfo
from data_model.actual_data._story.story_pos import *
from data_model.types.url import UrlModel
from data_model.loader import i18n_translator
from data_model.types.lang_string import LangStringModelList
from data_model.loader import FileLoader
from data_model.constant.file_type import FILE_STORY_MAIN, FILE_STORY_SIDE, FILE_STORY_SHORT, FILE_STORY_EVENT, \
    FILE_STORY_OTHER, FILE_STORY_BOND
from ._story.story_part import StoryInfoPartListManager
from ._story.story_part_auto import StoryPartAutoData
from ._story.story_source_all import StoryInfoSource
from ..tool.parent_data import IParentData
from ..tool.interpage import InterpageMixin
from .reference_data import ReferenceData
from collections import OrderedDict


class StoryInfo(FileLoader, IParentData, InterpageMixin):
    uuid = UUID('uuid')
    filetype = Integer('filetype')
    is_battle = Bool('is_battle')

    _story_type = {FILE_STORY_MAIN: "MAIN", FILE_STORY_SIDE: "SIDE", FILE_STORY_SHORT: "SHORT",
                   FILE_STORY_EVENT: "EVENT", FILE_STORY_OTHER: "OTHER"}
    _instance = OrderedDict()

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]
        self.is_battle = data["is_battle"]

        self.name = i18n_translator[data["name"]]
        self.pos = storyPosAuto(data["pos"])
        self.image = UrlModel()
        self.source = StoryInfoSource(data.get("source", {}))
        self.part = StoryInfoPartListManager(data["part"], self)
        self.image.load(self.data["image"])

        # Special case: some stories still have content after the battle,
        # and in that case, there will be two description text.
        # The code here can handle either single string or a list with strings,
        # and it will normalize into a list with LangStringModel in both cases.
        self.desc = LangStringModelList('desc')
        if isinstance(data["desc"], str):
            self.desc.append(i18n_translator[data["desc"]])
        else:
            for i in data["desc"]:
                self.desc.append(i18n_translator[i])

        self.extra_register()

    def extra_register(self):
        # Register itself to every track in StoryInfoPartListManager
        # For every story (not story parts) it should only be registered for once
        registered = []

        for part in self.part.part:
            for segment in part.segments:
                for track in segment.track.track:
                    if track not in registered:
                        track.register(self)
                        registered.append(track)
                for char in segment.character.character:
                    if char not in registered:
                        char.register(self)
                        registered.append(char)
                for background in segment.background.background:
                    if background not in registered:
                        background.register(self)
                        registered.append(background)

        # 各个StoryPart里头的register
        # 基本上相当于把 StoryPartInfo.extra_register 给取代了
        registered = {}

        for part in self.part.part:
            # 一般的都在segment精度追踪
            for segment in part.segments:
                # For CharacterInfo
                # register every TrackInfo to CharacterInfo
                for char in segment.character.character:
                    for track in segment.track.track:
                        if char not in registered.keys():
                            registered[char] = []
                        if track not in registered.keys():
                            registered[track] = []

                        if track not in registered[char]:
                            char.register(track)
                            registered[char].append(track)
                        if char not in registered[track]:
                            track.register(char)
                            registered[track].append(char)

                # For BackgroundInfo
                for background in segment.background.background:
                    if background not in registered.keys():
                        registered[background] = []

                    for track in segment.track.track:
                        if track not in registered.keys():
                            registered[track] = []

                        if track not in registered[background]:
                            background.register(track)
                            registered[background].append(track)
                        if background not in registered[track]:
                            track.register(background)
                            registered[track].append(background)

                    for char in segment.character.character:
                        if char not in registered.keys():
                            registered[char] = []

                        if char not in registered[background]:
                            background.register(char)
                            registered[background].append(char)
                        if background not in registered[char]:
                            char.register(background)
                            registered[char].append(background)

            # 以下是专门为char-char（in story）进行
            # 该部分数据仅精确到part
            part_characters = list(set([char for segment in part.segments for char in segment.character.character]))
            for char in part_characters:
                for char2 in part_characters:
                    if char.uuid == char2.uuid:
                        continue

                    if char not in registered.keys():
                        registered[char] = []
                    if char2 not in registered.keys():
                        registered[char2] = []

                    if char2 not in registered[char]:
                        char.register(char2)
                        registered[char].append(char2)
                    if char not in registered[char2]:
                        char2.register(char)
                        registered[char2].append(char)

    @staticmethod
    def _get_instance_id(data: dict):
        story_type = StoryInfo._story_type[data["filetype"]]
        story_pos = data["pos"].values()
        story_pos = [str(i) for i in story_pos]
        return "_".join([story_type, *story_pos])

    def parent_data_to_json(self):
        if self.parent_data is None:
            return self.parent_data
        else:
            l = [self.export_parents_to_json_without_last_parent(i) for i in
                 self.unpack_parents(self.parent_data, False)]
            return l

    def to_json(self):
        t = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "filetype_sub": 0,
            "namespace": self.namespace,

            "name": self.name.to_json_basic(),
            "desc": [i for i in self.desc.to_json_basic()],
            "pos": self.pos.to_json_basic(),
            "image": self.image.to_json_basic(),
            "instance_id": self.instance_id,

            "part": self.part.to_json(),
            "is_battle": self.is_battle,
            "source": self.source.to_json_basic(),
            "interpage": self.get_interpage_data()
        }
        if self.is_battle:
            t["bgm_special"] = self.part.to_json_basic_tracks()
        if self.parent_data:
            t["parent_data"] = self.parent_data_to_json()
        return t

    def to_json_basic(self):
        return self.to_json()

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)

    def _get_instance_offset(self, offset: int):
        instances_list = list(self._instance.keys())
        self_instance_pos = instances_list.index(self.instance_id)

        if self_instance_pos == 0:
            if offset < 0:
                return None

        try:
            instance = self._instance[instances_list[self_instance_pos + offset]]
        except (KeyError, IndexError):
            return None

        if instance.filetype != self.filetype:
            # 故事类型不一致
            return None

        # 获取pos
        pos_value = self.pos.get_all_pos()
        # 根据不同的pos区分
        if len(pos_value) == 2:
            # event_id/character不一样
            if pos_value[0] != instance.pos.get_all_pos()[0]:
                return None
        elif len(pos_value) == 3:
            # volume 不一样
            if pos_value[0] != instance.pos.get_all_pos()[0]:
                return None

        return instance

    @staticmethod
    def process_reference_data(data: dict):
        try:
            if data["module_name"] == "":
                module_name = "data_model.actual_data.story"
            else:
                module_name = data["module_name"]
        except KeyError:
            module_name = "data_model.actual_data.story"

        try:
            if data["model_name"] == "":
                model_name = "StoryInfo"
            else:
                model_name = data["model_name"]
        except KeyError:
            model_name = "StoryInfo"

        return (module_name, model_name, data["instance_id"])

    @property
    def interpage_prev(self):
        try:
            self.data["interpage"]["prev"]
        except KeyError:
            return super().interpage_prev
        else:
            ref_data = self.data["interpage"]["prev"]
            return ReferenceData(*self.process_reference_data(ref_data)).ref_instance

    @property
    def interpage_next(self):
        try:
            self.data["interpage"]["next"]
        except KeyError:
            return super().interpage_next
        else:
            ref_data = self.data["interpage"]["next"]
            return ReferenceData(*self.process_reference_data(ref_data)).ref_instance

    def get_mixed_interpage_data(self, prev, next):
        return {
            "prev": {
                "name": prev.name.to_json_basic() if prev else "[NO_PREV]",
                "namespace": prev.namespace if prev else "[NO_PREV]",
                "is_battle": prev.is_battle if prev else "[NO_PREV]",
                "pos": prev.pos.to_json_basic() if prev else "[NO_PREV]"
            },
            "next": {
                "name": next.name.to_json_basic() if next else "[NO_NEXT]",
                "namespace": next.namespace if next else "[NO_NEXT]",
                "is_battle": next.is_battle if next else "[NO_NEXT]",
                "pos": next.pos.to_json_basic() if next else "[NO_NEXT]"
            }
        }


class StoryInfoBond(FileLoader, IParentData, InterpageMixin):
    """Basically a modified class from StoryInfo"""
    _instance = OrderedDict()

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        from .character import StudentInfo

        self.data = data = kwargs["data"]
        self.namespace = kwargs["namespace"]
        self.filetype = data["filetype"]
        self.uuid = data["uuid"]
        self.is_memory = data["is_memory"]

        self.name = i18n_translator[data["name"]]
        self.pos = storyPosAuto(data["pos"])
        self.source = StoryInfoSource(data.get("source", {}))

        self.stu = StudentInfo.get_instance(instance_id=self.pos.student.upper())

        # Special case: some stories still have content after the battle,
        # and in that case, there will be two description text.
        # The code here can handle either single string or a list with strings,
        # and it will normalize into a list with LangStringModel in both cases.
        self.desc = LangStringModelList('desc')
        if isinstance(data["desc"], str):
            self.desc.append(i18n_translator[data["desc"]])
        else:
            for i in data["desc"]:
                self.desc.append(i18n_translator[i])

    def after_instantiate(self):
        # To avoid that when creating a student's bond story,
        # it can't find itself since it's in the process of being created.
        self.part = StoryInfoPartListManager(self.data["part"], self)

        # 如果当前为回忆大厅剧情，则绑定学生的bond_track
        if self.is_memory:
            self.stu.bond_track = self.part.bgm_special[0]
            self.stu.bond_rank = self.pos.favor_rank

        self.extra_register()

    def extra_register(self):
        StoryInfo.extra_register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        story_pos = data["pos"].values()
        story_pos = [str(i) for i in story_pos]
        return "_".join(["BOND", *story_pos])

    def _get_instance_offset(self, offset: int):
        return StoryInfo._get_instance_offset(self, offset)

    def parent_data_to_json(self):
        return StoryInfo.parent_data_to_json(self)

    def to_json(self):
        t = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "filetype_sub": 0,
            "namespace": self.namespace,

            "name": self.name.to_json_basic(),
            "desc": [i for i in self.desc.to_json_basic()],
            "pos": self.pos.to_json_basic(),
            "image": self.data["image"],
            "instance_id": self.instance_id,

            "part": self.part.to_json(),
            "is_memory": self.is_memory,
            "source": self.source.to_json_basic(),
            "interpage": self.get_interpage_data()
        }

        if self.is_memory:
            t["bgm_special"] = self.part.to_json_basic_tracks()
        try:
            t["parent_data"] = self.parent_data_to_json()
        except AttributeError:
            pass

        # find students
        from .character import StudentInfo
        stu = StudentInfo.get_instance(instance_id=self.pos.student.upper())
        t["student"] = stu.to_json_basic()

        return t

    def to_json_basic(self):
        return self.to_json()

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)

    def get_mixed_interpage_data(self, prev, next):
        return {
            "prev": {
                "name": prev.name.to_json_basic() if prev else "[NO_PREV]",
                "namespace": prev.namespace if prev else "[NO_PREV]",
                "is_memory": prev.is_memory if prev else "[NO_PREV]",
                "pos": prev.pos.to_json_basic() if prev else "[NO_PREV]"
            },
            "next": {
                "name": next.name.to_json_basic() if next else "[NO_NEXT]",
                "namespace": next.namespace if next else "[NO_NEXT]",
                "is_memory": next.is_memory if next else "[NO_NEXT]",
                "pos": next.pos.to_json_basic() if next else "[NO_NEXT]"
            }
        }


class StoryInfoAutoMixin:
    @staticmethod
    def to_json(data):
        temp = data
        temp["filetype_sub"] = 1
        return temp

    @staticmethod
    def to_json_basic(data):
        temp = data
        temp["filetype_sub"] = 1
        return temp


class StoryInfoAuto(StoryInfo, StoryInfoAutoMixin):
    def __init__(self, **kwargs):
        FileLoader.__init__(self, data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]
        self.is_battle = data["is_battle"]

        self.name = i18n_translator[data["name"]]
        self.pos = storyPosAuto(data["pos"])
        self.image = UrlModel()
        self.source = StoryInfoSource(data.get("source", {}))
        self.image.load(self.data["image"])

        self.desc = LangStringModelList('desc')
        if isinstance(data["desc"], str):
            self.desc.append(i18n_translator[data["desc"]])
        else:
            for i in data["desc"]:
                self.desc.append(i18n_translator[i])

        self.extra_register()

    def extra_register(self):
        self.part = StoryPartAutoData(self.data["data"], self)

        # 手动加载，防止bug
        self.part.load()

    def to_json(self):
        return StoryInfoAutoMixin.to_json(StoryInfo.to_json(self))

    def to_json_basic(self):
        return StoryInfoAutoMixin.to_json_basic(StoryInfo.to_json_basic(self))


class StoryInfoBondAuto(StoryInfoBond, StoryInfoAutoMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extra_register(self):
        self.part = StoryPartAutoData(self.data["data"], self)
        self.part.load()

    def to_json(self):
        return StoryInfoAutoMixin.to_json(StoryInfoBond.to_json(self))

    def to_json_basic(self):
        return StoryInfoAutoMixin.to_json_basic(StoryInfoBond.to_json_basic(self))

    def after_instantiate(self):
        self.extra_register()

        # 如果当前为回忆大厅剧情，则绑定学生的bond_track
        if self.data["data"]["special"]["flag"]:
            self.stu.bond_track = TrackInfo.get_instance(self.data["data"]["special"]["track"])
            self.stu.bond_rank = self.pos.favor_rank


def storyinfo_dispatcher(**kwargs):
    try:
        filetype_sub = kwargs["data"]["filetype_sub"]
    except KeyError:
        filetype_sub = 0

    if kwargs["data"]["filetype"] == FILE_STORY_BOND:
        if filetype_sub == 0:
            return StoryInfoBond(**kwargs)
        else:
            return StoryInfoBondAuto(**kwargs)
    else:
        if filetype_sub == 0:
            return StoryInfo(**kwargs)
        else:
            return StoryInfoAuto(**kwargs)
