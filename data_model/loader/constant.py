import json
import os
from ..config import DATA_PATH_CONSTANT
from ..types.lang_string import LangStringModel


class ConstantManager:
    def __init__(self, basepath):
        self.basepath = basepath
        self.filelist = list(os.listdir(basepath))

        self.constant = {}
        self.load()

    def join_path(self, path):
        return os.path.join(self.basepath, path)

    def load(self):
        for key in self.filelist:
            with open(self.join_path(key), mode="r", encoding="UTF-8") as file:
                temp = json.load(file)
                id_ = temp["file_id"]
                del temp["file_id"], temp["file_type"]

                self.constant[id_] = temp

    def query(self, constant_id: str, value: str or int = None):
        if value is None:
            return self.constant[constant_id]

        # Is it a LangStringModel object?
        result = self.constant[constant_id][str(value)]
        t = LangStringModel()
        t.load(result)
        if not any([value for value in t.to_json()[1].values()]):
            return result
        return t


constant_manager = ConstantManager(DATA_PATH_CONSTANT)
