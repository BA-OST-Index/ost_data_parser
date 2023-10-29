from .track import TrackInfo
from data_model.types.metatype.base_type import *
from data_model.types.metatype.complex import *
from ..loader import i18n_translator, FileLoader
from ..tool.interpage import InterpageMixin
from ..tool.to_json import IToJson


class AlbumTrackListManager(IToJson):
    def __init__(self, disc_num: int, album_obj):
        self.disc_num: int = disc_num
        self.album_obj = album_obj
        self.tracks = []

    @property
    def track_num(self) -> int:
        return sum([len(self.tracks[i]) for i in range(self.disc_num)])

    def load(self, data):
        for i in range(self.disc_num):
            self.tracks.append([])

            for j in data[i]:
                instance = TrackInfo.get_instance(j)
                self.tracks[i].append(instance)
                instance.album.append(self.album_obj)

    def to_json(self):
        temp = []
        for i in range(self.disc_num):
            temp.append([])

            for j in self.tracks[i]:
                temp[i].append(j.to_json_basic())
        return temp

    def to_json_basic(self):
        return self.to_json()


class AlbumInfo(FileLoader, InterpageMixin):
    release_date = Timestamp("release_date")
    disc_num = Integer('disc_num')
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])

        self.name = i18n_translator.query(self.data["name"])
        self.desc = i18n_translator.query(self.data["desc"])
        self.cover_img = self.data["cover_img"]
        self.release_date = self.data["release_date"]
        self.disc_num = self.data["disc_num"]
        self.album_id = self.data["album_id"]

        self.tracks = AlbumTrackListManager(self.disc_num, self)
        self.tracks.load(self.data["tracks"])

    @staticmethod
    def _get_instance_id(data):
        return "ALBUM_" + str(data["album_id"])

    def to_json(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "album_id": self.album_id,
            "name": self.name.to_json(),
            "desc": self.desc.to_json(),
            "cover_img": self.cover_img,
            "release_date": int(self.release_date.timestamp()),
            "release_date_format": self.release_date.strftime("%Y-%m-%d"),
            "disc_num": self.disc_num,

            "tracks": self.tracks.to_json_basic(),
            "track_num": self.tracks.track_num
        }

    def to_json_basic(self):
        return {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "album_id": self.album_id,
            "name": self.name.to_json(),
            "desc": self.desc.to_json(),
            "cover_img": self.cover_img,
            "release_date": int(self.release_date.timestamp()),
            "release_date_format": self.release_date.strftime("%Y-%m-%d"),
            "disc_num": self.disc_num,
            "track_num": self.tracks.track_num
        }

    def _get_instance_offset(self, offset: int):
        instance_keys = list(self._instance.keys())
        instance_pos = instance_keys.index(self.instance_id)

        if instance_pos == 0 and offset < 0:
            return None

        try:
            return self._instance[instance_keys[instance_pos + offset]]
        except (KeyError, IndexError):
            return None
