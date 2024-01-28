from ..loader import FileLoader, i18n_translator, schale_db_manager
from ..types.metatype.base_type import Integer, String, Bool
from ..types.url import UrlModel
from .track import TrackListManager, TrackInfo
from ..tool.parent_data import IParentData
from ..tool.interpage import InterpageMixin


class BaseBattleInfo(FileLoader, IParentData):
    def parent_data_to_json(self):
        if self.parent_data is None:
            return self.parent_data
        else:
            return [self.export_parents_to_json(self.unpack_parents(self.parent_data, False)[0])]

    @classmethod
    def get_instance(cls, instance_id):
        return cls._instance[instance_id]


class MainBattleInfo(BaseBattleInfo, InterpageMixin):
    chapter = Integer('chapter')
    no = String('no')
    is_hard = Bool('is_hard')
    is_normal = Bool('is_normal')
    is_sub = Bool('is_sub')
    _instance = {}

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
            "interpage": self.get_interpage_data(),

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
            "interpage": self.get_interpage_data(),
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)

    def _get_instance_offset(self, offset: int):
        battle_list = list(self._instance.keys())
        current_index = battle_list.index(self.instance_id)

        if current_index == 0 and offset < 0:
            return None

        try:
            return self._instance[battle_list[current_index + offset]]
        except IndexError:
            return None

    def get_mixed_interpage_data(self, prev, next):
        def get_chapter(obj):
            try:
                return obj.chapter
            except AttributeError:
                return "[NO_PREV]"

        return {
            "prev": {
                "name": prev.name.to_json_basic() if prev else "[NO_PREV]",
                "namespace": prev.namespace if prev else "[NO_PREV]",
                "chapter": get_chapter(prev),
                "no": prev.no if prev else "[NO_PREV]"
            },
            "next": {
                "name": next.name.to_json_basic() if next else "[NO_NEXT]",
                "namespace": next.namespace if next else "[NO_NEXT]",
                "chapter": get_chapter(next),
                "no": next.no if next else "[NO_NEXT]"
            }
        }


class SchoolExchangeInfo(BaseBattleInfo):
    _instance = {}

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
            "id": self.data["id"].lower(),
            "namespace": self.namespace,

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return self.to_json()

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class TotalAssaultInfo(BaseBattleInfo):
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]

        self.image = UrlModel()
        self.image.load(data["image"])
        self.track = TrackListManager()

        self.faction_ori = schale_db_manager.query_constant("raids", data["name"], "Faction")
        self.faction = schale_db_manager.query("localization", "BossFaction_" + self.faction_ori)

        self.name_ori = schale_db_manager.query_constant("raids", data["name"], "PathName")
        self.name = schale_db_manager.query("raids", data["name"], "Name")
        self.profile = schale_db_manager.query("raids", data["name"], "Profile")

        self.track.load(data["track"])

        self.extra_register()

    def extra_register(self):
        for i in self.track.track:
            i.register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        return "BOSS_" + data["name"].upper()

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "id": self.data["name"].lower(),
            "namespace": self.namespace,

            "name": self.name.to_json_basic(),
            "name_ori": self.name_ori,
            "faction": self.faction.to_json_basic(),
            "faction_ori": self.faction_ori,

            "profile": self.profile.to_json_basic(),
            "track": self.track.to_json_basic(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "id": self.data["name"].lower(),

            "name": self.name.to_json_basic(),
            "faction": self.faction.to_json_basic(),
            "profile": self.profile.to_json_basic(),
            "track": self.track.to_json_basic(),
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class SpecialCommissionInfo(BaseBattleInfo):
    _instance = {}

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
            "id": self.data["id"].lower(),
            "namespace": self.namespace,

            "name": self.name.to_json_basic(),
            "name_ori": self.name_ori,
            "track": self.track.to_json_basic(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "id": self.data["id"].lower(),
            "namespace": self.namespace,

            "name": self.name.to_json_basic(),
            "track": self.track.to_json_basic(),
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class BountyHuntInfo(BaseBattleInfo):
    _instance = {}

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
            "id": self.data["id"].lower(),
            "namespace": self.namespace,

            "name": self.name.to_json_basic(),
            "name_ori": self.name_ori,
            "track": self.track.to_json_basic(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "id": self.data["id"].lower(),
            "namespace": self.namespace,

            "name": self.name.to_json_basic(),
            "track": self.track.to_json_basic(),
        }

    @classmethod
    def get_instance(cls, instance_id):
        return super().get_instance(instance_id)


class EventBattleInfo(MainBattleInfo):
    _instance = {}
    event_id = Integer('event_id')

    def __init__(self, **kwargs):
        FileLoader.__init__(self, data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]

        self.name = i18n_translator.query(data["name"])
        self.event_id = data["event_id"]
        self.no = data["no"]
        self.is_hard = data["is_hard"]
        self.is_normal = data["is_normal"]
        self.is_sub = data["is_sub"]

        self.track = TrackListManager()
        self.track.load(data["track"])

        self.extra_register()

    @staticmethod
    def _get_instance_id(data: dict):
        return "EVENT_" + "_".join([str(data["event_id"]), data["no"]])

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "event_id": self.event_id,
            "no": self.no,
            "is_hard": self.is_hard,
            "is_normal": self.is_normal,
            "is_sub": self.is_sub,
            "track": self.track.to_json_basic(),
            "interpage": self.get_interpage_data(),

            "parent_data": self.parent_data_to_json()
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "event_id": self.event_id,
            "no": self.no,
            "is_hard": self.is_hard,
            "is_normal": self.is_normal,
            "is_sub": self.is_sub,
            "interpage": self.get_interpage_data(),
            "parent_data": self.parent_data_to_json()
        }

    def _get_instance_offset(self, offset: int):
        battle_list = list(self._instance.keys())
        current_index = battle_list.index(self.instance_id)

        if current_index == 0 and offset < 0:
            return None

        try:
            result = self._instance[battle_list[current_index + offset]]
        except IndexError:
            return None
        else:
            if result.event_id != self.event_id:
                return None
            return result


class WorldRaidBattleInfo(BaseBattleInfo):
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])
        data = kwargs["data"]

        self.image = UrlModel()
        self.image.load(data["image"])
        self.track = TrackListManager()

        self.name_ori = schale_db_manager.query_constant("world_raids", data["name"], "PathName")
        self.name = schale_db_manager.query("world_raids", data["name"], "Name")

        self.track.load(data["track"])

        self.extra_register()

    def extra_register(self):
        for i in self.track.track:
            i.register(self)

    @staticmethod
    def _get_instance_id(data: dict):
        return "WORLDRAID_" + data["name"].upper()

    def to_json(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "id": self.data["name"].lower(),
            "namespace": self.namespace,

            "name": self.name.to_json_basic(),
            "name_ori": self.name_ori,

            "track": self.track.to_json_basic(),
            "parent_data": self.parent_data_to_json()
        }
        return d

    def to_json_basic(self):
        return self.to_json()
