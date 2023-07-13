from data_model.types.metatype.basic import *
from data_model.types.metatype.complex import *
from data_model.actual_data._story.story_pos import *
from data_model.loader import i18n_translator, constant_manager
from data_model.actual_data.track import TrackInfo, TrackListManager
from data_model.types.lang_string import MultipleLangStringModelList


class StoryInfo(IToJson):
    uuid = UUID('uuid')
    file_type = Integer('file_type')
    is_battle = bool('is_battle')

    def __init__(self, data: dict, key_name: str = None):
        self.key_name = key_name
        self.data = data

        self.uuid = data["uuid"]
        self.file_type = data["file_type"]
        self.is_battle = data["is_battle"]

        self.name = i18n_translator[data["name"]]
        self.pos = storyPosAuto(data["pos"])
        self.track = TrackListManager('track')
        self.track.load(data["track"])

        # Special case: some stories still have content after the battle,
        # and in that case, there will be two description text.
        # The code here can handle either single string or a list with strings,
        # and it will normalize into a list with LangStringModel in both cases.
        self.desc = MultipleLangStringModelList('desc')
        if isinstance(data["desc"], str):
            self.desc.append(i18n_translator[data["desc"]])
        else:
            for i in data["desc"]: self.desc.append(i18n_translator[i])

    def get_unique_id(self, is_joined: bool = True):
        if is_joined:
            return ",".join([str(i) for i in self.pos.get_all_pos()])
        return [str(i) for i in self.pos.get_all_pos()]

    def to_json(self):
        t = {
            "uuid": self.uuid,
            "file_type": self.file_type,

            "name": self.name.to_json()[-1],
            "desc": [i[-1] for i in self.desc.to_json()[-1]],
            "pos": self.pos.to_json()[-1],
            "image": self.data["image"],

            "track": self.track.to_json_basic(),
            "is_battle": self.is_battle
        }
        return t

    def to_json_basic(self):
        return self.to_json()


class StoryInfoBond(StoryInfo):
    def get_unique_id(self, is_joined: bool = True):
        if is_joined:
            t = ",".join([str(i) for i in self.pos.get_all_pos()])
            if self.pos.is_bond:
                return t + ",1"
            return t + ",0"

        t = [str(i) for i in self.pos.get_all_pos()]
        t.append("1" if self.pos.is_bond else "0")
        return t
