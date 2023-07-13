import json
import os
from ..types.lang_string import LangStringModel, ZhLangStringModel
from ..config import DATA_PATH_TRANSLATION


class SingleLanguageTranslation:
    """自适应单语言全文件检索"""

    def __init__(self, basepath):
        self.basepath = basepath
        self.filelist = list(os.listdir(basepath))
        self.langcode = os.path.split(basepath)[-1]

        self.all_trans = {}
        self.load_json()

    def join_path(self, path):
        return os.path.join(self.basepath, path)

    def load_json(self):
        for i in self.filelist:
            # According to this StackOverflow question:
            # "How do I merge two dictionaries in a single expression in Python?"
            # though "dict | dict" is possible above Python 3.9,
            # for maximum compatibility I decided to take a step back
            # and use "z = {**x, **y}" (above Python 3.5) instead.
            with open(self.join_path(i), mode="r", encoding="UTF-8") as file:
                content = json.load(file)
            self.all_trans = {**self.all_trans, **content}

    def get(self, item):
        return self.all_trans.get(item, "")


class TranslationManager:
    def __init__(self, basepath):
        self.basepath = basepath
        self.filelist = list(os.listdir(basepath))

        self.translations = {}
        self.load()

    def join_path(self, path):
        return os.path.join(self.basepath, path)

    def load(self):
        for key in self.filelist:
            self.translations[key] = SingleLanguageTranslation(self.join_path(key))

    def __getitem__(self, item) -> LangStringModel:
        temp = dict((key, value.get(item)) for key, value in self.translations.items())
        if temp["zh_cn"] == "":
            # Special i18n case: Student Name, etc.
            # There are at lease 3 variants when talking about that in Chinese.
            # - zh_cn_cn indicates the data from the Blue Archive (China Server)
            # - zh_cn_tw indicates the data from the Blue Archive (Global/Taiwan Server)
            #   But with the content being converted from Traditional to Simplified Chinese
            # - zh_cn_jp indicates the data from a third-party unofficial translation of
            #   the original Japanese content (which is widely-accepted as well).
            m = ZhLangStringModel()
            m.load(temp)
        else:
            m = LangStringModel()
            m.load(temp)
        return m

    def get(self, key):
        return self[key]


i18n_translator = TranslationManager(DATA_PATH_TRANSLATION)
