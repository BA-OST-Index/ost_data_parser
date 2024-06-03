import logging
from collections import OrderedDict

from data_model.actual_data.track import TrackInfo
from data_model.actual_data.character import CharacterInfo
from data_model.actual_data.background import BackgroundInfo
from data_model.tool.to_json import IToJson
from data_model.tool.tool import KeyToMultiValueDict


class StoryPartAutoDataAll(IToJson):
    def __init__(self, data, story):
        self.data = data
        self.story = story

        self.background = OrderedDict()
        self.character = OrderedDict()
        self.track = OrderedDict()

    def load(self):
        # bg
        for i in self.data["background"]:
            try:
                temp = BackgroundInfo.get_instance(i)
                temp.register(self.story)
                self.background[i] = temp
            except KeyError:
                logging.warning("No bg info about: " + repr(i))
        # track
        for i in self.data["track"]:
            temp = TrackInfo.get_instance(i)
            temp.register(self.story)
            self.track[i] = temp
        # character
        for i in self.data["character"]:
            try:
                temp = CharacterInfo.get_instance(i)
                temp.register(self.story)
                self.character[i] = temp
            except KeyError:
                logging.warning("No character info about: " + repr(i))

    def to_json(self):
        return {
            "background": {key: value.to_json_basic() for (key, value) in self.background.items()},
            "character": {key: value.to_json_basic() for (key, value) in self.character.items()},
            "track": {key: value.to_json_basic() for (key, value) in self.track.items()}
        }

    def to_json_basic(self):
        return self.to_json()


class StoryPartAutoData(IToJson):
    def __init__(self, data, story):
        self.data = data
        self.story = story

        self.data_all = StoryPartAutoDataAll(data["all"], story)
        self._bg_to_track = KeyToMultiValueDict()
        self._char_to_track = KeyToMultiValueDict()
        self._bg_to_char = KeyToMultiValueDict()

        self._track_to_bg = KeyToMultiValueDict()
        self._char_to_bg = KeyToMultiValueDict()

        self.data_special = {
            "flag": self.data["special"]["flag"],
            "track": None if self.data["special"]["track"] == "OST_0" else TrackInfo.get_instance(
                self.data["special"]["track"]),
            "char": [] if "char" not in self.data["special"].keys() else self.data["special"]["char"]
        }

    def load(self):
        self.data_all.load()

        # pre-process
        try:
            del self.data["track_to_bg"]["OST_0"]
        except KeyError:
            # it's okay if it doesn't exist
            pass

        # track to bg
        for (track_id, bgs) in self.data["track_to_bg"].items():
            if track_id == "OST_0":
                continue
            track = self.data_all.track[track_id]
            for bg_id in bgs:
                if bg_id in ["BG_Red.jpg", "BG_Black.jpg", "BG_White.jpg"]:
                    continue

                try:
                    bg = self.data_all.background[bg_id]
                except KeyError:
                    continue

                track.register(bg)
                bg.register(track)

                self._bg_to_track[bg_id] = track_id
                self._track_to_bg[track_id] = bg.uuid

        # track to char
        for (track_id, chars) in self.data["track_to_char"].items():
            if track_id == "OST_0":
                continue

            track = self.data_all.track[track_id]
            for char_id in chars:
                try:
                    char = self.data_all.character[char_id]
                except KeyError:
                    continue

                track.register(char)
                char.register(track)

                self._char_to_track[char_id] = track_id

        # char to bg
        for (char_id, bgs) in self.data["char_to_bg"].items():
            try:
                char = self.data_all.character[char_id]
            except KeyError:
                continue

            for bg_id in bgs:
                if bg_id in ["BG_Red.jpg", "BG_Black.jpg", "BG_White.jpg"]:
                    continue

                try:
                    bg = self.data_all.background[bg_id]
                except KeyError:
                    continue

                char.register(bg)
                bg.register(char)

                self._bg_to_char[bg_id] = char_id
                self._char_to_bg[char_id] = bg.uuid

        # char to char
        _char_to_char = []
        for (char_id, data) in self.data["char_to_char"].items():
            try:
                char1 = self.data_all.character[char_id]
            except KeyError:
                continue

            for char2_id in data:
                try:
                    char2 = self.data_all.character[char2_id]
                except KeyError:
                    continue

                # 唯一识别ID，防止二次注册
                _ctc_id1 = f"{char_id}_{char2_id}"
                _ctc_id2 = f"{char2_id}_{char_id}"
                if _ctc_id1 in _char_to_char or _ctc_id2 in _char_to_char:
                    continue
                _char_to_char.append(_ctc_id1)
                _char_to_char.append(_ctc_id2)

                char1.register(char2)
                char2.register(char1)

    def to_json(self):
        return {
            "all": self.data_all.to_json(),

            # for normal
            "_track_to_bg": self.data["track_to_bg"],
            # for indexing
            "track_to_bg": self._track_to_bg.to_json(),

            "track_to_char": self.data["track_to_char"],

            "bg_to_char": self._bg_to_char.to_json(),
            "bg_to_track": self._bg_to_track.to_json(),

            "char_to_track": self._char_to_track.to_json(),

            # for normal
            "_char_to_bg": self.data["char_to_bg"],
            # for indexing
            "char_to_bg": self._char_to_bg.to_json(),

            "char_to_char": self.data["char_to_char"],
            "special": {
                "flag": self.data_special["flag"],
                "track": None if self.data_special["track"] is None else self.data_special["track"].to_json_basic()
            }
        }

    @property
    def bgm_special(self):
        # see this traceback:
        # --------------------------
        # File "F:\GitFile\BA_OST_Index_Parser\data_model\actual_data\track.py", line 96, in register
        #   for i in file_loader.part.bgm_special:
        # --------------------------
        # and now you know.
        if self.data_special["flag"]:
            return [self.data_special["track"]]
        else:
            return []

    def to_json_basic_tracks(self):
        # traceback:
        # File "F:\GitFile\BA_OST_Index_Parser\data_model\actual_data\story.py", line 355, in to_json
        #   t["bgm_special"] = self.part.to_json_basic_tracks()
        try:
            return [self.data_special["track"].to_json_basic()]
        except Exception:
            return []
