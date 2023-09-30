import abc
import os
import json
import hashlib
from collections import namedtuple
from ..config import DATA_BASE_PATH
from ..tool.tool import NamespacePathMixin, SingletonInstanceMixin
from ..tool.to_json import IToJson
from ..types.metatype.base_type import Integer
from ..types.metatype.complex import UUID
from ..loader import i18n_translator
from ..tool.parent_data import ParentDataMixin, ParentData
from ..constant.file_type import FILE_VIRTUAL_DATA

IncludingInfo = namedtuple("IncludingInfo", ["name", "loader"])


class BaseLoader(abc.ABC, IToJson):
    uuid = UUID('uuid')
    filetype = Integer('filetype')

    def __init__(self, data: dict, namespace: list):
        self.data = data
        self.uuid = data["uuid"]
        self.filetype = data["filetype"]
        self.namespace = namespace
        super().__init__()


class FolderLoader(NamespacePathMixin, IToJson, ParentDataMixin):
    def __init__(self, namespace: list, basepath: str = DATA_BASE_PATH, json_data=None, parent_data: ParentData = None):
        self.basepath = basepath
        self.namespace = list(namespace)

        self.data: dict = json_data if json_data else self.load_json("_all.json")
        self.uuid = self.data["uuid"]
        self.filetype = self.data["filetype"]
        self.name = i18n_translator.query(self.data["name"])
        self.desc = i18n_translator.query(self.data["desc"])
        self.including = self.auto_include()
        if self.data["namespace"] == "":
            self.namespace.append(os.path.split(basepath)[-1])
        else:
            self.namespace.append(self.data["namespace"])

        if self.parent_data_exist and self.parent_data_enable:
            self._parent_data = parent_data
            self.load_parent_data()

        self.process()

    def load_json(self, path):
        with open(os.path.join(self.basepath, path), mode="r", encoding="UTF-8") as file:
            return json.load(file)

    def is_folder(self, path):
        return os.path.isdir(self.join_path(path))

    def is_file(self, path):
        return os.path.isfile(self.join_path(path))

    def join_path(self, path):
        return os.path.join(self.basepath, path)

    def auto_include(self):
        including = []

        if self.data["include"][0] == "[AUTO]":
            dirs = os.listdir(self.basepath)
            for i in dirs:
                if i == "_all.json":
                    continue
                else:
                    including.append(i)
        else:
            including = self.data["include"]

        # linux, why would you list the dirs from Z to A?
        including.sort()

        return including

    def process(self):
        # TODO: Avoid circular imports
        from .loader_detect import get_loader_by_filepath
        for (n, i) in enumerate(self.including):
            if os.path.isfile(self.join_path(i)):
                self.including[n] = IncludingInfo(i, get_loader_by_filepath(
                    self.namespace + [self._get_filename_without_extension(self.join_path(i))],
                    self.join_path(i), self.parent_data if self.parent_data_exist else None))
            else:
                self.including[n] = IncludingInfo(i, get_loader_by_filepath(self.namespace, self.join_path(i),
                                                                            self.parent_data if self.parent_data_exist else None))

    @staticmethod
    def _get_filename_without_extension(filename):
        splited = os.path.split(filename)[-1]
        splited = splited.split(".")[:-1]
        return ".".join(splited)

    @abc.abstractmethod
    def to_json(self):
        pass

    @abc.abstractmethod
    def to_json_basic(self):
        pass


class FileLoader(BaseLoader, SingletonInstanceMixin, NamespacePathMixin, IToJson):
    @abc.abstractmethod
    def __init__(self, **kwargs):
        BaseLoader.__init__(self, kwargs["data"], kwargs["namespace"])

        try:
            self.parent_data = kwargs["parent_data"]
        except Exception:
            self.parent_data = None

    @staticmethod
    @abc.abstractmethod
    def _get_instance_id(data):
        pass

    @abc.abstractmethod
    def to_json(self):
        pass

    @abc.abstractmethod
    def to_json_basic(self):
        pass


class VirtualLoader(BaseLoader, NamespacePathMixin):
    """一种用于二次处理数据的特殊Loader，在所有数据载入后再进行。"""

    @abc.abstractmethod
    def __init__(self, loader_name: str, template_path, page_path):
        def uuid_gen(string: str):
            md5 = hashlib.md5(string.encode("UTF-8")).hexdigest()
            uuid = "-".join([md5[0:8], md5[8:12], md5[12:16], md5[16:20], md5[20:32]])
            return uuid

        BaseLoader.__init__(self,
                            {
                                "uuid": uuid_gen(loader_name),
                                "filetype": FILE_VIRTUAL_DATA,
                                "name": f"[VIRTUAL_{loader_name.upper()}_NAME]",
                                "desc": f"[VIRTUAL_{loader_name.upper()}_DESC]"
                            },
                            ["virtual_data", loader_name + ".json"])
        self.template_path = template_path
        self.page_path = page_path

        self.load_data()

    @abc.abstractmethod
    def load_data(self):
        pass

    @abc.abstractmethod
    def to_json(self):
        return {
            "uuid": self.data["uuid"],
            "filetype": self.data["filetype"],
            "name": i18n_translator.query(self.data["name"]).to_json(),
            "desc": i18n_translator.query(self.data["desc"]).to_json(),
            "template_path": self.template_path,
            "page_path": self.page_path
        }

    def to_json_basic(self):
        return self.to_json()
