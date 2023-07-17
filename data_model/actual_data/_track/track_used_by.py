import data_model.constant.file_type as FILE_TYPE
from collections import OrderedDict
from data_model.loader import i18n_translator
from data_model.types.lang_string import LangStringModelList
from data_model.tool.to_json import ToJsonMixin


__all__ = ["TrackUsedBy_story", "TrackUsedBy_battle", "TrackUsedBy_other"]


# ---------------------------------------------------------
# TrackUsedBy




class TrackUsedBy_ToJsonMixin(ToJsonMixin):
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


class TrackUsedBy_other(TrackUsedBy_ToJsonMixin):
    __slots__ = ("ui", "other", "video", "key_name", "data")
    _components = ("ui", "video")  # "other" is not possible through parent method to read

    def __init__(self):
        self.key_name = "other"
        self.ui = OrderedDictWithCounter()
        self.other = LangStringModelList('other')
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


class TrackUsedBy_battle(TrackUsedBy_ToJsonMixin):
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


class TrackUsedBy_story(TrackUsedBy_ToJsonMixin):
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
