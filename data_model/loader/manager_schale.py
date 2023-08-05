import os
import json
from ..types.lang_string import LangStringModel, ZhLangStringModel
from ..config import DATA_PATH_TRANSLATION


class SchaleDbSingleLanguage:
    def __init__(self, basepath):
        self.basepath = basepath
        self.filelist = list(os.listdir(basepath))
        self.lang_code = os.path.split(basepath)[-1]

        self.all_trans = {}
        self.load_json()

    def join_path(self, path):
        return os.path.join(self.basepath, path)

    def load_json(self):
        # Compared with the i18n manager, we're not merging the files there
        # as they are actually a kind of constant, yet they are not actually
        # 100% compatible with the existing constant.
        for i in self.filelist:
            with open(self.join_path(i), mode="r", encoding="UTF-8") as file:
                content = json.load(file)

            # Leaving only the pure file name, without the extension name
            self.all_trans[i[:-5]] = content

    def query(self, filename, *keys):
        try:
            r = self.all_trans[filename]
            for i in keys:
                r = r[i]
            return r
        except KeyError:
            return "[NO_KEY_DATA]"


class SchaleDbManager:
    def __init__(self, basepath):
        self.basepath = basepath
        self.filelist = set(os.listdir(basepath)) - {"zh_cn"}

        self.constants = {}
        self.load()

    def load(self):
        for key in self.filelist:
            self.constants[key] = SchaleDbSingleLanguage(os.path.join(self.basepath, f"{key}/schale"))

    def query(self, filename, *keys):
        temp = {lang: value.query(filename, *keys)
                for lang, value in self.constants.items()}
        m = ZhLangStringModel()
        m.load(temp)
        return m

    def query_constant(self, filename, *keys):
        return self.constants["en"].query(filename, *keys)


schale_db_manager = SchaleDbManager(DATA_PATH_TRANSLATION)
