import abc
from collections import OrderedDict


class SingletonInstanceMixin(abc.ABC):
    _instance = {}

    def __new__(cls, *args, **kwargs):
        data = kwargs.get("data", None)
        if not data:
            raise ValueError

        if data:
            instance_id = cls._get_instance_id(data)
            instance = cls._instance.get(instance_id, None)
            if instance:
                return instance
            instance = super().__new__(cls)
            cls._instance[instance_id] = instance
            return instance

    @staticmethod
    @abc.abstractmethod
    def _get_instance_id(data):
        raise NotImplementedError

    @property
    def instance_id(self):
        return self._get_instance_id(self.data)

    @classmethod
    def get_instance(cls, instance_id):
        return cls._instance[instance_id]


class NamespacePathMixin(abc.ABC):
    def get_path(self, delimiter: str = "/", filename: bool = False):
        path = delimiter.join(self.namespace)
        if not filename:
            return path[:-5]
        return path


class OrderedDictWithCounter:
    def __init__(self):
        self.ordered_dict = OrderedDict()
        self.counter = dict()

    def get_counter_with_data(self):
        return OrderedDict((key, [value, self.counter[key]])
                           for key, value in self.ordered_dict.items())

    def keys(self):
        return self.ordered_dict.keys()

    def values(self):
        return self.ordered_dict.values()

    def items(self):
        return self.ordered_dict.items()

    def __getitem__(self, item):
        return self.ordered_dict[item]

    def __setitem__(self, key, value):
        if key not in self.ordered_dict.keys():
            self.counter[key] = 1
            self.ordered_dict[key] = value
        else:
            self.counter[key] += 1

    def __len__(self):
        return len(self.ordered_dict.keys())
