from data_model.loader._loader import BaseLoader
from ..actual_data.track import TrackInfo


class TrackFolder(BaseLoader):
    def __init__(self, namespace: list, basepath):
        super().__init__(namespace, basepath)

    def process(self):
        for n, i in enumerate(self.including):
            if self.is_folder(i):
                self.including[n] = [i, TrackFolder(self.namespace, self.join_path(i))]
            else:
                self.including[n] = [i, TrackInfo(self.load_json(i))]
