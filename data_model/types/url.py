from .metatype.basic import BasicModel, String, MultipleBasicModelList, Integer, MultipleBasicModelListManager
from .metatype.complex import Url
from ..loader.constant import constant_manager

__all__ = ["UrlModel", "MultipleUrlModelList", "MultipleUrlModelListManager"]


class UrlModel(BasicModel):
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
            "platform": constant_manager.query("platform", self.platform).to_json()[-1],
            "value": self.value,
            "short_desc": self.short_desc
        }
        return self.key_name, t

    def to_json_basic(self):
        return self.to_json()[1]


class MultipleUrlModelList(MultipleBasicModelList):
    def __init__(self, key_name):
        super().__init__(key_name, UrlModel)


class MultipleUrlModelListManager(MultipleBasicModelListManager):
    def __init__(self, key_name):
        super().__init__(key_name)
        self.url = MultipleUrlModelList(key_name)

    def load(self, data: list):
        super().load(data)
        for i in data:
            t = UrlModel()
            t.load(i)
            self.url.append(t)

    def to_json(self):
        return None, self.url.to_json()[-1]

    def to_json_basic(self):
        return self.to_json()[-1]
