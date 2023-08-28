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
        if filename:
            return path + ".json"
        return path


class OrderedDictWithCounter:
    def __init__(self):
        self.ordered_dict = OrderedDict()
        self.counter = dict()

    def get_counter_with_data(self):
        return OrderedDict((key, [value, self.counter[key]])
                           for key, value in self.ordered_dict.items())

    def get_counter_with_data_sorted_by_counter(self, reverse: bool = True):
        temp = [[key, [value, self.counter[key]]]
                for key, value in self.ordered_dict.items()]
        temp.sort(key=lambda i: i[1][1], reverse=reverse)
        return OrderedDict((i[0], i[1]) for i in temp)

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


def seconds_to_minutes(seconds: int):
    return seconds // 60, seconds % 60


def counter_dict_sorter(d: OrderedDict, key_name: list, reverse: bool = False, ignore_key_errors: bool = True):
    # sort the dict generated by `OrderedDictWithCounter.get_counter_with_data_sorted_by_counter`
    # tip: it also exports to json automatically, so just call it like
    #   counter_dict_sorter(OrderedDictWithCounter.get_counter_with_data_sorted_by_counter())

    # separate different items with different counts
    counter_and_item = {}
    for key, value in d.items():
        counter = value[1]
        if counter not in counter_and_item.keys():
            counter_and_item[counter] = []

        # export to json (to_json_basic)
        json_export = value[0].to_json_basic()

        counter_and_item[counter].append([key, [json_export, counter]])

    # define a function to return all the values of the keys wanted in sorting
    def get_all_keys(item):
        actual_dict = item[1][0]
        values = []

        for i in key_name:
            try:
                if isinstance(i, str):
                    values.append(actual_dict[i])
                elif isinstance(i, list):
                    _curr = actual_dict
                    for j in i: _curr = _curr[j]
                    values.append(_curr)
            except KeyError:
                if not ignore_key_errors:
                    raise

        values = tuple(values)
        return values

    # sort the dict
    for item_list in counter_and_item.values():
        item_list.sort(key=get_all_keys, reverse=reverse)

    # pack back
    new_d = OrderedDict()
    for item_list in counter_and_item.values():
        for item in item_list:
            new_d[item[0]] = item[1]

    return new_d
