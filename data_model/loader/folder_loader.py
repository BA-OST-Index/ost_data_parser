import os
from data_model.loader._loader import FolderLoader
from ..actual_data.character import StudentInfo
from ..constant.file_type import FILE_DIR_STUDENT_BOND, FILE_DIR_STUDENT_SINGLE
from ._loader import IncludingInfo


class TrackFolder(FolderLoader):
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
        return self.to_json()


class TagFolder(FolderLoader):
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
        if self.parent_data_export:
            d["parent_data"] = self.export_parents_to_json()
        return d

    def to_json_basic(self):
        return self.to_json()


class CharacterLoader(FolderLoader):
    def __init__(self, namespace: list, basepath, json_data=None, parent_data=None):
        if json_data["filetype"] == FILE_DIR_STUDENT_SINGLE:
            new_namespace = list(namespace)
            if json_data["namespace"] == "":
                new_namespace.append(os.path.split(basepath)[-1])
            else:
                new_namespace.append(json_data["namespace"])
            self.student = StudentInfo(data=json_data["name"], namespace=new_namespace, parent_data=None)
        super().__init__(namespace, basepath, json_data, parent_data)

    def to_json(self):
        d = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "namespace": self.namespace,
            "name": self.data["name"],
            "include": [[i.name, i.loader.to_json_basic()] for i in self.including]
        }

        # If the filetype is FILE_DIR_STUDENT_SINGLE or something
        try:
            d["student"] = self.student.to_json_basic()
        except Exception:
            pass
        return d

    def to_json_basic(self):
        return self.to_json()


class BackgroundLoader(FolderLoader):
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
        if self.parent_data_export:
            d["parent_data"] = self.export_parents_to_json()
        return d

    def to_json_basic(self):
        return self.to_json()

class StoryLoader(FolderLoader):
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
        if self.parent_data_export:
            d["parent_data"] = self.export_parents_to_json()
        return d

    def to_json_basic(self):
        return self.to_json()

class UiLoader(FolderLoader):
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
        if self.parent_data_export:
            d["parent_data"] = self.export_parents_to_json()
        return d

    def to_json_basic(self):
        return self.to_json()

class BattleLoader(FolderLoader):
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
        if self.parent_data_export:
            d["parent_data"] = self.export_parents_to_json()
        return d

    def to_json_basic(self):
        return self.to_json()
