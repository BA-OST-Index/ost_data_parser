from data_model.loader import i18n_translator
from data_model.tool.to_json import IToJson
from data_model.constant.platform import BILIBILI, YOUTUBE


class StoryVideoInfo(IToJson):
    """兼容 UrlModel 模型"""
    def __init__(self, data):
        """
        data = {"url": "https://youtube.com/watch?v=Fsdfjisdjfio", "short_desc": "fjsdifajio"}
        """
        self.data = data

        self.value = data.get("value", "")
        self.platform = self._detect_platform(self.value)
        self.short_desc = i18n_translator.query(data.get("short_desc", ""))

    @staticmethod
    def _detect_platform(url):
        if "bilibili.com" in url:
            return BILIBILI
        elif "youtube.com" in url or "youtu.be" in url:
            return YOUTUBE

        raise ValueError

    def to_json(self):
        return {
            "value": self.url,
            "platform": int(self.platform),
            "short_desc": self.short_desc.to_json()
        }

    def to_json_basic(self):
        return self.to_json()


class StoryVideoLanguageInfo(IToJson):
    def __init__(self, data: list):
        self.data = [StoryVideoInfo(i) for i in data]

    def to_json(self):
        return [i.to_json() for i in self.data]

    def to_json_basic(self):
        return self.to_json()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]




class StoryInfoVideoType(IToJson):
    _component = []

    def __init__(self, data: dict):
        for i in self._component:
            setattr(self, i, StoryVideoLanguageInfo(data.get(i, [])))

    def to_json(self):
        return [getattr(self, i).to_json() for i in self._component]

    def to_json_basic(self):
        return self.to_json()


class StoryInfoVideoTypeOfficial(StoryInfoVideoType):
    _component = ["zh_cn_cn", "zh_tw", "en"]

    def __init__(self, data: dict):
        super().__init__(data)


class StoryInfoVideoTypeUnofficial(StoryInfoVideoType):
    _component = ["zh_cn_jp", "en"]

    def __init__(self, data: dict):
        super().__init__(data)


class StoryInfoVideo(IToJson):
    def __init__(self, data):
        self.data = data
        self.video_official = StoryInfoVideoTypeOfficial(data.get("official", {}))
        self.video_unofficial = StoryInfoVideoTypeUnofficial(data.get("unofficial", {}))

    def to_json(self):
        return {
            "official": self.video_official.to_json(),
            "unofficial": self.video_unofficial.to_json()
        }

    def to_json_basic(self):
        return self.to_json()
