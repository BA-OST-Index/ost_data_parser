from data_model.types.url import UrlModel
from data_model.loader import i18n_translator, constant_manager
from data_model.tool.to_json import IToJson
from data_model.constant.platform import BILIBILI, YOUTUBE, BLUEARCHIVE_IO
from .story_source_all import StoryInfoSource, StoryInfoSourceList
from collections import UserList
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode


class StoryInfoPartSourceEntry(IToJson):
    VIDEO_SITES = [BILIBILI, YOUTUBE]

    def __init__(self, part_data: dict, story_data: UrlModel):
        self.part_data = part_data
        self.story_data = story_data

        try:
            self.base_url = part_data["value"]
            self.platform = part_data["platform"]
            self.desc = i18n_translator.query(part_data["short_desc"])
        except KeyError:
            self.base_url = story_data.value
            self.platform = story_data.platform
            self.desc = story_data.short_desc

        self.url = self.get_url()

    def get_url(self):
        parsed_url = urlparse(self.base_url)
        parameters = parse_qs(parsed_url.query)

        if str(self.platform) in self.VIDEO_SITES:
            parameters["t"] = self.part_data["timestamp"]
        elif str(self.platform) == BLUEARCHIVE_IO:
            parameters["changeIndex"] = self.part_data["script_index"]
        else:
            raise ValueError

        modified_query = urlencode(parameters, doseq=True)

        modified_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params,
                                   modified_query, parsed_url.fragment))
        return modified_url

    def to_json(self):
        t = {
            "platform": constant_manager.query("platform", self.platform).to_json(),
            "value": self.url,
            "short_desc": self.desc.to_json()
        }
        return t

    def to_json_basic(self):
        return self.to_json()


class StoryInfoPartSourceList(UserList, IToJson):
    def __init__(self, part_data: list, story_data: StoryInfoSourceList):
        super().__init__()
        for i, j in zip(part_data, story_data):
            self.append(StoryInfoPartSourceEntry(i, j))

    def to_json(self):
        return [i.to_json() for i in self]

    def to_json_basic(self):
        return self.to_json()


class StoryInfoPartSource(IToJson):
    _component = ["en", "zh_tw", "zh_cn_cn", "zh_cn_jp"]

    def __init__(self, part_data: dict, story_data: StoryInfoSource):
        self.part_data = part_data
        self.story_data = story_data

        self.en = StoryInfoPartSourceList(part_data.get("en", []), story_data.en)
        self.zh_tw = StoryInfoPartSourceList(part_data.get("zh_tw", []), story_data.zh_tw)
        self.zh_cn_cn = StoryInfoPartSourceList(part_data.get("zh_cn_cn", []), story_data.zh_cn_cn)
        self.zh_cn_jp = StoryInfoPartSourceList(part_data.get("zh_cn_jp", []), story_data.zh_cn_jp)

    def to_json(self):
        d = {}
        for i in self._component:
            d[i] = getattr(self, i).to_json()
        return d

    def to_json_basic(self):
        return self.to_json()
