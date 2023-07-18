from ..loader import FileLoader, schale_db_manager, i18n_translator
from .used_by import BaseUsedBy, OrderedDictWithCounter, UsedByToJsonMixin, UsedByRegisterMixin
from ..constant.file_type import FILETYPES_STORY, FILETYPES_TRACK, FILE_STORY_EVENT, FILE_BATTLE_EVENT
from ..types.metatype.base_model import BaseDataModelListManager
from ..types.url import UrlModel


class CharacterUsedBy(BaseUsedBy, UsedByToJsonMixin):
    SUPPORTED_FILETYPE = [*FILETYPES_STORY, *FILETYPES_TRACK, FILE_STORY_EVENT, FILE_BATTLE_EVENT]

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


class CharacterInfo(FileLoader):
    _instance = {}

    @classmethod
    def get_instance(cls, instance_id):
        instance_id = instance_id.upper()
        try:
            # If it's a student
            temp = super().get_instance(instance_id="STU_"+instance_id)
        except Exception:
            try:
                # Otherwise it must be an NPC
                temp = super().get_instance(instance_id="NPC_"+instance_id)
            except Exception:
                raise
            else:
                return temp
        else:
            return temp


class NpcInfo(CharacterInfo, UsedByRegisterMixin):
    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])

        self.name = i18n_translator.query(self.data["name"])
        self.desc = i18n_translator.query(self.data["desc"])
        self.image = UrlModel()
        self.image.load(self.data["image"])

        self.used_by = CharacterUsedBy()

    def to_json(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "namespace": self.namespace,
            "name": self.name.to_json_basic(),
            "desc": self.name.to_json_basic(),
            "image": self.image.to_json_basic()
        }
        return d

    def to_json_basic(self):
        return self.to_json()

    @staticmethod
    def _get_instance_id(data: dict):
        return "NPC_" + data["namespace"].upper()

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class StudentInfo(CharacterInfo, UsedByRegisterMixin):
    def __init__(self, **kwargs):
        # Do not add super() here as the `data` is only a string instead of a dict
        self.data = kwargs["data"]
        self.namespace = kwargs["namespace"]

        self.path_name = schale_db_manager.query("students", self.data, "PathName")
        self.family_name = schale_db_manager.query("students", self.data, "FamilyName")
        self.personal_name = schale_db_manager.query("students", self.data, "PersonalName")
        self.school_year = schale_db_manager.query("students", self.data, "SchoolYear")
        self.age = schale_db_manager.query("students", self.data, "CharacterAge")
        self.birthday = schale_db_manager.query("students", self.data, "BirthDay")
        self.birthday_localized = schale_db_manager.query("students", self.data, "Birthday")
        self.profile = schale_db_manager.query("students", self.data, "ProfileIntroduction")
        self.profile_gacha = schale_db_manager.query("students", self.data, "CharacterSSRNew")
        self.hobby = schale_db_manager.query("students", self.data, "Hobby")
        self.school = schale_db_manager.query("localization",
                                              "School_" + schale_db_manager.query_constant("students", self.data,
                                                                                           "School"))
        self.school_long = schale_db_manager.query("localization",
                                                   "SchoolLong_" + schale_db_manager.query_constant("students",
                                                                                                    self.data,
                                                                                                    "School"))
        self.club = schale_db_manager.query("localization",
                                            "Club_" + schale_db_manager.query_constant("students", self.data, "Club"))

        self.used_by = CharacterUsedBy()

    @staticmethod
    def _get_instance_id(data: str):
        return "STU_" + data.upper()

    def to_json(self):
        return {
            "name": {
                "path_name": self.path_name.to_json(),
                "family_name": self.family_name.to_json(),
                "personal_name": self.personal_name.to_json(),
            },
            "birthday": {
                "localized": self.birthday_localized.to_json(),
                "normalized": self.birthday.to_json()
            },
            "profile": {
                "profile": self.profile.to_json(),
                "gacha": self.profile_gacha.to_json()
            },
            "school": {
                "short": self.school.to_json(),
                "long": self.school_long.to_json()
            },
            "club": self.club.to_json(),
            "age": self.age,
            "hobby": self.hobby.to_json()
        }

    def to_json_basic(self):
        return {
            "name": {
                "path_name": self.path_name.to_json_basic(),
            },
            "birthday": self.birthday.to_json_basic(),
            "school": self.school_long.to_json_basic(),
            "club": self.club.to_json_basic(),
            "age": self.age.to_json_basic(),
            "hobby": self.hobby.to_json_basic()
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class CharacterListManager(BaseDataModelListManager):
    def __init__(self, key_name="character"):
        super().__init__(key_name)
        self.character = []

    def load(self, data: list):
        super().load(data)
        for i in data:
            self.character.append(StudentInfo.get_instance(i))

    def to_json(self):
        t = [i.to_json_basic() for i in self.character]
        return t

    def to_json_basic(self):
        return self.to_json()
