from data_model.types.metatype.base_type import *
from data_model.types.metatype.complex import *
from data_model.actual_data._story.story_pos import *
from data_model.tool.to_json import IToJson
from data_model.loader import i18n_translator
from data_model.types.lang_string import LangStringModelList
from data_model.loader import FileLoader
from data_model.constant.file_type import FILE_STORY_MAIN, FILE_STORY_SIDE, FILE_STORY_SHORT, FILE_STORY_EVENT, \
    FILE_STORY_BOND, FILE_STORY_OTHER
from ._story.story_part import StoryInfoPartListManager
from ..tool.parent_data import IParentData


class StoryInfo(FileLoader, IToJson, IParentData):
    uuid = UUID('uuid')
    filetype = Integer('filetype')
    is_battle = Bool('is_battle')

    _story_type = {FILE_STORY_MAIN: "MAIN", FILE_STORY_SIDE: "SIDE", FILE_STORY_SHORT: "SHORT",
                   FILE_STORY_EVENT: "EVENT", FILE_STORY_OTHER: "OTHER"}
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]
        self.is_battle = data["is_battle"]

        self.name = i18n_translator[data["name"]]
        self.pos = storyPosAuto(data["pos"])
        self.part = StoryInfoPartListManager(data["part"])
        self.bgm_battle = self.part.get_bgm_special()

        # Special case: some stories still have content after the battle,
        # and in that case, there will be two description text.
        # The code here can handle either single string or a list with strings,
        # and it will normalize into a list with LangStringModel in both cases.
        self.desc = LangStringModelList('desc')
        if isinstance(data["desc"], str):
            self.desc.append(i18n_translator[data["desc"]])
        else:
            for i in data["desc"]: self.desc.append(i18n_translator[i])

        self.extra_register()

    def extra_register(self):
        # Register itself to every track in StoryInfoPartListManager
        for part in self.part.part:
            for track in part.track.track:
                track.register(self)
            for char in part.character.character:
                char.register(self)

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
            return self.export_parents_to_json(self.unpack_parents(self.parent_data, False)[0])

    def to_json(self):
        t = {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json()[-1],
            "desc": [i[-1] for i in self.desc.to_json()[-1]],
            "pos": self.pos.to_json()[-1],
            "image": self.data["image"],
            "instance_id": self.instance_id,

            "part": self.part.to_json_basic(),
            "is_battle": self.is_battle,

            "parent_data": self.parent_data_to_json()
        }
        if self.is_battle:
            t["bgm_battle"] = self.bgm_battle.to_json_basic()
        return t

    def to_json_basic(self):
        return self.to_json()

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class StoryInfoBond(StoryInfo):
    """Basically a modified class from StoryInfo"""

    def __init__(self, **kwargs):
        self.data = data = kwargs["data"]
        self.filetype = data["filetype"]
        self.uuid = data["uuid"]
        self.is_memory = data["is_memory"]

        self.name = i18n_translator[data["name"]]
        self.pos = storyPosAuto(data["pos"])

        # Special case: some stories still have content after the battle,
        # and in that case, there will be two description text.
        # The code here can handle either single string or a list with strings,
        # and it will normalize into a list with LangStringModel in both cases.
        self.desc = LangStringModelList('desc')
        if isinstance(data["desc"], str):
            self.desc.append(i18n_translator[data["desc"]])
        else:
            for i in data["desc"]: self.desc.append(i18n_translator[i])

    def after_instantiate(self):
        # To avoid that when creating a student's bond story,
        # it can't find itself since it's in the process of being created.
        self.part = StoryInfoPartListManager(self.data["part"])
        self.bgm_memory = self.part.get_bgm_special()

        self.extra_register()

    @staticmethod
    def _get_instance_id(data: dict):
        story_pos = data["pos"].values()
        story_pos = [str(i) for i in story_pos]
        return "_".join(["BOND", *story_pos])

    def to_json(self):
        t = {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json()[-1],
            "desc": [i[-1] for i in self.desc.to_json()[-1]],
            "pos": self.pos.to_json()[-1],
            "image": self.data["image"],
            "instance_id": self.instance_id,

            "part": self.part.to_json_basic(),
            "is_memory": self.is_memory,

            "parent_data": self.parent_data_to_json()
        }
        if self.is_memory:
            t["bgm_bond"] = self.bgm_memory.to_json_basic()
        return t

    def to_json_basic(self):
        return self.to_json()
