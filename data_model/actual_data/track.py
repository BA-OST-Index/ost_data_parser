from itertools import chain
from data_model.types.url import *
from data_model.types.metatype.base_type import *
from data_model.types.metatype.base_model import *
from data_model.types.metatype.complex import *
from data_model.types.lang_string import *
from data_model.loader import i18n_translator, FileLoader
from data_model.loader.manager_constant import constant_manager
from data_model.actual_data.used_by import BaseUsedBy, UsedByRegisterMixin, OrderedDictWithCounter, UsedByToJsonMixin
from data_model.actual_data._track.track_version import *
from data_model.constant.file_type import FILETYPES_STORY, FILETYPES_BATTLE, FILETYPES_BACKGROUND, \
    FILE_VIDEO_INFO, FILETYPES_TRACK, FILE_STORY_EVENT, FILE_BATTLE_EVENT, FILE_UI_EVENT, FILE_UI_CHILD, \
    FILETYPES_CHARACTER, FILE_STUDENT_INFO
from data_model.actual_data.tag import TagListManager
from data_model.tool.tool import seconds_to_minutes
from data_model.tool.interpage import InterpageMixin
from ..tool.tool import counter_dict_sorter

__all__ = ["TrackInfo", "TrackListManager"]


class TrackUsedBy(BaseUsedBy, UsedByToJsonMixin):
    SUPPORTED_FILETYPE = [*FILETYPES_STORY, *FILETYPES_BATTLE, *FILETYPES_BACKGROUND, FILE_VIDEO_INFO,
                          FILE_STORY_EVENT, FILE_BATTLE_EVENT, FILE_UI_EVENT, FILE_UI_CHILD, *FILETYPES_CHARACTER]
    _components = ["data_background", "data_story", "data_battle", "data_ui", "data_video", "data_character"]

    def __init__(self):
        self.data_background = OrderedDictWithCounter()
        self.data_story = OrderedDictWithCounter()
        self.data_battle = OrderedDictWithCounter()
        self.data_ui = OrderedDictWithCounter()
        self.data_video = OrderedDictWithCounter()
        self.data_character = OrderedDictWithCounter()

    def register(self, file_loader: FileLoader, count_increase=True):
        try: filetype = file_loader.filetype
        except AttributeError:
            # currently, only students don't have a filetype
            filetype = FILE_STUDENT_INFO

        instance_id = file_loader.instance_id

        if filetype in self.SUPPORTED_FILETYPE:
            if filetype in [*FILETYPES_STORY, FILE_STORY_EVENT]:
                self.data_story[instance_id] = file_loader
                if not count_increase:
                    self.data_story.counter_adjust(instance_id, -1)
            elif filetype in [*FILETYPES_BATTLE, FILE_BATTLE_EVENT]:
                self.data_battle[instance_id] = file_loader
                if not count_increase:
                    self.data_battle.counter_adjust(instance_id, -1)
            elif filetype in [FILE_UI_EVENT, FILE_UI_CHILD]:
                self.data_ui[instance_id] = file_loader
                if not count_increase:
                    self.data_ui.counter_adjust(instance_id, -1)
            elif filetype in FILETYPES_BACKGROUND:
                self.data_background[instance_id] = file_loader
                if not count_increase:
                    self.data_background.counter_adjust(instance_id, -1)
            elif filetype == FILE_VIDEO_INFO:
                self.data_video[instance_id] = file_loader
                if not count_increase:
                    self.data_video.counter_adjust(instance_id, -1)
            elif filetype in FILETYPES_CHARACTER:
                self.data_character[instance_id] = file_loader
                if not count_increase:
                    self.data_character.counter_adjust(instance_id, -1)
        else:
            raise ValueError

    def get_special_case_info(self):
        is_story = True if len(self.data_story) != 0 else False
        is_battle = True if len(self.data_battle) != 0 else False

        is_bond_memory = False
        for i in self.data_story.values():
            try:
                if i.is_bond:
                    is_bond_memory = True
                    break
            except Exception:
                pass

        is_event = False
        for i in chain(self.data_story.keys(), self.data_battle.keys()):
            if "EVENT" in i:
                is_event = True
                break

        return {"is_story": is_story, "is_battle": is_battle,
                "is_bond_memory": is_bond_memory, "is_event": is_event}

    def to_json(self, no_used_by: bool = True):
        d = super().to_json()
        d["data_character"] = counter_dict_sorter(self.data_character.get_counter_with_data_sorted_by_counter(),
                                                  [["name", "path_name"], ["name", "en"]])
        return d


