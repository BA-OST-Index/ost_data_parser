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
            instance = self._instance[keys[curr_index + offset]]

            # 仅索引自己这一类的instance（比方说普通UI/活动UI）
            if instance.filetype != self.filetype:
                return None
            return instance
        except (IndexError, KeyError):
            return None


class UiInfoEvent(UiInfo):
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        self.event_id = self.data["event_id"]

    @staticmethod
    def _get_instance_id(data: dict):
        return "UI_" + "_".join([str(data["event_id"]), data["name"].split("_")[-2]])

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "track": self.track.to_json_basic(),
            "image": self.image.to_json_basic(),
            "event_id": self.event_id,
            "id": self.data["name"].split("_")[-2],

            "parent_data": self.parent_data_to_json(),
            "interpage": self.get_interpage_data()
        }

    def _get_instance_offset(self, offset: int):
        instance = super()._get_instance_offset(offset)
        if instance is not None:
            # 如果同样是 UiInfoEvent 对象
            if instance.event_id != self.event_id:
                # 如果不是一个 event 里头的
                return None
        return instance
