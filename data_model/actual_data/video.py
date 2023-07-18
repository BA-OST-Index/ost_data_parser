from ..loader import FileLoader, i18n_translator
from ..types.url import UrlModel
from ..actual_data.track import TrackListManager, TrackVersionListManager

class VideoInfo(FileLoader):
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
            "name": self.name.to_json_basic(),
            "desc": self.name.to_json_basic(),
            "image": self.image.to_json_basic(),
            "version": self.version.to_json_basic(),
            "track": self.track.to_json_basic()
        }
        return t

    def to_json_basic(self):
        return self.to_json()

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)
