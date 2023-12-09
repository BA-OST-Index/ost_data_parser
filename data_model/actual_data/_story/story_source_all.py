from data_model.types.url import UrlModel
from data_model.loader import i18n_translator
from data_model.tool.to_json import IToJson
from collections import UserList


class StoryInfoSourceList(UserList, IToJson):
    def __init__(self, data: list):
        super().__init__()
        for i in data:
            obj = UrlModel()
            obj.load(i)
            self.append(obj)

    def to_json(self):
        return [i.to_json() for i in self]

    def to_json_basic(self):
        return [i.to_json_basic() for i in self]


class StoryInfoSource(IToJson):
    _component = ["en", "zh_tw", "zh_cn_cn", "zh_cn_jp"]

    def __init__(self, data: dict):
        self.data = data
        self.en = StoryInfoSourceList(data.get("en", []))
        self.zh_tw = StoryInfoSourceList(data.get("zh_tw", []))
        self.zh_cn_cn = StoryInfoSourceList(data.get("zh_cn_cn", []))
        self.zh_cn_jp = StoryInfoSourceList(data.get("zh_cn_jp", []))

    def to_json(self):
        d = {}
        for i in self._component:
            d[i] = getattr(self, i).to_json()
        return d

    def to_json_basic(self):
        return self.to_json()