class ComposerUsedBy(BaseUsedBy, UsedByToJsonMixin):
    SUPPORTED_FILETYPE = [*FILETYPES_TRACK]
    _components = ["data_track"]

    def __init__(self):
        self.data_track = OrderedDictWithCounter()

    def register(self, file_loader: FileLoader, count_increase=True):
        filetype = file_loader.filetype
        instance_id = file_loader.instance_id
        if filetype in self.SUPPORTED_FILETYPE:
            if filetype in FILETYPES_TRACK:
                self.data_track[instance_id] = file_loader
                if not count_increase:
                    self.data_track.counter_adjust(instance_id, -1)
        else:
            raise ValueError


class TrackSpecialCase:
    _all = ["is_ost", "is_bond_memory", "is_story", "is_battle", "is_event"]
    _counter = {key: [] for key in _all}

    def __init__(self, key_name):
        pass

    def load(self, data: dict, track_info):
        self.data = data
        for i, y in self.data.items():
            setattr(self, i, y)
            if y:
                self._counter[i].append(track_info)

    def to_json(self):
        return self.data

    def to_json_basic(self):
        return self.to_json()

    @classmethod
    def get_counter(cls):
        return cls._counter

    @classmethod
    def export_counter_json(cls):
        t = dict((key, list(track.to_json() for track in value))
                 for key, value in cls._counter.items())
        return t

    @classmethod
    def export_counter_json_basic(cls):
        t = dict((key, list(track.to_json_basic() for track in value))
                 for key, value in cls._counter.items())
        return t


class TrackName(BaseDataModel):
    def __init__(self, key_name):
        super().__init__(key_name)
        self.known_as = LangStringModelList('known_as')

    def load(self, data):
        super().load(data)
        self.realname = i18n_translator[data["realname"]]
        for i in data["known_as"]:
            self.known_as.append(i18n_translator[i])

    def to_json(self):
        known_as = self.known_as.to_json()
        t = {"realname": self.realname.to_json(), "known_as": [value for value in known_as]}
        return t

    def to_json_basic(self):
        return self.to_json()


class TrackVersionListManager(BaseDataModelListManager):
    def __init__(self, key_name):
        super().__init__(key_name)
        self.version = TrackVersionList(key_name)

    def load(self, data):
        super().load(data)
        for i in data:
            t = TrackVersion()
            t.load(i)
            self.version.append(t)

    def to_json(self):
        return self.version.to_json()

    def to_json_basic(self):
        return self.to_json()


class TrackTags(BaseDataModel):
    def __init__(self, key_name, track):
        super().__init__(key_name)
        self.track = track
        self.tags = TagListManager()

    def load(self, data):
        super().load(data)
        self.tags.load(data)
        for i in self.tags.tag:
            i.register(self.track)

    def to_json(self):
        return self.tags.to_json()

    def to_json_basic(self):
        return self.to_json()


class Contact(BaseDataModel):
    platform = Integer("platform")
    _components = ["platform", "url"]

    def __init__(self):
        super().__init__("contact")
        self.url = UrlModel()

    def load(self, data: dict):
        super().load(data)
        self.platform = data["platform"]
        self.url.load(data["url"])

    def to_json(self):
        t = {
            "platform": constant_manager.query("platform", self.platform).to_json(),
            "url": self.url.to_json()
        }
        return t

    def to_json_basic(self):
        return self.to_json()


class Composer(BaseDataModel, UsedByRegisterMixin):
    """
    Defines a `composer` dict.

    Note: This class implements irregular Singleton behaviour, in which when
        you're loading the data, it might return an existing instance if
        there's a match in either the `nickname` or `composer_id`.
    """
    realname = String("realname")
    nickname = String("nickname")
    _components = ["composer_id", "realname", "nickname", "contact"]
    _instance = {}

    def __init__(self, key_name="composer"):
        super().__init__(key_name)
        self.contact = Contact()
        self.used_by = ComposerUsedBy()

    def load(self, value: dict):
        self.composer_id = str(value.get("composer_id", ""))
        if self.composer_id in self._instance.keys():
            return self._instance[self.composer_id]

        # If none is found, then it's the first time to create
        # Check if the composer is auto-indexed
        if value.get("composer_id", "") != "":
            value = constant_manager.query("composer", value["composer_id"])
        super().load(value)

        self.realname = value["realname"]
        self.nickname = value["nickname"]
        self.contact.load(value["contact"])

        self._instance[self.composer_id] = self

        return self

    def to_json(self):
        return {"composer_id": self.composer_id,
                "realname": self.realname,
                "nickname": self.nickname,
                "contact": self.contact.to_json_basic(),
                "used_by": self.used_by.to_json_basic()}

    def to_json_basic(self):
        return {"composer_id": self.composer_id,
                "nickname": self.nickname,
                "contact": self.contact.to_json_basic()}


