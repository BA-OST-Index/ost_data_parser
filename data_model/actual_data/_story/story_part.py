from data_model.loader import i18n_translator
from data_model.tool.to_json import IToJson
from data_model.actual_data.track import TrackListManager
from data_model.actual_data.background import BackgroundListManager
from data_model.actual_data.character import CharacterListManager
from collections import UserList
from .story_source_part import StoryInfoPartVideo


class StoryInfoPartSegment(IToJson):
    def __init__(self, data: dict):
        self.data = data

        self.desc = i18n_translator.query(self.data["desc"])
        self.character = CharacterListManager()
        self.track = TrackListManager()
        self.background = BackgroundListManager()

        self.track.load(self.data["track"])
        self.character.load(self.data["character"])
        self.background.load(self.data["background"])

        # self.extra_register()

    def extra_register(self):
        for char in self.character.character:
            for track in self.track.track:
                char.register(track, False)
                track.register(char, False)

        for background in self.background.background:
            for track in self.track.track:
                track.register(background, False)
                background.register(track, False)
            for character in self.character.character:
                character.register(background, False)
                background.register(character, False)

    def to_json(self):
        return {
            "desc": self.desc.to_json(),
            "track": self.track.to_json_basic(),
            "character": self.character.to_json_basic(),
            "background": self.background.to_json_basic()
        }

    def to_json_basic(self):
        return self.to_json()


class StoryInfoPartSegmentListManager(UserList, IToJson):
    def load(self, data: list):
        for i in data:
            self.append(StoryInfoPartSegment(i))

    def to_json(self):
        return [i.to_json_basic() for i in self]

    def to_json_basic(self):
        return self.to_json()


class StoryInfoPart(IToJson):
    _components = ["name", "desc", "character", "track", "background"]

    def __init__(self, data: dict, story_obj):
        self.data = data
        self.name = i18n_translator[data["name"]]
        self.segments = StoryInfoPartSegmentListManager()

        # 旧数据转为新数据
        if "desc" in data.keys():
            self.segments.load([{"desc": data["desc"], "track": data["track"],
                                 "character": data["character"], "background": data["background"]}])
        # 新数据
        else:
            self.segments.load(data["data"])

        # TODO: StoryInfoPartSource
        # self.video = StoryInfoPartVideo(data.get("video", {}), story_obj)

        self._story_obj = story_obj

        # 特别地，当为战斗时，self.segments必然只有一个segment
        if "is_battle" in data.keys():
            # For normal case
            self.is_battle = data["is_battle"]
            self.battle_leader_pos = self.segments[0].character.leader_pos
        elif "is_memory" in data.keys():
            # For bond case
            self.is_memory = data["is_memory"]
            self.is_momotalk = data["is_momotalk"]

    def to_json_basic(self):
        d = {"name": self.name.to_json_basic(),
             "data": [{"desc": i.desc.to_json_basic()} for i in self.segments]}
        return d

    def to_json(self):
        d = {"name": self.name.to_json(),
             "data": self.segments.to_json()}

        if "is_battle" in self.data.keys():
            d["is_battle"] = self.is_battle
            d["battle_leader_pos"] = self.battle_leader_pos
        elif "is_memory" in self.data.keys():
            d["is_memory"] = self.is_memory
            d["is_momotalk"] = self.is_momotalk

        return d


class StoryInfoPartListManager(IToJson):
    def __init__(self, data: list, story_obj):
        self.part = []
        self.bgm_special = []
        self.story_obj = story_obj

        for i in data:
            p = StoryInfoPart(i, story_obj)
            try:
                # Normal case
                if p.is_battle and p.segments[0].track.track[0] not in self.bgm_special:
                    self.bgm_special.append(p.segments[0].track.track[0])
            except Exception:
                try:
                    # Bond case
                    if p.is_memory and p.segments[0].track.track[0] not in self.bgm_special:
                        self.bgm_special.append(p.segments[0].track.track[0])
                except Exception:
                    raise

            self.part.append(p)

    def to_json(self):
        return [part.to_json() for part in self.part]

    def to_json_basic(self):
        return [part.to_json_basic() for part in self.part]

    def to_json_basic_tracks(self):
        return [track.to_json_basic() for track in self.bgm_special]
