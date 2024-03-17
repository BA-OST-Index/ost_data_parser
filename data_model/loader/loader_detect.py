import abc
import json
import os.path
from ..constant.file_type import FILETYPES_TRACK, FILETYPES_TRACK_DIR, FILE_ALBUM, FILE_DIR_ALBUM_ALL, \
    FILE_TAG_INFO, FILE_DIR_TAG_ALL, \
    FILE_DIR_CHARACTER_ALL, FILE_DIR_CHARACTER_CATEGORY, FILE_DIR_STUDENT_SINGLE, FILE_DIR_STUDENT_BOND, \
    FILE_STORY_BOND, FILETYPES_STORY, FILETYPES_STORY_DIR, FILE_CHARACTER_INFO, \
    FILE_BACKGROUND_INFO, FILE_DIR_BACKGROUND_ALL, \
    FILE_UI_CHILD, FILE_UI_EVENT, FILETYPES_UI_DIR, \
    FILETYPES_BATTLE, FILETYPES_BATTLE_DIR, \
    FILE_BATTLE_MAIN, FILE_BATTLE_EVENT, FILE_BATTLE_ARENA, FILE_BATTLE_TOTAL_ASSAULT, FILE_BATTLE_BOUNTY_HUNT, \
    FILE_BATTLE_SCHOOL_EXCHANGE, FILE_BATTLE_SPECIAL_COMMISSION, FILE_BATTLE_WORLD_RAID, \
    FILE_VIDEO_INFO, FILE_DIR_VIDEO_ALL, \
    FILETYPES_EVENT_DIR, FILE_STORY_EVENT, \
    FILE_REFERENCE_DATA
from ..actual_data.track import TrackInfo
from ..actual_data.track_album import AlbumInfo
from .folder_loader import TrackFolder, TagFolder, CharacterLoader, BackgroundLoader, StoryLoader, UiLoader, \
    BattleLoader, VideoLoader, EventLoader, AlbumLoader
from ..actual_data.tag import TagInfo
from ..actual_data.story import storyinfo_dispatcher
from ..actual_data.background import BackgroundInfo
from ..actual_data.character import NpcInfo
from ..actual_data.ui import UiInfo, UiInfoEvent
from ..actual_data.battle import MainBattleInfo, SchoolExchangeInfo, TotalAssaultInfo, \
    SpecialCommissionInfo, BountyHuntInfo, EventBattleInfo, WorldRaidBattleInfo
from ..actual_data.video import VideoInfo
from ..actual_data.reference_data import ReferenceFile


# This implementation of State design pattern is achieved through `yield` and `yield from` expressions.
# It is mostly to avoid the messy and long call stack shown in PyCharm's debugger.
# A shoutout to Python Cookbook (3rd) and Fluent Python (2nd) as they all mentioned this special "yielding" feature.

class BaseLoaderDetect(abc.ABC):
    next_detect = None

    @staticmethod
    @abc.abstractmethod
    def detect(entry):
        raise NotImplementedError


class OtherLoaderDetect(BaseLoaderDetect):
    next_detect = None

    @staticmethod
    def detect(entry):
        if entry.filetype == FILE_REFERENCE_DATA:
            yield ReferenceFile(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)


