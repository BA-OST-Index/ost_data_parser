from data_model.loader import i18n_translator
from data_model.tool.to_json import IToJson
from data_model.actual_data.track import TrackListManager
from data_model.actual_data.background import BackgroundListManager
from data_model.actual_data.character import CharacterListManager


class StoryInfoPart(IToJson):
    _components = ["name", "desc", "character", "track", "background"]

    def __init__(self, data: dict):
        self.data = data
        self.name = i18n_translator[data["name"]]
        self.desc = i18n_translator[data["desc"]]
        self.character = CharacterListManager()
        self.track = TrackListManager()
        self.background = BackgroundListManager()

        if "is_battle" in data.keys():
            # For normal case
            self.is_battle = data["is_battle"]
        elif "is_memory" in data.keys():
            # For bond case
            self.is_memory = data["is_memory"]

        self.track.load(self.data["track"])
        self.character.load(self.data["character"])
        self.background.load(self.data["background"])

        self.extra_register()

    def extra_register(self):
        # For CharacterInfo
        # register every TrackInfo to CharacterInfo
        for char in self.character.character:
            for track in self.track.track:
                char.register(track)

        # For BackgroundInfo
        # if there's only one background, then:
        #   - register this BackgroundInfo to every TrackInfo
        #   - register every TrackInfo to this BackgroundInfo
        if len(self.background.background) == 1:
            background = self.background.background[0]
            for track in self.track.track:
                track.register(background)
                background.register(track)

        # For TrackInfo
        # if there's only one track, then:
        #   - register this TrackInfo to every BackgroundInfo
        if len(self.track.track) == 1:
            track = self.track.track[0]
            for background in self.background.background:
                background.register(track)

    def to_json_basic(self):
        d = {"name": self.name.to_json_basic(),
             "desc": self.desc.to_json_basic()}
        return d

    def to_json(self):
        d = {"name": self.name.to_json(),
             "desc": self.desc.to_json(),
             "character": self.character.to_json_basic(),
             "track": self.track.to_json_basic(),
             "background": self.background.to_json_basic()}

        if "is_battle" in self.data.keys():
            d["is_battle"] = self.is_battle
        elif "is_memory" in self.data.keys():
            d["is_memory"] = self.is_memory

        return d


class StoryInfoPartListManager(IToJson):
    def __init__(self, data: list):
        self.part = []
        self.bgm_special = []

        for i in data:
            p = StoryInfoPart(i)
            try:
                # Normal case
                if p.is_battle and p.track.track[0] not in self.bgm_special:
                    self.bgm_special.append(p.track.track[0])
            except Exception:
                try:
                    # Bond case
                    if p.is_memory and p.track.track[0] not in self.bgm_special:
                        self.bgm_special.append(p.track.track[0])
                except Exception:
                    raise

            self.part.append(p)

    def to_json(self):
        return [part.to_json() for part in self.part]

    def to_json_basic(self):
        return [part.to_json_basic() for part in self.part]

    def to_json_basic_tracks(self):
        return [track.to_json_basic() for track in self.bgm_special]
