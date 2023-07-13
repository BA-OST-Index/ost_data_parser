import abc
import os
import json
from collections import namedtuple
from data_model.config import DATA_BASE_PATH
from ..tool import NamespacePathMixin

IncludingInfo = namedtuple("IncludingInfo", ["name", "loader"])


class FolderLoader(abc.ABC, NamespacePathMixin):
    def __init__(self, namespace: list, basepath: str = DATA_BASE_PATH, json_data=None):
        self.basepath = basepath
        self.namespace = list(namespace)

        self.data = json_data if json_data else self.load_json("_all.json")
        self.including = self.auto_include()
        if self.data["namespace"] == "":
            self.namespace.append(os.path.split(basepath)[-1])
        else:
            self.namespace.append(self.data["namespace"])

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

        if self.data["include"][0] == "[ALL_INDEX]":
            dir = os.listdir(self.basepath)
            for i in dir:
                if i == "_all.json":
                    continue
                else:
                    including.append(i)
        else:
            including = self.data["include"]

        return including

    @abc.abstractmethod
    def process(self):
        pass