class EventLoaderDetect(BaseLoaderDetect):
    next_detect = OtherLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype in FILETYPES_EVENT_DIR:
            yield EventLoader(namespace=entry.namespace, json_data=entry.data,
                              basepath=entry.filepath, parent_data=entry.parent_data)
        elif entry.filetype == FILE_BATTLE_EVENT:
            yield EventBattleInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype == FILE_STORY_EVENT:
            yield storyinfo_dispatcher(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        else:
            yield from EventLoaderDetect.next_detect.detect(entry)


class VideoLoaderDetect(BaseLoaderDetect):
    next_detect = EventLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype == FILE_VIDEO_INFO:
            yield VideoInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype == FILE_DIR_VIDEO_ALL:
            yield VideoLoader(namespace=entry.namespace, json_data=entry.data,
                              basepath=entry.filepath, parent_data=entry.parent_data)
        else:
            yield from VideoLoaderDetect.next_detect.detect(entry)


class BattleLoaderDetect(BaseLoaderDetect):
    next_detect = VideoLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype in FILETYPES_BATTLE_DIR:
            yield BattleLoader(namespace=entry.namespace, json_data=entry.data,
                               basepath=entry.filepath, parent_data=entry.parent_data)
        elif entry.filetype in FILETYPES_BATTLE:
            if entry.filetype == FILE_BATTLE_MAIN:
                yield MainBattleInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            elif entry.filetype == FILE_BATTLE_TOTAL_ASSAULT:
                yield TotalAssaultInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            elif entry.filetype == FILE_BATTLE_BOUNTY_HUNT:
                yield BountyHuntInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            elif entry.filetype == FILE_BATTLE_SCHOOL_EXCHANGE:
                yield SchoolExchangeInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            elif entry.filetype == FILE_BATTLE_SPECIAL_COMMISSION:
                yield SpecialCommissionInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            elif entry.filetype == FILE_BATTLE_WORLD_RAID:
                yield WorldRaidBattleInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            else:
                raise NotImplementedError
        else:
            yield from BattleLoaderDetect.next_detect.detect(entry)


class UiLoaderDetect(BaseLoaderDetect):
    next_detect = BattleLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype == FILE_UI_CHILD:
            yield UiInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype == FILE_UI_EVENT:
            yield UiInfoEvent(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype in FILETYPES_UI_DIR:
            yield UiLoader(namespace=entry.namespace, json_data=entry.data,
                           basepath=entry.filepath, parent_data=entry.parent_data)
        else:
            yield from UiLoaderDetect.next_detect.detect(entry)


class StoryLoaderDetect(BaseLoaderDetect):
    next_detect = UiLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype in FILETYPES_STORY:
            if entry.filetype == FILE_STORY_BOND:
                # just in case if something goes wrong
                bond = storyinfo_dispatcher(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
                bond.after_instantiate()
                yield bond

            # Normal
            yield storyinfo_dispatcher(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype in FILETYPES_STORY_DIR:
            yield StoryLoader(namespace=entry.namespace, json_data=entry.data,
                              basepath=entry.filepath, parent_data=entry.parent_data)
        else:
            yield from StoryLoaderDetect.next_detect.detect(entry)


class BackgroundLoaderDetect(BaseLoaderDetect):
    next_detect = StoryLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype == FILE_DIR_BACKGROUND_ALL:
            yield BackgroundLoader(namespace=entry.namespace, json_data=entry.data,
                                   basepath=entry.filepath, parent_data=entry.parent_data)
        elif entry.filetype == FILE_BACKGROUND_INFO:
            yield BackgroundInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        else:
            yield from BackgroundLoaderDetect.next_detect.detect(entry)


class CharacterLoaderDetect(BaseLoaderDetect):
    next_detect = BackgroundLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype in [FILE_DIR_CHARACTER_ALL, FILE_DIR_CHARACTER_CATEGORY, FILE_DIR_STUDENT_SINGLE,
                              FILE_DIR_STUDENT_BOND]:
            yield CharacterLoader(namespace=entry.namespace, json_data=entry.data,
                                  basepath=entry.filepath, parent_data=entry.parent_data)
        elif entry.filetype == FILE_STORY_BOND:
            bond = storyinfo_dispatcher(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            bond.after_instantiate()
            yield bond
        elif entry.filetype == FILE_CHARACTER_INFO:
            yield NpcInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        else:
            yield from CharacterLoaderDetect.next_detect.detect(entry)


class TagLoaderDetect(BaseLoaderDetect):
    next_detect = CharacterLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype == FILE_TAG_INFO:
            yield TagInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype == FILE_DIR_TAG_ALL:
            yield TagFolder(namespace=entry.namespace, json_data=entry.data,
                            basepath=entry.filepath, parent_data=entry.parent_data)
        else:
            yield from TagLoaderDetect.next_detect.detect(entry)


class TrackLoaderDetect(BaseLoaderDetect):
    next_detect = TagLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype in FILETYPES_TRACK:
            yield TrackInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype in FILETYPES_TRACK_DIR:
            yield TrackFolder(namespace=entry.namespace, json_data=entry.data,
                              basepath=entry.filepath, parent_data=entry.parent_data)
        elif entry.filetype == FILE_ALBUM:
            yield AlbumInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype == FILE_DIR_ALBUM_ALL:
            yield AlbumLoader(namespace=entry.namespace, json_data=entry.data,
                              basepath=entry.filepath, parent_data=entry.parent_data)
        else:
            yield from TrackLoaderDetect.next_detect.detect(entry)


class LoaderDetectEntry:
    def __init__(self, namespace: list, filepath: str, parent_data=None):
        self.namespace = namespace
        self.filepath = filepath
        self.filepath_type = 1 if os.path.isdir(self.filepath) else 0
        self.data = self.load_data()
        self.filetype = self.data["filetype"]
        self.parent_data = parent_data

    def load_data(self):
        if self.filepath_type == 0:
            filepath = self.filepath
        else:
            filepath = os.path.join(self.filepath, "_all.json")
        with open(filepath, mode="r", encoding="UTF-8") as file:
            return json.load(file)

    def detect(self):
        yield from TrackLoaderDetect.detect(self)


def get_loader_by_filepath(namespace: list, filepath: str, parent_data):
    return next(LoaderDetectEntry(namespace, filepath, parent_data).detect())
