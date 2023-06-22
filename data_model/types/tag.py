from .metatype.basic import BasicModel, String, MultipleBasicModelList
from .lang_string import LangStringModel
from ..loader.constant import constant_manager


class TagModel(BasicModel):
    ALL_TAGS = {}
    tag_id = String('tag_id')
    color = String('color')

    def __new__(cls, *args, **kwargs):
        tag_id = kwargs.get("tag_id")
        if str(int(tag_id)) in cls.ALL_TAGS.keys():
            return cls.ALL_TAGS.get(tag_id)

        instance = super().__new__(cls)
        return instance

    def __init__(self, *, tag_id: int):
        super().__init__(None)
        self.ALL_TAGS[str(tag_id)] = self
        self.tag_name = constant_manager.query("tag", tag_id)
        self.tag_id = str(tag_id)

        self.tag_name.key_name = "tag_name"

    def load(self, data):
        raise NotImplemented("Data is automatically loaded.")

    def to_json(self):
        return None, self.tag_name.to_json()[1]

    def to_json_basic(self):
        return self.to_json()[1]


class MultipleTagModelList(MultipleBasicModelList):
    def __init__(self, key_name):
        super().__init__(key_name, TagModel)

