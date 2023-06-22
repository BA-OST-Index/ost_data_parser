import json
import data_model._constant.file_type as FILE_TYPE
from collections import OrderedDict
from data_model.types.url import *
from data_model.types.metatype.basic import *
from data_model.types.metatype.complex import *
from data_model.types.lang_string import *
from data_model.loader.i18n import i18n_translator
from data_model.loader.constant import constant_manager

__all__ = ["TrackInfo"]


# ---------------------------------------------------------
# TrackUsedBy

class OrderedDictWithCounter:
    def __init__(self):
        self.ordered_dict = OrderedDict()
        self.counter = dict()

    def add(self, unique_id, data):
        if unique_id in self.ordered_dict.keys():
            self.counter[unique_id] += 1
        else:
            self.ordered_dict[unique_id] = data
            self.counter[unique_id] = 1

    def get_counter_with_data(self):
        return OrderedDict((key, [value, self.counter[key]])
                           for key, value in self.ordered_dict.items())


class _TrackUsedBy_ToJsonMixin(ToJsonMixin):
    def to_json(self):
        t = dict((key, []) for key in self._components)
        for key, value in t.items():
            data = getattr(self, key).get_counter_with_data()
            t[key] = OrderedDict((key, [value[0].to_json(), value[1]])
                                 for key, value in data.items())
        return self.key_name, t

    def to_json_basic(self):
        t = dict((key, []) for key in self._components)
        for key, value in t.items():
            data = getattr(self, key).get_counter_with_data()
            t[key] = OrderedDict((key, [value[0].to_json_basic(), value[1]])
                                 for key, value in data.items())
        return self.key_name, t


class _TrackUsedBy_other(_TrackUsedBy_ToJsonMixin):
    __slots__ = ("ui", "other", "video", "key_name", "data")
    _components = ("ui", "video")  # "other" is not possible through parent method to read

    def __init__(self):
        self.key_name = "other"
        self.ui = OrderedDictWithCounter()
        self.other = MultipleLangStringModelList('other')
        self.video = OrderedDictWithCounter()

    def load_other(self, data: list):
        for i in data:
            self.other.append(i18n_translator[i])

    def add(self, unique_id, data):
        if data.file_type == FILE_TYPE.FILE_UI_PARENT:
            raise ValueError("Only supports UI_CHILD object.")
        elif data.file_type == FILE_TYPE.FILE_UI_CHILD:
            self.ui.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_VIDEO_INFO:
            self.video.add(unique_id, data)
        else:
            raise TypeError("The object %r (id: %r) is not supported!" % (data, unique_id))

    def to_json(self):
        """Overriding the parent's method in order to access `self.other`"""
        key, data = super().to_json()
        data["other"] = [value[-1] for value in self.other.to_json()[-1]]
        return key, data

    def to_json_basic(self):
        key, data = super().to_json_basic()
        data["other"] = [value[-1] for value in self.other.to_json_basic()[-1]]
        return key, data


class _TrackUsedBy_battle(_TrackUsedBy_ToJsonMixin):
    __slots__ = ("main", "event", "arena", "total_assault", "bounty_hunt", "school_exchange", "special_commission",
                 "data", "key_name")
    _components = ("main", "event", "arena", "total_assault", "bounty_hunt", "school_exchange", "special_commission")

    def __init__(self):
        self.key_name = "story"
        self.main = OrderedDictWithCounter()
        self.event = OrderedDictWithCounter()
        self.arena = OrderedDictWithCounter()
        self.total_assault = OrderedDictWithCounter()
        self.bounty_hunt = OrderedDictWithCounter()
        self.school_exchange = OrderedDictWithCounter()
        self.special_commission = OrderedDictWithCounter()

    def add(self, unique_id, data):
        if data.file_type == FILE_TYPE.FILE_BATTLE_MAIN:
            self.main.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_BATTLE_EVENT:
            self.event.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_BATTLE_ARENA:
            self.arena.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_BATTLE_TOTAL_ASSAULT:
            self.total_assault.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_BATTLE_BOUNTY_HUNT:
            self.total_assault.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_BATTLE_SCHOOL_EXCHANGE:
            self.school_exchange.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_BATTLE_SPECIAL_COMMISSION:
            self.school_exchange.add(unique_id, data)
        else:
            raise TypeError("The object %r (id: %r) is not a battle!" % (data, unique_id))


