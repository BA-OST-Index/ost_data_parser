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
            if os.path.isfile(self.join_path(i)):
                # Skip folders (e.g. /data/i18n/xx/schale)
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

        # NEW: ZhLangStringModel 自动降级到 LangStringModel
        # 由于 ZhLangStringModel 在导出到JSON后太占存储空间，为了爱和正义决定根据特殊情况将其自动
        # 降级到 LangStringModel 进行处置
        if temp["zh_cn_cn"] == temp["zh_cn_jp"] == temp["zh_cn_tw"]:
            # 如果三者全部都一样，那不就是单语言？
            temp["zh_cn"] = temp["zh_cn_cn"]
            m = LangStringModel()
            m.load(temp)
        else:
            # 单独考察三种小语言，是不是有两个是空的
            try:
                if temp["zh_cn_cn"] == "" and temp["zh_cn_jp"] == "":
                    temp["zh_cn"] = temp["zh_cn_tw"]
                elif temp["zh_cn_cn"] == "" and temp["zh_cn_tw"] == "":
                    temp["zh_cn"] = temp["zh_cn_jp"]
                elif temp["zh_cn_jp"] == "" and temp["zh_cn_tw"] == "":
                    temp["zh_cn"] = temp["zh_cn_cn"]
                else:
                    # 哦原来降级不了啊
                    raise AssertionError
            except AssertionError:
                # 降级不了，老老实实.jpg
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
                # 能降级就嗯降
                m = LangStringModel()
                m.load(temp)

        return m

    def query(self, key):
        return self[key]


i18n_translator = TranslationManager(DATA_PATH_TRANSLATION)
