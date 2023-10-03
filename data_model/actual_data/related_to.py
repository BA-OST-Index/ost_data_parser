import abc
from ..loader import FileLoader
from ..tool.to_json import IToJson


class BaseRelatedTo(abc.ABC, IToJson):
    @abc.abstractmethod
    def register(self, file_loader: FileLoader, related_to_keyname: str, auto_register: bool = False):
        raise NotImplementedError


class RelatedToRegisterMixin:
    def register_related_to(self, file_loader: FileLoader, related_to_keyname: str, auto_register: bool = False):
        self.related_to.register(file_loader, related_to_keyname, auto_register)


class RelatedToJsonMixin(IToJson):
    def to_json(self):
        d = {}
        for i in self._components:
            data = getattr(self, i)

            # 对曲子排序作特别优化
            # 改自 UsedByToJsonMixin.to_json 函数
            if len(data) > 0 and "track" in i:
                data_ = []
                for j in sorted(data, key=lambda k: int(data[k].no)):
                    data_.append(data[j].to_json_basic())
                data = data_
            else:
                data_ = [i.to_json_basic() for i in data.values()]

            d[i] = data_

        return d

    def to_json_basic(self):
        return self.to_json()
