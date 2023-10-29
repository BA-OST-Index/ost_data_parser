import abc
from data_model.tool.to_json import ToJsonMixin, IToJson


class BaseDataModel(abc.ABC, ToJsonMixin):
    """
    代表一个高层的数据模型，其中所有的内容的检查都委托给类变量中的继承 BaseType 的对象的类型检查。

    此类支持直接对其赋值一个JSON文件里的内容（如字典）来实现自动将内容加载到对象中。

    (注意：这不是一个 descriptor 这就是一个普通的 class 而已)
    """
    _components = []

    def __init__(self, key_name):
        """key_name 代表在JSON数据项中的 键 的名字"""
        self.key_name = key_name

    @abc.abstractmethod
    def load(self, data):
        self.data = data


class BaseDataModelList(abc.ABC, IToJson):
    def __init__(self, key_name, allowed_type):
        self.key_name = key_name
        self.basic_model_list = []
        self.allowed_type = allowed_type

    def __len__(self):
        return len(self.basic_model_list)

    def __iter__(self):
        return iter(self.basic_model_list)

    def __getitem__(self, item):
        return self.basic_model_list[item]

    def __setitem__(self, key, value):
        if not isinstance(value, self.allowed_type):
            raise ValueError("%r only supports %r object!" % (str(self.__class__.__name__),
                                                              str(self.allowed_type.__class__.__name__)))
        self.basic_model_list[key] = value

    def __delitem__(self, key):
        del self.basic_model_list[key]

    def append(self, value):
        if not isinstance(value, self.allowed_type):
            raise ValueError("%r only supports %r object!" % (str(self.__class__.__name__),
                                                              str(self.allowed_type.__class__.__name__)))
        self.basic_model_list.append(value)

    def to_json(self):
        t = [value.to_json_basic() for value in self.basic_model_list]
        return t

    def to_json_basic(self):
        return self.to_json()


class BaseDataModelListManager(BaseDataModel, IToJson):
    def __init__(self, key_name):
        super().__init__(key_name)

    @abc.abstractmethod
    def load(self, data):
        super().load(data)

    def to_json_basic(self):
        return self.to_json()