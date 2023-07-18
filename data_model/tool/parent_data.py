import abc
from collections import namedtuple

ParentData = namedtuple("ParentData", ["name", "desc", "namespace", "path", "extra_data", "last_parent"])


class ParentDataTool:
    @staticmethod
    def unpack_parents(data: ParentData, latest_fist: bool = True) -> [ParentData, ...]:
        parents = []
        current_parent = data
        while True:
            parents.append(current_parent)
            if current_parent.last_parent:
                current_parent = current_parent.last_parent
            else:
                break

        if not latest_fist:
            parents.reverse()
        return parents

    @staticmethod
    def export_parents_to_json(data: ParentData) -> dict:
        parents = ParentDataTool.unpack_parents(data=data)
        d = {}
        current_dict = d

        for num, data in enumerate(parents):
            current_dict["name"] = data.name.to_json()
            current_dict["desc"] = data.desc.to_json()
            current_dict["namespace"] = data.namespace
            current_dict["path"] = data.path
            current_dict["extra_data"] = data.extra_data
            if data.last_parent:
                current_dict["last_parent"] = {}
                current_dict = current_dict["last_parent"]

        return d


class ParentDataMixin(abc.ABC):
    def load_parent_data(self):
        if self.parent_data_exist:
            if self.parent_data_enable:
                self.parent_data_extra = self.data["parent_data"]["extra_data"]
                self.parent_data_export = self.data["parent_data"]["enable_export"]

        # Load the current ParentData
        self.parent_data = ParentData(self.name, self.desc, self.namespace, self.get_path(),
                                      self.parent_data_extra, last_parent=self._parent_data)

    @property
    def parent_data_exist(self):
        return "parent_data" in self.data.keys()

    @property
    def parent_data_enable(self):
        return self.data["parent_data"]["enable"]

    def export_parents_to_json(self):
        return ParentDataTool.export_parents_to_json(self.parent_data)


class IParentData:
    @staticmethod
    def unpack_parents(data: ParentData, latest_fist: bool = True):
        return ParentDataTool.unpack_parents(data, latest_fist)

    @staticmethod
    def export_parents_to_json(data: ParentData):
        return ParentDataTool.export_parents_to_json(data)

    def parent_data_to_json(self):
        if self.parent_data is None:
            return self.parent_data
        else:
            return self.export_parents_to_json(self.unpack_parents(self.parent_data, False)[0])
