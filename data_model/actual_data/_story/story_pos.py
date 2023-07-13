import abc
from data_model.types.metatype.basic import *

__all__ = ["StoryPosBond", "StoryPosEvent", "StoryPosMainSideShortOther",
           "storyPosAuto"]


class StoryPos(BaseDataModel, abc.ABC):
    _components = []

    def __init__(self, key_name):
        super().__init__(key_name)

    @abc.abstractmethod
    def load(self, data):
        super().load(data)

    def get_all_pos(self):
        return [getattr(self, key) for key in self._components]

    def to_json(self):
        t = dict((key, getattr(self, key)) for key in self._components)
        return t

    def to_json_basic(self):
        return self.to_json()


class StoryPosMainSideShortOther(StoryPos):
    """
    A sub-class of StoryPos, designed for Main/Side/Short/Other Story
    due to their similarity in ordering (can be listed as `volume`,
    `chapter`, `segment` with a total of 3 parts.)
    """
    volume = Integer('volume')
    chapter = Integer('chapter')
    segment = Integer('segment')
    _components = ["volume", "chapter", "segment"]

    def __init__(self, key_name='pos'):
        super().__init__(key_name)

    def load(self, data):
        super().load(data)
        self.volume = self.data["volume"]
        self.chapter = self.data["chapter"]
        self.segment = self.data["segment"]


class StoryPosEvent(StoryPos):
    event_id = Integer('event_id')
    segment = Integer('segment')
    _components = ["event_id", "segment"]

    def __init__(self, key_name="pos"):
        super().__init__(key_name)

    def load(self, data):
        super().load(data)
        self.event_id = data["event_id"]
        self.segment = data["segment"]


class StoryPosBond(StoryPos):
    student = String('student')
    no = Integer('no')
    is_bond = Bool('is_bond')
    _components = ["student", "no"]

    def load(self, data):
        super().load(data)
        self.student = data["student"]
        self.no = data["no"]
        self.is_bond = data["is_bond"]


def storyPosAuto(data: dict, key_name: str = "pos"):
    keys = data.keys()
    if 'student' in keys:
        t = StoryPosBond(key_name)
        t.load(data)
    elif 'event_id' in keys:
        t = StoryPosEvent(key_name)
        t.load(data)
    elif 'volume' in keys:
        t = StoryPosMainSideShortOther(key_name)
        t.load(data)
    else:
        raise ValueError

    return t
