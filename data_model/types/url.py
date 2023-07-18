from .metatype.base_type import  String, Integer
from .metatype.base_model import BaseDataModel, BaseDataModelList, BaseDataModelListManager
from .metatype.complex import Url
from ..loader.manager_constant import constant_manager

__all__ = ["UrlModel", "UrlModelList", "UrlModelListManager"]


class UrlModel(BaseDataModel):
    platform = Integer("platform")
    value = Url("value")
    short_desc = String("short_desc")
    _components = ["platform", "value", "short_desc"]

    def __init__(self):
        super().__init__("url")

    def load(self, data: dict):
        super().load(data)
        self.platform = data["platform"]
        self.value = data["value"]
        self.short_desc = data["short_desc"]

    def to_json(self):
        t = {
            "platform": constant_manager.query("platform", self.platform).to_json(),
            "value": self.value,
            "short_desc": self.short_desc
        }
        return t

    def to_json_basic(self):
        return self.to_json()


class UrlModelList(BaseDataModelList):
    def __init__(self, key_name):
        super().__init__(key_name, UrlModel)


class UrlModelListManager(BaseDataModelListManager):
    def __init__(self, key_name):
        super().__init__(key_name)
        self.url = UrlModelList(key_name)

    def load(self, data: list):
        super().load(data)
        for i in data:
            t = UrlModel()
            t.load(i)
            self.url.append(t)

    def to_json(self):
        return self.url.to_json()

    def to_json_basic(self):
        return self.to_json()
