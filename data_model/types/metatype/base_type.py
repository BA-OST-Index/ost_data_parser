import logging
import abc
import numbers
import functools

# logging.basicConfig(level=logging.DEBUG)

__all__ = ["BaseType", "Integer", "String", "Bool"]


def genetic_validator(value, target_type):
    if isinstance(value, target_type):
        return
    raise ValueError("The value %r is not an instance of %r" % (value, target_type))


class DescriptorNameMixin(abc.ABC):
    def __init__(self, name, type_name, no=0):
        self.private_name = f"_{type_name}_{name}_{no}"
        self.public_name = name


class BaseType(DescriptorNameMixin, abc.ABC):
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


class Integer(BaseType):
    def __init__(self, name, no=0):
        super().__init__(name, "integer", no)

    validate = functools.partial(genetic_validator, target_type=numbers.Integral)


class String(BaseType):
    def __init__(self, name, no=0):
        super().__init__(name, "string", no)

    validate = functools.partial(genetic_validator, target_type=str)


class Bool(BaseType):
    def __init__(self, name, no=0):
        super().__init__(name, "bool", no)

    validate = functools.partial(genetic_validator, target_type=bool)
