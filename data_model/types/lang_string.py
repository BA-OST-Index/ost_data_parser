from .metatype.base_type import String
from .metatype.base_model import BaseDataModel, BaseDataModelList

__all__ = ["LangStringModel", "LangStringModelList", "ZhLangStringModel"]


class LangStringModel(BaseDataModel):
    """如 name description 此类需要多语言支持的东西"""
    en = String("en")
    jp = String("jp")
    thai = String("thai")
    ko = String("ko")
    zh_cn = String("zh_cn")
    zh_tw = String("zh_tw")
    _components = ["en", "jp", "thai", "ko", "zh_cn", "zh_tw"]

    def __init__(self, key_name=None):
        super().__init__(key_name)

    def load(self, data: dict):
        super().load(data)
        self.en = data.get("en", "")
        self.jp = data.get("jp", "")
        self.thai = data.get("that", "")
        self.ko = data.get("ko", "")
        self.zh_cn = data.get("zh_cn", "")
        self.zh_tw = data.get("zh_tw", "")

    def get_content(self, lang_code: str, raise_error: bool = False):
        lang_code = lang_code.replace("-", "_")
        if hasattr(self, lang_code):
            result = getattr(self, lang_code)
            if result == "":
                return self.en or self.zh_tw or self.zh_cn
            return result

        if raise_error:
            raise ValueError("Invalid lang_code %r" % lang_code)

        # When couldn't be found, search in the following order.
        return self.en or self.zh_tw or self.zh_cn

    def to_json(self):
        return dict((key, self.get_content(key)) for key in self._components)

    def to_json_basic(self):
        return self.to_json()


class ZhLangStringModel(LangStringModel):
    zh_cn_jp = String("zh_cn_jp")
    zh_cn_tw = String("zh_cn_tw")
    zh_cn_cn = String("zh_cn_cn")
    _components = ["en", "jp", "thai", "ko", "zh_tw", "zh_cn_jp", "zh_cn_tw", "zh_cn_cn"]

    def load(self, data: dict):
        super().load(data)
        self.zh_cn_jp = data.get("zh_cn_jp", "")
        self.zh_cn_tw = data.get("zh_cn_tw", "")
        self.zh_cn_cn = data.get("zh_cn_cn", "")

    def get_content(self, lang_code: str, raise_error: bool = False):
        """Partially rewrite for zh_cn support."""
        def get_zh_cn():
            return self.zh_cn_tw or self.zh_cn_jp or self.zh_cn_cn

        def get_other():
            return self.en or self.zh_tw or get_zh_cn()

        lang_code = lang_code.replace("-", "_")
        if lang_code == "zh_cn":
            raise ValueError("zh-cn is not supported!")

        if hasattr(self, lang_code):
            result = getattr(self, lang_code)
            if result == "":
                if lang_code.startswith("zh_cn"):
                    return get_zh_cn()
                else:
                    return get_other()
            return result

        if raise_error:
            raise ValueError("Invalid lang_code %r" % lang_code)

        # When couldn't be found, search in the following order.
        return get_other()


class LangStringModelList(BaseDataModelList):
    def __init__(self, key_name):
        super().__init__(key_name, LangStringModel)
