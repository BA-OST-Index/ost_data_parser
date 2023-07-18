from data_model.types.metatype.base_type import Bool
from data_model.types.metatype.base_model import BaseDataModel, BaseDataModelList
from data_model.types.url import UrlModel, UrlModelList
from data_model.types.lang_string import LangStringModel
from data_model.loader import constant_manager, i18n_translator

__all__ = ["TrackVersion", "TrackVersionList"]


# ---------------------------------------------------------
# TrackVersion & TrackVersionList

class TrackVersion(BaseDataModel):
    is_main = Bool('is_main')
    _components = ["url", "desc", "is_main"]

    def __init__(self):
        super().__init__(None)
        self.url = UrlModelList('url')

    def load(self, data):
        super().load(data)
        self.is_main = data["is_main"]
        self.desc = i18n_translator.query(data["desc"])
        for i in data["url"]:
            m = UrlModel()
            m.load(i)
            self.url.append(m)

    def to_json(self):
        return {key: getattr(self, key) for key in self._components}

    def to_json_basic(self):
        return self.to_json()


class TrackVersionList(BaseDataModelList):
    def __init__(self, key_name):
        super().__init__(key_name, TrackVersion)

    def to_json(self):
        d = []
        for value in self.basic_model_list:
            d.append({
                "desc": value.desc.to_json_basic(),
                "is_main": value.is_main,
                "url": value.url.to_json_basic()
            })
        return d