class _TrackUsedBy_story(_TrackUsedBy_ToJsonMixin):
    __slots__ = ("main", "side", "short", "bond", "event", "other", "key_name", "data")
    _components = ("main", "side", "short", "bond", "event", "other")

    def __init__(self):
        self.key_name = "story"
        self.main = OrderedDictWithCounter()
        self.side = OrderedDictWithCounter()
        self.short = OrderedDictWithCounter()
        self.bond = OrderedDictWithCounter()
        self.event = OrderedDictWithCounter()
        self.other = OrderedDictWithCounter()

    def add(self, unique_id, data):
        if data.file_type == FILE_TYPE.FILE_STORY_MAIN:
            self.main.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_STORY_SIDE:
            self.side.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_STORY_SHORT:
            self.short.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_STORY_EVENT:
            self.event.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_STORY_OTHER:
            self.other.add(unique_id, data)
        elif data.file_type == FILE_TYPE.FILE_STORY_BOND:
            self.bond.add(unique_id, data)
        else:
            raise TypeError("The object %r (id: %r) is not a story!" % (data, unique_id))


class TrackUsedBy(BasicModel):
    __slots__ = ("story", "battle", "other", "key_name", "data")
    _components = ("story", "battle", "other")

    def __init__(self, key_name="used_by"):
        super().__init__(key_name)
        self.story = _TrackUsedBy_story()
        self.battle = _TrackUsedBy_battle()
        self.other = _TrackUsedBy_other()

    def load(self, data):
        super().load(data)
        self.other.load_other(data["other"]["other"])

    def to_json(self):
        t = dict()
        for i in self._components:
            data = getattr(self, i).to_json()
            t[i] = data[-1]
        return self.key_name, t

    def to_json_basic(self):
        t = dict()
        for i in self._components:
            data = getattr(self, i).to_json_basic()
            t[i] = data
        return self.key_name, t


# ---------------------------------------------------------
# TrackSpecialCase

class TrackSpecialCase(BasicModel):
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
        return self.key_name, self.data

    def to_json_basic(self):
        return self.to_json()[-1]

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


# ---------------------------------------------------------
# TrackVersion & TrackVersionList

class TrackVersion(BasicModel):
    is_main = Bool('is_main')
    _components = ["url", "desc", "is_main"]

    def __init__(self):
        super().__init__(None)
        self.url = MultipleUrlModelList('url')
        self.desc = LangStringModel()

    def load(self, data):
        super().load(data)
        self.is_main = data["is_main"]
        self.desc.load(constant_manager.query("ost", data["desc"]))
        for i in data["url"]:
            m = UrlModel()
            m.load(i)
            self.url.append(m)

    def to_json(self):
        return None, dict((key, getattr(self, key))
                          for key in self._components)

    def to_json_basic(self):
        return self.to_json()[-1]


class TrackVersionList(MultipleBasicModelList):
    def __init__(self, key_name):
        super().__init__(key_name, TrackVersion)


# ---------------------------------------------------------

class TrackName(BasicModel):
    def __init__(self, key_name):
        super().__init__(key_name)
        self.known_as = MultipleLangStringModelList('known_as')

    def load(self, data):
        super().load(data)
        self.realname = i18n_translator[data["realname"]]
        for i in data["known_as"]:
            self.known_as.append(i18n_translator[i])

    def to_json(self):
        known_as = self.known_as.to_json()[-1]
        t = {"realname": self.realname.to_json()[-1], "known_as": [value[-1] for value in known_as]}
        return self.key_name, t

    def to_json_basic(self):
        return self.to_json()[-1]


class TrackVersionListManager(MultipleBasicModelListManager):
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
        return self.to_json()[-1]


class TrackTags(BasicModel):
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
        return self.to_json()[-1]


class Contact(BasicModel):
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
            "platform": constant_manager.query("platform", self.platform).to_json()[-1],
            "url": self.url.to_json()[-1]
        }
        return self.key_name, t

    def to_json_basic(self):
        return self.to_json()[1]


class Composer(BasicModel):
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
        return self.key_name, {"composer_id": self.composer_id,
                               "realname": self.realname,
                               "nickname": self.nickname,
                               "contact": self.contact.to_json()[-1]}

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
        self.reference = MultipleUrlModelListManager('reference')

        # Load Data
        self.name.load(data["name"])
        self.used_by.load(data["used_by"])

    def to_json(self):
        t = {
            "uuid": self.uuid,

            "name": self.name.to_json()[1],
            "desc": self.desc.to_json()[1],

            "release_date": int(self.release_date.timestamp()),
            "no": self.no,
            "track_type": self.track_type,
            "duration": self.duration,
            "file_type": self.file_type,

            "composer": self.composer.to_json()[1],
            "used_by": self.used_by.to_json()[1],
            "tags": self.tags.to_json()[1],
            "version": self.version.to_json()[1],
            "special_case": self.special_case.to_json()[1],
            "reference": self.reference.to_json()[1]
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
