from ..loader import FileLoader, i18n_translator, schale_db_manager
from ..types.metatype.base_type import Integer, String, Bool
from ..types.url import UrlModel
from .track import TrackListManager, TrackInfo
from ..tool.parent_data import IParentData


class BaseBattleInfo(FileLoader, IParentData):
    _instance = {}

    def parent_data_to_json(self):
        if self.parent_data is None:
            return self.parent_data
        else:
            return self.export_parents_to_json(self.unpack_parents(self.parent_data, False)[0])

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class MainBattleInfo(BaseBattleInfo):
    chapter = Integer('chapter')
    no = String('no')
    is_hard = Bool('is_hard')
    is_normal = Bool('is_normal')
    is_sub = Bool('is_sub')

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]

        self.name = i18n_translator.query(data["name"])
        self.chapter = data["chapter"]
        self.no = data["no"]
        self.is_hard = data["is_hard"]
        self.is_normal = data["is_normal"]
        self.is_sub = data["is_sub"]

        self.track = TrackListManager()
        self.track.load(data["track"])

        self.extra_register()

    def extra_register(self):
        for track in self.track.track:
            track.register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        return "MAIN_" + "_".join([str(data["chapter"]), data["no"]])

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "chapter": self.chapter,
            "no": self.no,
            "is_hard": self.is_hard,
            "is_normal": self.is_normal,
            "is_sub": self.is_sub,
            "track": self.track.to_json_basic(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "chapter": self.chapter,
            "no": self.no,
            "is_hard": self.is_hard,
            "is_normal": self.is_normal,
            "is_sub": self.is_sub,
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class SchoolExchangeInfo(BaseBattleInfo):
    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]

        self.name = schale_db_manager.query("localization", data["name"])
        self.name_ori = data["name"]
        self.track = TrackInfo.get_instance(instance_id=data["track"])
        self.extra_register()

    def extra_register(self):
        self.track.register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        return "SCHOOL_" + data["id"].upper()

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "name_ori": self.name_ori,
            "track": self.track.to_json_basic(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return self.to_json()

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class TotalAssaultInfo(BaseBattleInfo):
    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]

        self.image = UrlModel()
        self.image.load(data["image"])
        self.track = TrackInfo.get_instance(instance_id=data["track"])

        self.faction_ori = schale_db_manager.query("raids", data["name"], "Faction")
        self.faction = schale_db_manager.query("localization", "BossFaction" + self.faction_ori)

        self.name_ori = schale_db_manager.query("raids", data["name"], "PathName")
        self.name = schale_db_manager.query("raids", data["name"], "Name")
        self.profile = schale_db_manager.query("raids", data["name"], "Profile")

        self.extra_register()

    def extra_register(self):
        self.track.register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        return "BOSS_" + data["name"].upper()

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json_basic(),
            "name_ori": self.name_ori,
            "faction": self.faction.to_json_basic(),
            "faction_ori": self.faction_ori.to_json_basic(),

            "profile": self.profile.to_json_basic(),
            "track": self.track.to_json_basic(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json_basic(),
            "faction": self.faction.to_json_basic(),
            "profile": self.profile.to_json_basic(),
            "track": self.track.to_json_basic(),
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class SpecialCommissionInfo(BaseBattleInfo):
    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]

        self.name_ori = data["name"]
        self.name = schale_db_manager.query("localization", data["name"])

        self.track = TrackInfo.get_instance(instance_id=data["track"])
        self.extra_register()

    def extra_register(self):
        self.track.register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        return "SPECIAL_" + data["id"].upper()

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json_basic(),
            "name_ori": self.name_ori,
            "track": self.track.to_json_basic(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json_basic(),
            "track": self.track.to_json_basic(),
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class BountyHuntInfo(BaseBattleInfo):
    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]

        self.name_ori = data["name"]
        self.name = schale_db_manager.query("localization", data["name"])

        self.track = TrackInfo.get_instance(instance_id=data["track"])

        self.extra_register()

    def extra_register(self):
        self.track.register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        return "BOUNTY_" + data["id"].upper()

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json_basic(),
            "name_ori": self.name_ori,
            "track": self.track.to_json_basic(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,

            "name": self.name.to_json_basic(),
            "track": self.track.to_json_basic(),
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)
