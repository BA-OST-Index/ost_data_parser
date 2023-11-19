from ..loader import FileLoader, i18n_translator
from ..types.url import UrlModel
from ..actual_data.track import TrackListManager, TrackVersionListManager
from ..tool.interpage import InterpageMixin
from ..tool.to_json import IToJson


class VideoStats(IToJson):
    def __init__(self, data: dict):
        self.data = data

        # 基本上就是做数据检查，有不对的就报错
        # 这部分不需要额外处理
        all_key = ["is_jp", "is_global", "is_cn",
                   "is_pv", "is_pv_char", "is_pv_ani",
                   "is_mv", "is_animation", "is_other",
                   "is_ad", "is_ingame"]
        for i in all_key:
            if i not in data.keys():
                raise ValueError("key {} not exist".format(i))
            if not isinstance(data[i], bool):
                raise TypeError("expected bool, got {}".format(type(data[i])))

    def to_json(self):
        return self.data

    def to_json_basic(self):
        return self.data

    def __getattr__(self, item):
        return self.data[item]


class VideoInfo(FileLoader, InterpageMixin):
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])

        self.name = i18n_translator.query(self.data["name"])
        self.desc = i18n_translator.query(self.data["desc"])
        self.image = UrlModel()
        self.image.load(self.data["image"])
        self.version = TrackVersionListManager('version')  # I'm just gonna reuse it anyway
        self.version.load(self.data["version"])
        self.track = TrackListManager()
        self.track.load(self.data["track"])
        self.stats = VideoStats(self.data["stats"])

        self.extra_register()

    def extra_register(self):
        for track in self.track.track:
            track.register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        return "VID_" + data["name"].split("_")[1]

    def to_json(self):
        t = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "namespace": self.namespace,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "image": self.image.to_json_basic(),
            "version": self.version.to_json_basic(),
            "track": self.track.to_json_basic(),
            "stats": self.stats.to_json_basic(),
            "interpage": self.get_interpage_data()
        }
        return t

    def to_json_basic(self):
        return self.to_json()

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)

    def _get_instance_offset(self, offset: int):
        keys = list(self._instance.keys())
        curr_index = keys.index(self.instance_id)

        try:
            if curr_index == 0 and offset < 0:
                return None
            return self._instance[keys[curr_index + offset]]
        except (IndexError, KeyError):
            return None
