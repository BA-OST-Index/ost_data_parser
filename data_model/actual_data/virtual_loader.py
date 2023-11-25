from ..loader._loader import VirtualLoader
from ..tool.tool import PostExecutionManager


class FolderLoaderAccesser:
    __slots__ = ["TAG", "TRACK", "BACKGROUND", "CHARACTER", "STORY", "BATTLE", "UI", "VIDEO", "EVENT", "ALBUM"]
    _instance = None

    def __init__(self, tag, track, background, character, story, battle, ui, video, event, album):
        self.TAG, self.TRACK, self.BACKGROUND, self.CHARACTER, self.STORY, self.BATTLE, self.UI, self.VIDEO, \
        self.EVENT, self.ALBUM = tag, track, background, character, story, battle, ui, video, event, album

        FolderLoaderAccesser._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("Initialize it first!")
        return cls._instance


class TrackStats(VirtualLoader):
    def __init__(self):
        VirtualLoader.__init__(self, "track_special_stats", "virtual/track_special_stats.html",
                               "virtual/track/track_special_stats.html")

    def load_data(self):
        # get accessor
        accessor: FolderLoaderAccesser = FolderLoaderAccesser.get_instance()
        track_folder = accessor.TRACK

        # extract (flatten) all tracks
        tracks = []
        for category in track_folder.including:
            category = category.loader

            sorted_tracks = sorted(category.including, key=lambda i: int(i[0][:-5]))
            for track in sorted_tracks:
                tracks.append(track.loader)

        # categorize tracks
        self.is_ost, self.is_story, self.is_battle, self.is_recollection, self.is_event = [], [], [], [], []
        for i in tracks:
            sc = i.special_case
            if sc.is_ost: self.is_ost.append(i)
            if sc.is_story: self.is_story.append(i)
            if sc.is_battle: self.is_battle.append(i)
            if sc.is_bond_memory: self.is_recollection.append(i)
            if sc.is_event: self.is_event.append(i)

    def to_json(self):
        d = super().to_json()
        data = {
            "counts": {
                "is_ost": len(self.is_ost),
                "is_story": len(self.is_story),
                "is_battle": len(self.is_battle),
                "is_bond": len(self.is_recollection),
                "is_event": len(self.is_event)
            },
            "instances": {
                "is_ost": [i.to_json_basic() for i in self.is_ost],
                "is_story": [i.to_json_basic() for i in self.is_story],
                "is_battle": [i.to_json_basic() for i in self.is_battle],
                "is_bond": [i.to_json_basic() for i in self.is_recollection],
                "is_event": [i.to_json_basic() for i in self.is_event],
            }
        }
        d["data"] = data
        return d
