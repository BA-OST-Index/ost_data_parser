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
                try:
                    id_ = temp["file_id"]
                    del temp["file_id"], temp["filetype"]
                except KeyError:
                    # 默认fallback策略
                    id_ = os.path.splitext(key)[0]

                self.constant[id_] = temp

    def query(self, constant_id: str, value: str or int):
        result = self.constant[constant_id][str(value)]
        if isinstance(result, dict):
            if "en" in result.keys():
                # It's an LangStringModel object!
                t = LangStringModel()
                t.load(result)
                return t
            else:
                # Maybe just a normal dict, like in `composer.json`
                return result
        else:
            return result

    def query_by_constant_file(self, constant_id: str):
        constant_keys = self.constant[constant_id].keys()
        d = {key: self.query(constant_id, key) for key in constant_keys}
        return d


constant_manager = ConstantManager(DATA_PATH_CONSTANT)
