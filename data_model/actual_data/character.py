from ..loader import FileLoader, schale_db_manager, i18n_translator
from .used_by import BaseUsedBy, OrderedDictWithCounter, UsedByToJsonMixin, UsedByRegisterMixin
from .related_to import BaseRelatedTo, RelatedToJsonMixin, RelatedToRegisterMixin
from ..constant.file_type import FILETYPES_STORY, FILETYPES_TRACK, FILE_STORY_EVENT, FILE_BATTLE_EVENT, \
    FILETYPES_CHARACTER, FILETYPES_BACKGROUND, FILE_BACKGROUND_INFO
from ..types.metatype.base_model import BaseDataModelListManager
from ..types.url import UrlModel
from ..tool.interpage import InterpageMixin
from ..tool.tool import counter_dict_sorter, PostExecutionManager


class CharacterRelatedTo(BaseRelatedTo, RelatedToJsonMixin):
    SUPPORTED_FILETYPE = [*FILETYPES_CHARACTER]
    BLANK_DATA = {"character_variant": [], "character_other": []}
    _components = ["character_variant", "character_other"]

    def __init__(self, character_obj, related_to_data: dict):
        self.character_variant = {}
        self.character_other = {}
        self.character_obj = character_obj
        self.data = related_to_data
        PostExecutionManager.add_to_pool(self.auto_register, pool_name="related_to")

    def auto_register(self):
        for i in self._components:
            for j in self.data[i]:
                try:
                    file_loader = eval(f"StudentInfo.get_instance('{j}')")
                except ValueError:
                    try:
                        file_loader = eval(f"NpcInfo.get_instance('{j}')")
                    except ValueError:
                        raise

                file_loader.register_related_to(self.character_obj, i)

    def register(self, file_loader: FileLoader, related_to_keyname: str, auto_register: bool = False):
        filetype = file_loader.filetype
        instance_id = file_loader.instance_id

        if filetype in self.SUPPORTED_FILETYPE:
            getattr(self, related_to_keyname)[instance_id] = file_loader
        else:
            raise ValueError

        if not auto_register:
            file_loader.register_related_to(self.character_obj, related_to_keyname, True)


class CharacterUsedBy(BaseUsedBy, UsedByToJsonMixin):
    SUPPORTED_FILETYPE = [*FILETYPES_STORY, *FILETYPES_TRACK, *FILETYPES_BACKGROUND, *FILETYPES_CHARACTER,
                          FILE_STORY_EVENT]
    _components = ["data_story", "data_track", "data_background", "data_background_direct", "data_character"]

    def __init__(self):
        self.data_story = OrderedDictWithCounter()
        self.data_track = OrderedDictWithCounter()
        self.data_background = OrderedDictWithCounter()
        self.data_background_direct = OrderedDictWithCounter()
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
            elif filetype in FILETYPES_BACKGROUND:
                if filetype == FILE_BACKGROUND_INFO:
                    self.data_background[instance_id] = file_loader
                    if not count_increase:
                        self.data_background.counter_adjust(instance_id, -1)
                else:
                    self.data_background_direct[instance_id] = file_loader
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
        d["data_background_direct"] = counter_dict_sorter(self.data_background_direct.get_counter_with_data_sorted_by_counter(),
                                                          ["filename"])
        d["data_character"] = counter_dict_sorter(self.data_character.get_counter_with_data_sorted_by_counter(),
                                                  [["name", "path_name"], ["name", "en"]])
        return d


class CharacterInfo(FileLoader, InterpageMixin, UsedByRegisterMixin, RelatedToRegisterMixin):
    _instance = {}

    @classmethod
    def get_instance(cls, instance_id):
        instance_id = instance_id.upper()
        try:
            # If it's a student
            temp = super().get_instance(instance_id="STU_" + instance_id)
        except Exception:
            try:
                # Otherwise it must be an NPC
                temp = super().get_instance(instance_id="NPC_" + instance_id)
            except Exception:
                raise
            else:
                return temp
        else:
            return temp

    def _get_instance_offset(self, offset: int):
        keys = list(self._instance.keys())
        curr_index = keys.index(self.instance_id)

        try:
            if curr_index == 0 and offset < 0:
                raise ValueError
            target = self._instance[keys[curr_index + offset]]
        except (ValueError, IndexError):
            return None

        if target.instance_id.split("_")[0] != self.instance_id.split("_")[0]:
            # Do not inter-index NPCs and Students!
            return None
        return target


