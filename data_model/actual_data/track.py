from data_model.types.url import *
from data_model.types.metatype.basic import *
from data_model.types.metatype.complex import *
from data_model.types.lang_string import *
from data_model.loader.i18n import i18n_translator
from data_model.loader.constant import constant_manager
from data_model.actual_data._track.track_used_by import *
from data_model.actual_data._track.track_version import *

__all__ = ["TrackInfo", "TrackListManager"]


class TrackUsedBy(BaseDataModel):
    __slots__ = ("story", "battle", "other", "key_name", "data")
    _components = ("story", "battle", "other")

    def __init__(self, key_name="used_by"):
        super().__init__(key_name)
        self.story = TrackUsedBy_story()
        self.battle = TrackUsedBy_battle()
        self.other = TrackUsedBy_other()

    def load(self, data):
        super().load(data)
        self.other.load_other(data["other"]["other"])

    def to_json(self):
        t = dict()
        for i in self._components:
            data = getattr(self, i).to_json()
            t[i] = data[-1]
        return t

    def to_json_basic(self):
        t = dict()
        for i in self._components:
            data = getattr(self, i).to_json_basic()
            t[i] = data
        return t


class TrackSpecialCase(BaseDataModel):
    _all = ["is_ost", "is_bond_memory", "is_story", "is_battle", "is_event"]
    _counter = dict((key, []) for key in _all)

    def __init__(self, key_name):
        super().__init__(key_name)

    def load(self, data: dict, track_info):
        super().load(data)
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
        self.known_as = MultipleLangStringModelList('known_as')

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
    def __init__(self, key_name):
        super().__init__(key_name)
        self.tags = MultipleLangStringModelList(key_name)

    def load(self, data):
        super().load(data)
        for i in data:
            self.tags.append(constant_manager.query("tag", str(i)))

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


class Composer(BaseDataModel):
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

    def load(self, value: dict):
        self.composer_id = str(value.get("composer_id", ""))
        nickname = str(value.get("nickname", ""))

        # Implementing Singleton
        if nickname in self._instance.keys():
            return self._instance["nickname"]
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

        return self

    def to_json(self):
        return {"composer_id": self.composer_id,
                "realname": self.realname,
                "nickname": self.nickname,
                "contact": self.contact.to_json()}

    def to_json_basic(self):
        return {"composer_id": self.composer_id,
                "nickname": self.nickname,
                "contact": self.contact.to_json_basic()}


# -------------------------------------------------------

class TrackInfo:
    """大类，用于代表一个完整的歌曲JSON文件"""
    no = Integer("no")
    track_type = Integer("track_type")
    release_date = Timestamp("release_date")
    duration = Integer("duration")
    file_type = Integer("file_type")
    uuid = UUID("uuid")
    _instance = {}
    _filetype_id_map = {"1": "OST", "2": "short",
                        "3": "animation", "4": "other"}

    def __new__(cls, *args, **kwargs):
        try: data = args[0]
        except Exception: data = kwargs["data"]

        instance_id = "_".join([cls._filetype_id_map[str(data["file_type"])],
                                str(data["no"])])
        if instance_id in cls._instance.keys():
            return cls._instance[instance_id]

        new = super().__new__(cls)
        cls._instance[instance_id] = new
        return new

    def __init__(self, data: dict):
        self.data = data

        # Regular information
        self.no = data["no"]
        self.track_type = data["track_type"]
        self.duration = data["duration"]
        self.release_date = data["release_date"]
        self.file_type = data["file_type"]
        self.uuid = data["uuid"]

        # Song Description, using LangStringModel
        self.desc = i18n_translator[data["desc"]]

        # Special Case Usage
        # DO NOT load the data until all the relations data being imported!
        self.special_case = TrackSpecialCase('special_case')
        # TODO: for temporary development needs. This should be removed and generated
        #   from known relations (e.g. by accessing `TrackUsedBy`).
        self.special_case.load(data["special_case"], self)

        # Other stuff
        self.composer = Composer().load(data["composer"])
        self.tags = TrackTags('tags')
        self.version = TrackVersionListManager('version')
        self.name = TrackName('name')
        self.used_by = TrackUsedBy()
        self.reference = UrlModelListManager('reference')

        # Load Data
        self.name.load(data["name"])
        self.used_by.load(data["used_by"])

    def to_json(self):
        t = {
            "uuid": self.uuid,

            "name": self.name.to_json(),
            "desc": self.desc.to_json(),

            "release_date": int(self.release_date.timestamp()),
            "no": self.no,
            "track_type": self.track_type,
            "duration": self.duration,
            "file_type": self.file_type,

            "composer": self.composer.to_json(),
            "used_by": self.used_by.to_json(),
            "tags": self.tags.to_json(),
            "version": self.version.to_json(),
            "special_case": self.special_case.to_json(),
            "reference": self.reference.to_json()
        }
        return t

    def to_json_basic(self):
        t = {
            "uuid": self.uuid,
            "no": self.no,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "composer": self.composer.to_json_basic()
        }
        return t

    @classmethod
    def get_instance(cls, instance_id):
        return cls._instance[instance_id]


class TrackListManager(BaseDataModelListManager):
    def __init__(self, key_name="track"):
        super().__init__(key_name)
        self.track = []

    def load(self, data: list):
        for i in data:
            self.track.append(TrackInfo.get_instance(i))

    def to_json(self):
        t = [i.to_json() for i in self.track]
        return t

    def to_json_basic(self):
        t = [i.to_json_basic() for i in self.track]
        return t
