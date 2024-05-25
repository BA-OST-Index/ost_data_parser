import logging
from data_model.loader import i18n_translator
from data_model.tool.to_json import IToJson
from data_model.loader.manager_constant import constant_manager
from collections import UserList


class TrackPlaybackDataEntry(IToJson):
    def __init__(self, nx_data: dict, iframe_data: dict):
        self.nx_data = nx_data
        self.iframe_data = iframe_data

        self.process()

    @staticmethod
    def get_iframe_url(para1_type: int, para2_id: int, url: str = "https://music.163.com/outchain/player"):
        return f"{url}?type={para1_type}&id={para2_id}"

    def process(self):
        self.result = {
            "id": self.nx_data["id"],
            "path": self.nx_data["path"],
            "type": i18n_translator.query(f'[TRACK_PLAYBACK_TYPE_{self.nx_data["type"]}]'),
            "desc": i18n_translator.query(self.nx_data["desc"]),
            "timestamp": self.nx_data["timestamp"]
        }

        if self.iframe_data["iframe_parameter"]["url"] != "":
            self.result["iframe_url"] = self.get_iframe_url(**self.iframe_data["iframe_parameter"])
        else:
            self.result["iframe_url"] = self.iframe_data["url_detail"]

    def to_json(self):
        return {
            "id": self.result["id"],
            "path": self.result["path"],
            "type": self.result["type"].to_json(),
            "desc": self.result["desc"].to_json(),
            "timestamp": self.result["timestamp"],
            "iframe_url": self.result["iframe_url"]
        }

    def to_json_basic(self):
        return self.to_json()


class TrackPlaybackDataListManager(UserList, IToJson):
    def load(self, data: list):
        for i in data:
            self.append(TrackPlaybackDataEntry(i))

    def to_json(self):
        return [i.to_json_basic() for i in self]

    def to_json_basic(self):
        return self.to_json()


class TrackPlayback(IToJson):
    def __init__(self, instance_id: str):
        self.instance_id = instance_id
        self.all_data = TrackPlaybackDataListManager()

        self.process()

    def process(self):
        try:
            all_playback_data = constant_manager.query("track_playback", self.instance_id)

            for entry in all_playback_data:
                iframe_data = constant_manager.query("track_playback_ref", entry["path"])

                self.all_data.append(TrackPlaybackDataEntry(entry, iframe_data))
        except KeyError:
            logging.warning(f"No TrackPlayback info for \"{self.instance_id}\"")

    def to_json(self):
        return self.all_data.to_json()

    def to_json_basic(self):
        return self.all_data.to_json_basic()
