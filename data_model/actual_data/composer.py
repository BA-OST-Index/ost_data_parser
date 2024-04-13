from collections import OrderedDict

from ..loader import FileLoader
from .used_by import BaseUsedBy, UsedByRegisterMixin, UsedByToJsonMixin
from ..constant.file_type import FILETYPES_TRACK
from ..tool.interpage import InterpageMixin
from ..types.url import UrlModel
from ..tool.tool import ObjectAccessProxier


class ComposerUsedBy(BaseUsedBy, UsedByToJsonMixin):
    SUPPORTED_FILETYPE = [*FILETYPES_TRACK]

    def __init__(self):
        self.data_track = OrderedDict()

    def register(self, file_loader: FileLoader, count_increase=True):
        filetype = file_loader.filetype
        instance_id = file_loader.instance_id

        if filetype in self.SUPPORTED_FILETYPE:
            if filetype in FILETYPES_TRACK:
                self.data_track[instance_id] = file_loader
        else:
            raise ValueError

    def to_json(self, no_used_by: bool = True):
        return {"data_track": [i.to_json_basic() for i in self.data_track.values()]}


class NameMasker(ObjectAccessProxier):
    def __init__(self, obj: str):
        """兼容Interpage相关策略"""
        super().__init__(obj)

    def to_json(self):
        return {
            "en": self._object,
            "zh_cn": self._object,
            "jp": self._object
        }

    def to_json_basic(self):
        return self.to_json()


class ComposerInfo(FileLoader, UsedByRegisterMixin, InterpageMixin):
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        self.data = data = kwargs["data"]

        self.no = data["no"]
        self.name = NameMasker(data["name"]["nickname"])
        self.realname = data["name"]["realname"]
        self.nickname = data["name"]["nickname"]
        self.intro = data["intro"]

        self.contact = UrlModel()
        self.contact.load(data["contact"])

        self.used_by = ComposerUsedBy()

    @staticmethod
    def _get_instance_id(data: dict):
        return str(data["no"])

    def to_json(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "namespace": self.namespace,

            "name": self.name.to_json(),
            "no": self.no,
            "realname": self.realname,
            "nickname": self.nickname,
            "intro": self.intro,
            "contact": self.contact.to_json(),

            "used_by": self.used_by.to_json(),
            "interpage": self.get_interpage_data()
        }
        return d

    def to_json_basic(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "namespace": self.namespace,

            "name": self.name.to_json(),
            "no": self.no,
            "realname": self.realname,
            "nickname": self.nickname,
            "intro": self.intro,
            "contact": self.contact.to_json(),

            "interpage": self.get_interpage_data()
        }
        return d

    def _get_instance_offset(self, offset: int):
        keys = list(self._instance.keys())
        curr_index = keys.index(self.instance_id)

        try:
            if curr_index == 0 and offset < 0:
                return None
            return self._instance[keys[curr_index + offset]]
        except (IndexError, KeyError):
            return None
