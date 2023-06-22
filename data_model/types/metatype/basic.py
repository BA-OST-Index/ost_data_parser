import logging
import abc
import numbers
import functools

# logging.basicConfig(level=logging.DEBUG)

__all__ = ["BasicType", "BasicModel", "Integer", "String", "Bool",
           "MultipleBasicModelList", "MultipleBasicModelListManager",
           "MultipleBasicModelListManager", "ToJsonMixin", "ToJsonReminderMixin"]


def genetic_validator(value, target_type):
    if isinstance(value, target_type):
        return
    raise ValueError("The value %r is not an instance of %r" % (value, target_type))


class ToJsonReminderMixin:
    @abc.abstractmethod
    def to_json(self):
        pass

    @abc.abstractmethod
    def to_json_basic(self):
        pass


class ToJsonMixin(ToJsonReminderMixin):
    def to_json(self):
        """返回一个元组 (str, Any) 其中第一个为自己的公开名字，另一个则为符合标准的JSON对象（字典/列表）"""
        dict_ = dict()
        for i in self._components:
            dict_[i] = getattr(self, i)
        return self.key_name, dict_

    @abc.abstractmethod
    def to_json_basic(self):
        pass


class DescriptorNameMixin(abc.ABC):
    def __init__(self, name, type_name, no=0):
        self.private_name = f"_{type_name}_{name}_{no}"
        self.public_name = name


class BasicType(DescriptorNameMixin, abc.ABC):
    """Modified from https://docs.python.org/3/howto/descriptor.html#customized-names"""

    def __init__(self, name, type_name, no):
        DescriptorNameMixin.__init__(self, name, type_name, no)

    def __get__(self, instance, owner):
        value = getattr(instance, self.private_name)
        logging.debug("Accessing %r (instance %r): %r", self.public_name, instance, value)
        return value

    def __set__(self, instance, value):
        self.validate(value)
        setattr(instance, self.private_name, value)
        self.post_process(instance, self.private_name)
        logging.debug("Updating %r (instance %r) to %r" % (self.public_name, instance, value))

    @abc.abstractmethod
    def validate(self, value):
        pass

    def post_process(self, instance, private_name):
        """如果传入的值需要进一步处理的话（例如，将其转换为一致的格式时）"""
        pass


class BasicModel(abc.ABC, ToJsonMixin):
    """
    代表一个高层的数据模型，其中所有的内容的检查都委托给类变量中的继承 BasicType 的对象的类型检查。

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


class MultipleBasicModelList(abc.ABC, ToJsonMixin):
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
        t = [value.to_json() for value in self.basic_model_list]
        return self.key_name, t

    def to_json_basic(self):
        t = [value.to_json_basic() for value in self.basic_model_list]
        return t


class MultipleBasicModelListManager(BasicModel, abc.ABC):
    def __init__(self, key_name):
        super().__init__(key_name)

    @abc.abstractmethod
    def load(self, data):
        super().load(data)

    @abc.abstractmethod
    def to_json(self):
        pass

    def to_json_basic(self):
        return self.to_json()[-1]


class Integer(BasicType):
    def __init__(self, name, no=0):
        super().__init__(name, "integer", no)

    validate = functools.partial(genetic_validator, target_type=numbers.Integral)


class String(BasicType):
    def __init__(self, name, no=0):
        super().__init__(name, "string", no)

    validate = functools.partial(genetic_validator, target_type=str)


class Bool(BasicType):
    def __init__(self, name, no=0):
        super().__init__(name, "bool", no)

    validate = functools.partial(genetic_validator, target_type=bool)
