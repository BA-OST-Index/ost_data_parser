from ..types.metatype.base_type import String
from ..loader import FileLoader, i18n_translator
from ..types.metatype.base_model import BaseDataModelListManager
from .used_by import BaseUsedBy, UsedByRegisterMixin, OrderedDictWithCounter, UsedByToJsonMixin
from ..constant.file_type import FILETYPES_TRACK, FILETYPES_BACKGROUND
from ..tool.interpage import InterpageMixin


class TagUsedBy(BaseUsedBy, UsedByToJsonMixin):
    SUPPORTED_FILETYPE = [*FILETYPES_TRACK, *FILETYPES_BACKGROUND]
    _components = ["data_track", "data_background"]

    def __init__(self):
        self.data_track = OrderedDictWithCounter()
        self.data_background = OrderedDictWithCounter()

    def register(self, file_loader: FileLoader):
        filetype = file_loader.filetype
        instance_id = file_loader.instance_id
        if filetype in self.SUPPORTED_FILETYPE:
            if filetype in FILETYPES_TRACK:
                self.data_track[instance_id] = file_loader
            elif filetype in FILETYPES_BACKGROUND:
                self.data_background[instance_id] = file_loader
        else:
            raise ValueError


class TagInfo(FileLoader, UsedByRegisterMixin, InterpageMixin):
    _color_to_css = {"green": "success", "blue": "primary",
                     "red": "danger", "yellow": "warning",
                     "grey": "secondary"}
    _instance = {}

    color = String('color')
    color_css = String('color_css')

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        self.data = data = kwargs["data"]

        self.name = i18n_translator.query(data["name"])
        self.desc = i18n_translator.query(data["desc"])
        self.color = data["color"]
        self.color_css = self._color_to_css[self.color]

        self.used_by = TagUsedBy()

    @staticmethod
    def _get_instance_id(data: dict):
        return data["name"].split("_")[1].lower()

    def to_json(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json(),
            "desc": self.desc.to_json(),
            "namespace": self.namespace,
            "color": self.color,
            "color_css": self.color_css,
            "used_by": self.used_by.to_json(),
            "interpage": self.get_interpage_data()
        }
        return d

    def to_json_basic(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json(),
            "desc": self.desc.to_json(),
            "namespace": self.namespace,
            "color": self.color,
            "color_css": self.color_css,
            "interpage": self.get_interpage_data()
        }
        return d

    def _get_instance_offset(self, offset: int):
        keys = list(self._instance.keys())
        curr_index = keys.index(self.instance_id)

        try:
            if curr_index == 0 and offset < 0:
                return None
            return self._instance[keys[curr_index + offset]]
        except (IndexError, KeyError):
            return None


class TagListManager(BaseDataModelListManager):
    def __init__(self):
        super().__init__("tag")
        self.tag = []

    def load(self, data: list):
        super().load(data)
        for i in data:
            self.tag.append(TagInfo.get_instance(instance_id=i))

    def to_json(self):
        l = [i.to_json_basic() for i in self.tag]
        return l

    def to_json_basic(self):
        return self.to_json()
