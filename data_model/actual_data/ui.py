from .track import TrackInfo
from ..types.url import UrlModel
from ..loader import i18n_translator, FileLoader
from ..tool.parent_data import IParentData


class UiInfo(FileLoader, IParentData):
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])

        self.name = i18n_translator.query(self.data["name"])
        self.desc = i18n_translator.query(self.data["desc"])
        self.track = TrackInfo.get_instance(instance_id=self.data["track"])

        self.image = UrlModel()
        self.image.load(self.data["image"])

        self.track.register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        return "UI_" + data["name"].split("_")[1]

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "track": self.track.to_json_basic(),
            "image": self.image.to_json_basic(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return self.to_json()

