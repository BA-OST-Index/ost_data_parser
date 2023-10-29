import hashlib
from ..loader import FileLoader
from ..tool.parent_data import IParentData
from ..tool.interpage import InterpageMixin
from ..tool.tool import PostExecutionManager, uuid_crafter


class ReferenceData:
    """单独用来处理引用数据的类"""

    def __init__(self, module_name, model_name, instance_id):
        self._module_name = module_name
        self._model_name = model_name
        self._instance_id = instance_id

        self._ref_instance = None
        PostExecutionManager.add_to_pool(self.load_data, pool_name="reference_data")

    def load_data(self):
        data_model = __import__(self._module_name)
        self._ref_instance = eval(self._module_name + "." + self._model_name + f".get_instance('{self._instance_id}')")

    def to_json(self):
        self.check_data_loaded()
        return self._ref_instance.to_json()

    def to_json_basic(self):
        self.check_data_loaded()
        return self._ref_instance.to_json_basic()

    def is_data_loaded(self):
        return not (self._ref_instance is None)

    def check_data_loaded(self):
        if not self.is_data_loaded():
            raise RuntimeError


class ReferenceFile(FileLoader, InterpageMixin, IParentData):
    _instance = {}

    def __init__(self, **kwargs):
        super().__init__(data=kwargs["data"], namespace=kwargs["namespace"], parent_data=kwargs["parent_data"])

        self.uuid = self.data["uuid"]
        self.filetype = self.data["filetype"]
        self._module_name = self.data["module_name"]
        self._model_name = self.data["model_name"]
        self._instance_id = self.data["instance_id"]
        self.interpage = self.data.get("interpage", {})

        self._ref_instance = ReferenceData(self._module_name, self._model_name, self._instance_id)
        self._interpage_register()

        self._instance[self.uuid] = self

    @staticmethod
    def _get_instance_id(data):
        uuid = data["uuid"]
        return uuid

    def _interpage_register(self):
        try:
            prev = self.interpage["prev"]
            self._interpage_prev = ReferenceData(prev["module_name"], prev["model_name"], prev["instance_id"])
        except KeyError:
            self._interpage_prev = None

        try:
            next = self.interpage["next"]
            self._interpage_next = ReferenceData(next["module_name"], next["model_name"], next["instance_id"])
        except KeyError:
            self._interpage_next = None

    def interpage_prev(self):
        self._interpage_prev.check_data_loaded()
        return self._interpage_prev

    def interpage_next(self):
        self._interpage_next.check_data_loaded()
        return self._interpage_next

    def _json_post_process(self, json_data: dict):
        if self.parent_data:
            json_data["parent_data"] = self.parent_data_to_json()
        json_data["filetype_sub"] = 1
        json_data["uuid_sub"] = self.uuid
        json_data["ref_obj"] = {
            "model_name": self._model_name,
            "instance_id": self._instance_id
        }
        json_data["interpage"] = {
            "prev": None if not self._interpage_prev else self._interpage_prev.to_json_basic(),
            "next": None if not self._interpage_next else self._interpage_next.to_json_basic()
        }
        try:
            json_data["namespace_sub"] = json_data.pop("namespace")
        except KeyError:
            json_data["namespace_sub"] = {}
        json_data["namespace"] = self.namespace

        return json_data

    def to_json(self):
        result = self._ref_instance.to_json()
        result = self._json_post_process(result)
        return result

    def to_json_basic(self):
        result = self._ref_instance.to_json_basic()
        result = self._json_post_process(result)
        return result

    def _get_instance_offset(self, offset: int):
        raise NotImplementedError
