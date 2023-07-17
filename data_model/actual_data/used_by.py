import abc
from ..loader import FileLoader
from ..tool.to_json import IToJson
from ..tool.tool import OrderedDictWithCounter

__all__ = ["BaseUsedBy", "UsedByToJsonMixin", "UsedByRegisterMixin", "OrderedDictWithCounter"]


class BaseUsedBy(abc.ABC, IToJson):
    SUPPORTED_FILETYPE = []

    @abc.abstractmethod
    def register(self, file_loader: FileLoader):
        raise NotImplementedError


class UsedByRegisterMixin(abc.ABC):
    def register(self, file_loader: FileLoader):
        self.used_by.register(file_loader)


class UsedByToJsonMixin(IToJson):
    def to_json(self, no_used_by: bool = True):
        d = {}
        for i in self._components:
            data = getattr(self, i).get_counter_with_data()
            d[i] = {key: [value[0].to_json_basic(), value[1]] for key, value in data.items()}
        return d

    def to_json_basic(self):
        return self.to_json()
