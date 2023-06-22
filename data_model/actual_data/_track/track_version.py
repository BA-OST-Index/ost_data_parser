from data_model.types.metatype.basic import Bool, BasicModel, MultipleBasicModelList
from data_model.types.url import UrlModel, MultipleUrlModelList
from data_model.types.lang_string import LangStringModel
from data_model.loader import constant_manager

__all__ = ["TrackVersion", "TrackVersionList"]


# ---------------------------------------------------------
# TrackVersion & TrackVersionList

class TrackVersion(BasicModel):
    is_main = Bool('is_main')
    _components = ["url", "desc", "is_main"]

    def __init__(self):
        super().__init__(None)
        self.url = MultipleUrlModelList('url')
        self.desc = LangStringModel()

    def load(self, data):
        super().load(data)
        self.is_main = data["is_main"]
        self.desc.load(constant_manager.query("ost", data["desc"]))
        for i in data["url"]:
            m = UrlModel()
            m.load(i)
            self.url.append(m)

    def to_json(self):
        return None, dict((key, getattr(self, key))
                          for key in self._components)

    def to_json_basic(self):
        return self.to_json()[-1]


class TrackVersionList(MultipleBasicModelList):
    def __init__(self, key_name):
        super().__init__(key_name, TrackVersion)
