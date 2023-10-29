from data_model.loader import i18n_translator
from data_model.tool.to_json import IToJson
from data_model.constant.platform import BILIBILI, YOUTUBE


class StoryInfoPartVideo(IToJson):
    def __init__(self, data, story_obj):
        self.part_video = data
        self.story_video = story_obj.video




