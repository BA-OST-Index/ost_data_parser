from ..loader import FileLoader, i18n_translator
from .used_by import BaseUsedBy, OrderedDictWithCounter, UsedByToJsonMixin, UsedByRegisterMixin
from ..constant.file_type import (FILETYPES_STORY, FILETYPES_TRACK, FILE_STORY_EVENT, FILETYPES_CHARACTER,
                                  FILE_BACKGROUND_INFO_DIRECT)
from ..types.metatype.base_model import BaseDataModelListManager
from ..types.url import UrlModel
from ..actual_data.tag import TagListManager
from ..actual_data.character import CharacterListManager
from ..tool.interpage import InterpageMixin
from ..tool.tool import counter_dict_sorter, PostExecutionManager, ObjectAccessProxier


class BackgroundUsedBy(BaseUsedBy, UsedByToJsonMixin):
    # Copied from `character.py`
    # I did not merge simply because they're not even the same one, after all.
    # And by that said they are possible to be changed in the future independently.
    SUPPORTED_FILETYPE = [*FILETYPES_STORY, *FILETYPES_TRACK, FILE_STORY_EVENT, *FILETYPES_CHARACTER]
    _components = ["data_story", "data_track", "data_character"]

    def __init__(self):
        self.data_story = OrderedDictWithCounter()
        self.data_track = OrderedDictWithCounter()
        self.data_character = OrderedDictWithCounter()

    def register(self, file_loader: FileLoader, count_increase=True):
        filetype = file_loader.filetype
        instance_id = file_loader.instance_id

        if filetype in self.SUPPORTED_FILETYPE:
            if filetype in [*FILETYPES_STORY, FILE_STORY_EVENT]:
                self.data_story[instance_id] = file_loader
                if not count_increase:
                    self.data_story.counter_adjust(instance_id, -1)
            elif filetype in FILETYPES_TRACK:
                self.data_track[instance_id] = file_loader
                if not count_increase:
                    self.data_track.counter_adjust(instance_id, -1)
            elif filetype in FILETYPES_CHARACTER:
                self.data_character[instance_id] = file_loader
                if not count_increase:
                    self.data_character.counter_adjust(instance_id, -1)
        else:
            raise ValueError

    def to_json(self, no_used_by: bool = True):
        d = super().to_json()
        d["data_track"] = counter_dict_sorter(self.data_track.get_counter_with_data_sorted_by_counter(),
                                              ["track_type", "no"])
        d["data_character"] = counter_dict_sorter(self.data_character.get_counter_with_data_sorted_by_counter(),
                                                  ["filename"])
        return d


class BackgroundInfo(FileLoader, UsedByRegisterMixin, InterpageMixin):
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        self.filename = self.data["filename"]
        self.name = i18n_translator.query(self.data["name"])
        self.desc = i18n_translator.query(self.data["desc"])
        self.tag = TagListManager()
        self.tag.load(self.data["tag"])
        self.image = UrlModel()
        self.image.load(self.data["image"])

        self.used_by = BackgroundUsedBy()
        self.character = CharacterListManager()

        self.extra_register()
        PostExecutionManager.add_to_pool(self.character.load, self.data.get("character", []),
                                         pool_name="background_character_direct")
        PostExecutionManager.add_to_pool(self.register_character, pool_name="background_character_direct")

    def extra_register(self):
        for tag in self.tag.tag:
            tag.register(self)

    def register_character(self):
        for i in self.character.character:
            i.register(ObjectAccessProxier(self, {"filetype": FILE_BACKGROUND_INFO_DIRECT}))

    @staticmethod
    def _get_instance_id(data: dict):
        return data["filename"]

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "filename": self.filename,

            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "tag": self.tag.to_json_basic(),
            "image": self.image.to_json_basic(),
            "character": self.character.to_json_basic(),
            "used_by": self.used_by.to_json_basic(),
            "interpage": self.get_interpage_data()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "filename": self.filename,

            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "image": self.image.to_json_basic(),
            "character": self.character.to_json_basic(),
            "interpage": self.get_interpage_data()
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)

    def _get_instance_offset(self, offset: int):
        keys = list(self._instance.keys())
        curr_index = keys.index(self.instance_id)

        try:
            if curr_index == 0 and offset < 0:
                raise ValueError
            return self._instance[keys[curr_index + offset]]
        except (KeyError, ValueError, IndexError):
            return None


class BackgroundListManager(BaseDataModelListManager):
    def __init__(self):
        super().__init__("background")
        self.background = []

    def load(self, data: list):
        super().load(data)
        for i in data:
            self.background.append(BackgroundInfo.get_instance(instance_id=i))

    def to_json(self):
        t = [i.to_json_basic() for i in self.background]
        return t

    def to_json_basic(self):
        return self.to_json()
