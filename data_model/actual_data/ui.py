from .track import TrackInfo
from ..types.url import UrlModel
from ..loader import i18n_translator, FileLoader
from ..tool.parent_data import IParentData
from ..tool.interpage import InterpageMixin


class UiInfo(FileLoader, IParentData, InterpageMixin):
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
            "namespace": self.namespace,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "track": self.track.to_json_basic(),
            "image": self.image.to_json_basic(),
            "id": self.data["name"].split("_")[1],

            "parent_data": self.parent_data_to_json(),
            "interpage": self.get_interpage_data()
        }

    def to_json_basic(self):
        return self.to_json()

    def _get_instance_offset(self, offset: int):
        keys = list(self._instance.keys())
        curr_index = keys.index(self.instance_id)

        try:
            if curr_index == 0 and offset < 0:
                return None
            return self._instance[keys[curr_index + offset]]
        except (IndexError, KeyError):
            return None


class UiInfoEvent(UiInfo):
    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])

        self.event_id = self.data["event_id"]

    @staticmethod
    def _get_instance_id(data: dict):
        return "UI_" + "_".join([data["event_id"], data["name"].split("_")[1]])

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "track": self.track.to_json_basic(),
            "image": self.image.to_json_basic(),
            "event_id": self.event_id,
            "id": self.data["name"].split("_")[1],

            "parent_data": self.parent_data_to_json(),
            "interpage": self.get_interpage_data()
        }
