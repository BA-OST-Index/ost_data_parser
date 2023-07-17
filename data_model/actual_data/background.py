from ..loader import FileLoader, i18n_translator
from .used_by import BaseUsedBy, OrderedDictWithCounter, UsedByToJsonMixin, UsedByRegisterMixin
from ..constant.file_type import FILETYPES_STORY, FILETYPES_TRACK
from ..types.metatype.base_model import BaseDataModelListManager
from ..types.url import UrlModel
from ..actual_data.tag import TagListManager


class BackgroundUsedBy(BaseUsedBy, UsedByToJsonMixin):
    # Copied from `character.py`
    # I did not merge simply because they're not even the same one, after all.
    # And by that said they are possible to be changed in the future independently.
    SUPPORTED_FILETYPE = [*FILETYPES_STORY, *FILETYPES_TRACK]

    def __init__(self):
        self.data_story = OrderedDictWithCounter()
        self.data_track = OrderedDictWithCounter()

    def register(self, file_loader: FileLoader):
        filetype = file_loader.filetype
        instance_id = file_loader.instance_id
        if filetype in self.SUPPORTED_FILETYPE:
            if filetype in FILETYPES_STORY:
                if instance_id not in self.data_story.keys():
                    self.data_story[instance_id] = file_loader
            elif filetype in FILETYPES_TRACK:
                if instance_id not in self.data_track.keys():
                    self.data_track[instance_id] = file_loader
        else:
            raise ValueError


class BackgroundInfo(FileLoader, UsedByRegisterMixin):
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

        self.extra_register()

    def extra_register(self):
        for tag in self.tag.tag:
            tag.register(self)

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
            "used_by": self.desc.to_json()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "filename": self.filename,

            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "image": self.image.to_json_basic()
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


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