# -------------------------------------------------------

class TrackInfo(FileLoader, UsedByRegisterMixin, InterpageMixin):
    """大类，用于代表一个完整的歌曲JSON文件"""
    no = Integer("no")
    track_type = Integer("track_type")
    release_date = Timestamp("release_date")
    duration = Integer("duration")
    filetype = Integer("filetype")
    uuid = UUID("uuid")
    _instance = {}
    _filetype_id_map = {"0": "OST", "1": "short",
                        "2": "animation", "3": "other"}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]

        # Regular information
        self.no = data["no"]
        self.track_type = data["track_type"]
        self.duration = data["duration"]
        self.release_date = data["release_date"]
        self.filetype = data["filetype"]
        self.uuid = data["uuid"]

        # Song Description, using LangStringModel
        self.desc = i18n_translator[data["desc"]]

        # Special Case Usage
        # DO NOT load the data until all the relations data being imported!
        self.special_case = TrackSpecialCase('special_case')

        # Other stuff
        self.composer = Composer().load(data["composer"])
        self.composer.register(self)
        self.tags = TrackTags('tags', self)
        self.version = TrackVersionListManager('version')
        self.name = TrackName('name')
        self.used_by = TrackUsedBy()
        self.reference = UrlModelListManager('reference')
        self.image = UrlModel()

        # Load Data
        self.name.load(data["name"])
        self.reference.load(data["reference"])
        self.version.load(data["version"])
        self.image.load(data["image"])
        self.tags.load(data["tags"]["overall"])

    @staticmethod
    def _get_instance_id(data: dict):
        no = str(data["no"])
        track_type = TrackInfo._filetype_id_map[str(data["track_type"])]
        return "_".join([track_type, no])

    def load_special_case(self):
        t = self.used_by.get_special_case_info()
        t["is_ost"] = True if self.track_type == 0 else False
        self.special_case.load(t, self)

    def to_json(self):
        self.load_special_case()
        t = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "namespace": self.namespace,
            "instance_id": self.instance_id,

            "release_date": int(self.release_date.timestamp()),
            "release_date_format": self.release_date.strftime("%Y-%m-%d %H:%M:%S"),
            "no": self.no,
            "track_type": self.track_type,
            "duration": self.duration,
            "duration_splited": seconds_to_minutes(self.duration),

            "composer": self.composer.to_json_basic(),
            "tags": self.tags.to_json_basic(),
            "version": self.version.to_json_basic(),
            "special_case": self.special_case.to_json_basic(),
            "reference": self.reference.to_json_basic(),
            "used_by": self.used_by.to_json_basic(),
            "image": self.image.to_json_basic(),
            "interpage": self.get_interpage_data()
        }
        return t

    def to_json_basic(self):
        self.load_special_case()
        t = {
            "uuid": self.uuid,
            "no": self.no,
            "filetype": self.filetype,
            "namespace": self.namespace,
            "track_type": self.track_type,
            "instance_id": self.instance_id,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "composer": self.composer.to_json_basic(),
            "image": self.image.to_json_basic(),
            "interpage": self.get_interpage_data()
        }
        return t

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)

    def _get_instance_offset(self, offset: int):
        t = self.instance_id.split("_")
        no = int(t[1]) + offset
        try:
            return self._instance["_".join([t[0], str(no)])]
        except KeyError:
            return None


class TrackListManager(BaseDataModelListManager):
    def __init__(self, key_name="track"):
        super().__init__(key_name)
        self.track = []

    def load(self, data: list):
        super().load(data)
        for i in data:
            self.track.append(TrackInfo.get_instance(instance_id=i))

    def to_json(self):
        t = [i.to_json_basic() for i in self.track]
        return t

    def to_json_basic(self):
        return self.to_json()
