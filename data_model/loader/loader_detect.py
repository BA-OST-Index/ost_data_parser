# TODO: automatically detect suitable loaders using "State" design pattern!

import abc
import json
import os.path
from ..constant.file_type import FILETYPES_TRACK, FILETYPES_TRACK_DIR, \
    FILE_TAG_INFO, FILE_DIR_TAG_ALL, \
    FILE_DIR_CHARACTER_ALL, FILE_DIR_CHARACTER_CATEGORY, FILE_DIR_STUDENT_SINGLE, FILE_DIR_STUDENT_BOND, \
    FILE_STORY_BOND, FILETYPES_STORY, FILETYPES_STORY_DIR, FILE_CHARACTER_INFO, \
    FILE_BACKGROUND_INFO, FILE_DIR_BACKGROUND_ALL, \
    FILETYPES_UI, FILETYPES_UI_DIR, \
    FILETYPES_BATTLE, FILETYPES_BATTLE_DIR, \
    FILE_BATTLE_MAIN, FILE_BATTLE_EVENT, FILE_BATTLE_ARENA, FILE_BATTLE_TOTAL_ASSAULT, FILE_BATTLE_BOUNTY_HUNT, \
    FILE_BATTLE_SCHOOL_EXCHANGE, FILE_BATTLE_SPECIAL_COMMISSION
from ..actual_data.track import TrackInfo
from .folder_loader import TrackFolder, TagFolder, CharacterLoader, BackgroundLoader, StoryLoader, UiLoader, \
    BattleLoader
from ..actual_data.tag import TagInfo
from ..actual_data.story import StoryInfoBond, StoryInfo
from ..actual_data.background import BackgroundInfo
from ..actual_data.character import NpcInfo
from ..actual_data.ui import UiInfo
from ..actual_data.battle import MainBattleInfo, SchoolExchangeInfo, TotalAssaultInfo, \
    SpecialCommissionInfo, BountyHuntInfo


class BaseLoaderDetect(abc.ABC):
    next_detect = None

    @staticmethod
    @abc.abstractmethod
    def detect(entry):
        raise NotImplementedError


class BattleLoaderDetect(BaseLoaderDetect):
    next_detect = None

    @staticmethod
    def detect(entry):
        if entry.filetype in FILETYPES_BATTLE_DIR:
            return BattleLoader(namespace=entry.namespace, json_data=entry.data,
                                basepath=entry.filepath, parent_data=entry.parent_data)
        elif entry.filetype in FILETYPES_BATTLE:
            if entry.filetype == FILE_BATTLE_MAIN:
                return MainBattleInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            elif entry.filetype == FILE_BATTLE_TOTAL_ASSAULT:
                return TotalAssaultInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            elif entry.filetype == FILE_BATTLE_BOUNTY_HUNT:
                return BountyHuntInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            elif entry.filetype == FILE_BATTLE_SCHOOL_EXCHANGE:
                return SchoolExchangeInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            elif entry.filetype == FILE_BATTLE_SPECIAL_COMMISSION:
                return SpecialCommissionInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError

class UiLoaderDetect(BaseLoaderDetect):
    next_detect = BattleLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype in FILETYPES_UI:
            return UiInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype in FILETYPES_UI_DIR:
            return UiLoader(namespace=entry.namespace, json_data=entry.data,
                            basepath=entry.filepath, parent_data=entry.parent_data)


class StoryLoaderDetect(BaseLoaderDetect):
    next_detect = UiLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype in FILETYPES_STORY:
            if entry.filetype == FILE_STORY_BOND:
                # just in case if something goes wrong
                bond = StoryInfoBond(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
                bond.after_instantiate()
                return bond

            # Normal
            return StoryInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype in FILETYPES_STORY_DIR:
            return StoryLoader(namespace=entry.namespace, json_data=entry.data,
                               basepath=entry.filepath, parent_data=entry.parent_data)
        else:
            return StoryLoaderDetect.next_detect.detect(entry)


class BackgroundLoaderDetect(BaseLoaderDetect):
    next_detect = StoryLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype == FILE_DIR_BACKGROUND_ALL:
            return BackgroundLoader(namespace=entry.namespace, json_data=entry.data,
                                    basepath=entry.filepath, parent_data=entry.parent_data)
        elif entry.filetype == FILE_BACKGROUND_INFO:
            return BackgroundInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        else:
            return BackgroundLoaderDetect.next_detect.detect(entry)


class CharacterLoaderDetect(BaseLoaderDetect):
    next_detect = BackgroundLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype in [FILE_DIR_CHARACTER_ALL, FILE_DIR_CHARACTER_CATEGORY, FILE_DIR_STUDENT_SINGLE,
                              FILE_DIR_STUDENT_BOND]:
            return CharacterLoader(namespace=entry.namespace, json_data=entry.data,
                                   basepath=entry.filepath, parent_data=entry.parent_data)
        elif entry.filetype == FILE_STORY_BOND:
            bond = StoryInfoBond(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
            bond.after_instantiate()
            return bond
        elif entry.filetype == FILE_CHARACTER_INFO:
            return NpcInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        else:
            return CharacterLoaderDetect.next_detect.detect(entry)


class TagLoaderDetect(BaseLoaderDetect):
    next_detect = CharacterLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype == FILE_TAG_INFO:
            return TagInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype == FILE_DIR_TAG_ALL:
            return TagFolder(namespace=entry.namespace, json_data=entry.data,
                             basepath=entry.filepath, parent_data=entry.parent_data)
        else:
            return TagLoaderDetect.next_detect.detect(entry)


class TrackLoaderDetect(BaseLoaderDetect):
    next_detect = TagLoaderDetect

    @staticmethod
    def detect(entry):
        if entry.filetype in FILETYPES_TRACK:
            return TrackInfo(data=entry.data, namespace=entry.namespace, parent_data=entry.parent_data)
        elif entry.filetype in FILETYPES_TRACK_DIR:
            return TrackFolder(namespace=entry.namespace, json_data=entry.data,
                               basepath=entry.filepath, parent_data=entry.parent_data)
        else:
            return TrackLoaderDetect.next_detect.detect(entry)


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
        return TrackLoaderDetect.detect(self)


def get_loader_by_filepath(namespace: list, filepath: str, parent_data):
    return LoaderDetectEntry(namespace, filepath, parent_data).detect()