class NpcInfo(CharacterInfo):
    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])

        self.name = i18n_translator.query(self.data["name"])
        self.desc = i18n_translator.query(self.data["desc"])
        self.image = UrlModel()
        self.image.load(self.data["image"])
        if "related_to" in self.data.keys():
            self.related_to = CharacterRelatedTo(self, self.data["related_to"])
        else:
            self.related_to = CharacterRelatedTo(self, CharacterRelatedTo.BLANK_DATA)

        self.used_by = CharacterUsedBy()

    def to_json(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "namespace": self.namespace,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "image": self.image.to_json_basic(),
            "used_by": self.used_by.to_json_basic(),
            "related_to": self.related_to.to_json_basic(),
            "interpage": self.get_interpage_data()
        }
        return d

    def to_json_basic(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "namespace": self.namespace,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "image": self.image.to_json_basic(),
            "interpage": self.get_interpage_data()
        }
        return d

    @staticmethod
    def _get_instance_id(data: dict):
        return "NPC_" + data["namespace"].upper()

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class StudentInfo(CharacterInfo):
    def __init__(self, **kwargs):
        # Do not add super() here as the `data` is only a string instead of a dict
        self.data = kwargs["data"]
        self.char_name = kwargs["data"]["name"]
        self.namespace = kwargs["namespace"]
        self.filetype = 51

        self.path_name = schale_db_manager.query_constant("students", self.char_name, "PathName")
        self.dev_name = schale_db_manager.query_constant("students", self.char_name, "DevName")
        self.family_name = schale_db_manager.query("students", self.char_name, "FamilyName")
        self.personal_name = schale_db_manager.query("students", self.char_name, "PersonalName")
        self.name = schale_db_manager.query("students", self.char_name, "Name")
        self.school_year = schale_db_manager.query("students", self.char_name, "SchoolYear")
        self.age = schale_db_manager.query("students", self.char_name, "CharacterAge")
        self.birthday = schale_db_manager.query("students", self.char_name, "BirthDay")
        self.birthday_localized = schale_db_manager.query("students", self.char_name, "Birthday")
        self.profile = schale_db_manager.query("students", self.char_name, "ProfileIntroduction")
        self.profile_gacha = schale_db_manager.query("students", self.char_name, "CharacterSSRNew")
        self.hobby = schale_db_manager.query("students", self.char_name, "Hobby")
        self.school_id = schale_db_manager.query_constant("students", self.char_name, "School")
        self.school = schale_db_manager.query("localization",
                                              "School_" + schale_db_manager.query_constant("students", self.char_name,
                                                                                           "School"))
        self.school_long = schale_db_manager.query("localization",
                                                   "SchoolLong_" + schale_db_manager.query_constant("students",
                                                                                                    self.char_name,
                                                                                                    "School"))
        self.club = schale_db_manager.query("localization",
                                            "Club_" + schale_db_manager.query_constant("students", self.char_name,
                                                                                       "Club"))
        self.squad_type = schale_db_manager.query("localization",
                                                  "SquadType_" + schale_db_manager.query_constant("students",
                                                                                                  self.char_name,
                                                                                                  "SquadType"))
        self.attack_type = schale_db_manager.query("localization",
                                                   "BulletType_" + schale_db_manager.query_constant("students",
                                                                                                    self.char_name,
                                                                                                    "BulletType"))
        self.armor_type = schale_db_manager.query("localization",
                                                  "ArmorType_" + schale_db_manager.query_constant("students",
                                                                                                  self.char_name,
                                                                                                  "ArmorType"))
        self.collection_bg = schale_db_manager.query_constant("students", self.char_name, "CollectionBG")

        self._id = schale_db_manager.query_constant("students", self.char_name, "Id")
        self._squad_type = schale_db_manager.query_constant("students", self.char_name, "SquadType")
        self._attack_type = schale_db_manager.query_constant("students", self.char_name, "BulletType")
        self._armor_type = schale_db_manager.query_constant("students", self.char_name, "ArmorType")

        self.used_by = CharacterUsedBy()
        if "related_to" not in kwargs["data"].keys():
            self.related_to = CharacterRelatedTo(self, CharacterRelatedTo.BLANK_DATA)
        else:
            self.related_to = CharacterRelatedTo(self, kwargs["data"]["related_to"])

    @staticmethod
    def _get_instance_id(data: dict):
        return "STU_" + data["name"].upper()

    @property
    def uuid(self):
        """向前兼容"""
        return self.path_name

    def to_json(self):
        return {
            "uuid": self.uuid,
            "id": self._id,
            "name": {
                "path_name": self.path_name,
                "dev_name": self.dev_name,
                "family_name": self.family_name.to_json(),
                "personal_name": self.personal_name.to_json(),
                "name": self.name.to_json()
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
            "school_id": self.school_id,
            "club": self.club.to_json(),
            "age": self.age.to_json(),
            "hobby": self.hobby.to_json(),
            "used_by": self.used_by.to_json_basic(),
            "interpage": self.get_interpage_data(),
            "image": {
                "collection_bg": self.collection_bg,
                "collection_texture": str(self._id)  # deprecated by SchaleDB
            },
            "combatant_info": {
                "squad_type": {
                    "type": self._squad_type,
                    "lang": self.squad_type.to_json()
                },
                "attack_type": {
                    "type": self._attack_type,
                    "lang": self.attack_type.to_json()
                },
                "armor_type": {
                    "type": self._armor_type,
                    "lang": self.armor_type.to_json()
                }
            },
            "related_to": self.related_to.to_json_basic()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "id": self._id,
            "name": {
                "path_name": self.path_name,
                "dev_name": self.dev_name,
                "family_name": self.family_name.to_json(),
                "personal_name": self.personal_name.to_json(),
                "name": self.name.to_json()
            },
            "image": {
                "collection_bg": self.collection_bg,
                "collection_texture": str(self._id)  # deprecated by SchaleDB
            },
            "birthday": self.birthday.to_json_basic(),
            "school": self.school_long.to_json_basic(),
            "school_id": self.school_id,
            "club": self.club.to_json_basic(),
            "age": self.age.to_json_basic(),
            "hobby": self.hobby.to_json_basic(),
            "interpage": self.get_interpage_data(),
            "combatant_info": {
                "squad_type": {
                    "type": self._squad_type,
                    "lang": self.squad_type.to_json()
                },
                "attack_type": {
                    "type": self._attack_type,
                    "lang": self.attack_type.to_json()
                },
                "armor_type": {
                    "type": self._armor_type,
                    "lang": self.armor_type.to_json()
                }
            }
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)

    def get_mixed_interpage_data(self, prev, next):
        return {
            "prev": {
                "name": {
                    "path_name": prev.path_name if prev else "[NO_PREV]",
                    "dev_name": prev.dev_name if prev else "[NO_PREV]"
                },
                "namespace": prev.namespace if prev else "[NO_PREV]"
            },
            "next": {
                "name": {
                    "path_name": next.path_name if next else "[NO_NEXT]",
                    "dev_name": next.dev_name if next else "[NO_NEXT]"
                },
                "namespace": next.namespace if next else "[NO_NEXT]"
            }
        }


class CharacterListManager(BaseDataModelListManager):
    def __init__(self, key_name="character"):
        super().__init__(key_name)
        self.character = []
        self.leader_pos = 0

    def load(self, data: list):
        super().load(data)

        # 最后一项的编号为领队
        try:
            if data[-1].startswith("L"):
                self.leader_pos = int(data[-1][1:])
        except IndexError:
            # 未填写战斗人员信息
            pass

        for i in data:
            if i.startswith("L"):
                continue
            self.character.append(StudentInfo.get_instance(i))

    def to_json(self):
        t = [i.to_json_basic() for i in self.character]
        return t

    def to_json_basic(self):
        return self.to_json()
