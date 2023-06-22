import abc
import re
import datetime
import time
import numbers
from .basic import *

REGEX_URL = re.compile(r'\b\w+://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
__all__ = ["Url", "Timestamp", "UUID"]


class Url(BasicType):
    def __init__(self, name, no=0):
        super().__init__(name, "url", no)

    def validate(self, value):
        if REGEX_URL.search(value) is None:
            raise ValueError("Value %r is not URL." % value)


class Timestamp(BasicType):
    """
    A timestamp, which supports Integral, datetime.datetime,
    datetime.date and time.struct_time as the input. It then
    converts the input to a datetime object.
    """

    def __init__(self, name, no=0):
        super().__init__(name, "timestamp", no)

    def validate(self, value):
        a = isinstance(value, numbers.Integral)
        b = isinstance(value, datetime.datetime)
        c = isinstance(value, time.struct_time)
        if (not a) and (not b) and (not c):
            raise ValueError()

    def post_process(self, instance, private_name):
        value = getattr(instance, private_name)
        if isinstance(value, int):
            setattr(instance, private_name,
                    datetime.datetime.utcfromtimestamp(value))
        elif isinstance(value, datetime.datetime):
            # 已经是 datetime.datetime 类，那就顺便统一一下
            setattr(instance, private_name,
                    value.astimezone(datetime.timezone.utc))
        elif isinstance(value, time.struct_time):
            setattr(instance, private_name,
                    datetime.datetime(value.tm_year, value.tm_mon, value.tm_mday,
                                      value.tm_hour, value.tm_min, value.tm_sec,
                                      datetime.timezone.utc))


class GeneticAutoIndexingRecord(BasicType):
    """自动索引的数据记录（类CSV格式）"""

    def __init__(self, name, data_parts: int, no=0):
        super().__init__(name, "autoIndexing", no)
        self.data_parts = data_parts

    def validate(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Record %r is not a string." % value)
        temp = value.split(",")
        if len(temp) != self.data_parts:
            raise ValueError("Requires length %s but got %s instead." % (str(len(temp)), str(self.data_parts)))
        try:
            [int(i) for i in temp]
        except ValueError:
            raise ValueError("Record %r has data that is not an integer." % value)


class UUID(BasicType):
    def __init__(self, name, no=0):
        BasicType.__init__(self, name, "UUID", no)

    def validate(self, value):
        String.validate(value)
        if len(value) != 36:
            raise ValueError("Not a proper UUID (32-bit long)!")


class OneOf(BasicType, abc.ABC):
    """确认设置的内容是否是 options 之一。这是一个抽象类，应由具体的、预先定义好 options 的类继承。"""

    def __init__(self, name, options: list, no=0):
        BasicType.__init__(self, name, "oneof", no)
        self.options = options

    def validate(self, value):
        if value not in self.options:
            raise ValueError("%r is not a valid option!" % value)
