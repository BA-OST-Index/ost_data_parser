import os
from data_model.loader._loader import FolderLoader
from ..actual_data.character import StudentInfo
from ..constant.file_type import FILE_DIR_EVENT_STORY, FILE_DIR_STUDENT_SINGLE
from data_model.types.url import UrlModel, UrlModelListManager


def battle_comparison(item):
    item = item[0]
    if item.endswith(".json"):
        item = item[:-5]
        try:
            no = int(item[1:])

            if no < 10:
                # for event missions (e.g. N1, N10); main mission will always greater than 10 (e.g. N10)
                return item[0] + "0" + str(no) + ".json"
            else:
                return item
        except (ValueError, TypeError):
            # for bounty and other stuff, anyway this is messy
            pass
    return item


class GenericFolder(FolderLoader):
    """Basically a class for implementing normal, generic folder loader, without being copypasta."""

    def __init__(self, namespace: list, basepath, json_data=None, parent_data=None):
        super().__init__(namespace, basepath, json_data, parent_data)

    def to_json(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "namespace": self.namespace,

            "include": [[i.name, i.loader.to_json_basic()] for i in self.including]
        }
        if self.parent_data_exist and self.parent_data_export:
            d["parent_data"] = self.export_parents_to_json()
        return d

    def to_json_basic(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "namespace": self.namespace,

            "include": []
        }
        for i in self.including:
            if i.loader.filetype > 0:
                continue
            d["include"].append([i.name, i.loader.to_json_basic()])

        if self.parent_data_exist and self.parent_data_export:
            d["parent_data"] = self.export_parents_to_json()
        return d


class TrackFolder(GenericFolder):
    def auto_include(self):
        temp = super().auto_include()
        temp.sort(key=self.sort_by_int)
        return temp

    def to_json(self):
        d = super().to_json()
        return d

    def to_json_basic(self):
        d = super().to_json_basic()
        return d


class TagFolder(GenericFolder):
    pass


class BackgroundLoader(GenericFolder):
    pass


class StoryLoader(GenericFolder):
    def __init__(self, namespace: list, basepath, json_data=None, parent_data=None):
        super().__init__(namespace, basepath, json_data, parent_data)
        self.image = UrlModel()
        self.image.load(self.data["image"])

    def to_json_basic(self):
        d = super().to_json_basic()
        d["image"] = self.image.to_json_basic()
        return d

    def to_json(self):
        d = super().to_json()
        d["image"] = self.image.to_json()
        return d


class UiLoader(GenericFolder):
    def __init__(self, namespace: list, basepath, json_data=None, parent_data=None):
        super().__init__(namespace, basepath, json_data, parent_data)

    def auto_include(self):
        temp = super().auto_include()
        temp.sort(key=self.sort_by_int)
        return temp


class BattleLoader(GenericFolder):
    def __init__(self, namespace: list, basepath, json_data=None, parent_data=None):
        super().__init__(namespace, basepath, json_data, parent_data)
        self.image = UrlModelListManager('image')
        try:
            self.image.load(self.data["image"])
        except KeyError:
            self.image.load(
                [{
                    "platform": -1,
                    "value": "",
                    "short_desc": ""
                },
                    {
                        "platform": -1,
                        "value": "",
                        "short_desc": ""
                    }]
            )

    def auto_include(self):
        including = super().auto_include()

        def sorter(obj: str):
            if obj.endswith(".json"):
                if obj.startswith("H"):
                    return "1" + obj
                return "0" + obj
            else:
                return obj.rjust(2, "0")

        including.sort(key=sorter)

        return including

    def to_json_basic(self):
        d = super().to_json_basic()
        d["image"] = self.image.to_json_basic()
        return d

    def to_json(self):
        d = super().to_json()
        d["image"] = self.image.to_json()
        return d


class VideoLoader(GenericFolder):
    def auto_include(self):
        temp = super().auto_include()
        temp.sort(key=self.sort_by_int)
        return temp


class EventLoader(GenericFolder):
    def __init__(self, namespace: list, basepath, json_data=None, parent_data=None):
        super().__init__(namespace, basepath, json_data, parent_data)
        if self.data["filetype"] == FILE_DIR_EVENT_STORY:
            self.image = UrlModel()
            self.image.load(self.data["image"])

    def to_json_basic(self):
        d = super().to_json_basic()
        if self.data["filetype"] == FILE_DIR_EVENT_STORY:
            d["image"] = self.image.to_json_basic()
        if self.namespace[-1].lower() == "battle":
            d["include"].sort(key=battle_comparison)
        return d

    def to_json(self):
        d = super().to_json()
        if self.data["filetype"] == FILE_DIR_EVENT_STORY:
            d["image"] = self.image.to_json()
        if self.namespace[-1].lower() == "battle":
            d["include"].sort(key=battle_comparison)
        return d


class CharacterLoader(FolderLoader):
    def __init__(self, namespace: list, basepath, json_data=None, parent_data=None):
        if json_data["filetype"] == FILE_DIR_STUDENT_SINGLE:
            new_namespace = list(namespace)
            if json_data["namespace"] == "":
                new_namespace.append(os.path.split(basepath)[-1])
            else:
                new_namespace.append(json_data["namespace"])
            self.student = StudentInfo(data=json_data, namespace=new_namespace, parent_data=None)
        super().__init__(namespace, basepath, json_data, parent_data)

    def to_json(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "namespace": self.namespace,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "include": [[i.name, i.loader.to_json_basic()] for i in self.including]
        }

        # If the filetype is FILE_DIR_STUDENT_SINGLE or something
        try:
            d["student"] = self.student.to_json()
        except Exception:
            pass
        return d

    def to_json_basic(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "namespace": self.namespace,
            "name": self.name.to_json_basic(),
            "desc": self.desc.to_json_basic(),
            "include": []
        }
        for i in self.including:
            if i.loader.filetype in [-54]:
                continue
            d["include"].append([i.name, i.loader.to_json_basic()])

        # If the filetype is FILE_DIR_STUDENT_SINGLE or something
        try:
            d["student"] = self.student.to_json_basic()
        except Exception:
            pass
        return d

    def auto_include(self):
        temp = super().auto_include()
        temp.sort(key=self.sort_by_int)
        return temp


class AlbumLoader(GenericFolder):
    def __init__(self, namespace: list, basepath, json_data=None, parent_data=None):
        super().__init__(namespace, basepath, json_data, parent_data)

    def auto_include(self):
        temp = super().auto_include()
        temp.sort(key=self.sort_by_int)
        return temp
