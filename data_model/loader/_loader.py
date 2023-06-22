import abc
import copy
import os
import json
from data_model.config import DATA_BASE_PATH
from functools import partial


def join_path(basepath, path):
    return os.path.join(basepath, path)


class BaseLoader(abc.ABC):
    def __init__(self, namespace: list, base_path: str = DATA_BASE_PATH):
        self.base_path = base_path
        self.namespace = copy.deepcopy(namespace)
        self.process()

        self.json_all = self.load_json("all.json")
        self.including = self.json_all["include"]
        if self.json_all["name"] == "":
            self.namespace.append(os.path.split(base_path)[-1])
        else:
            self.namespace.append(self.json_all["name"])

        # 暴露JSON

    def load_json(self, path):
        with open(os.path.join(self.base_path, path), mode="r", encoding="UTF-8") as file:
            return json.load(file)

    def is_folder(self, path):
        return os.path.isdir(self.join_path(path))

    def is_file(self, path):
        return os.path.isfile(self.join_path(path))

    def join_path(self, path):
        return os.path.join(self.base_path, path)

    @abc.abstractmethod
    def process(self):
        pass
