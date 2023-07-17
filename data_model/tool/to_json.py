import abc


class IToJson:
    @abc.abstractmethod
    def to_json(self):
        pass

    @abc.abstractmethod
    def to_json_basic(self):
        pass


class ToJsonMixin(IToJson):
    def to_json(self):
        """返回一个元组 (str, Any) 其中第一个为自己的公开名字，另一个则为符合标准的JSON对象（字典/列表）"""
        dict_ = dict()
        for i in self._components:
            dict_[i] = getattr(self, i)
        return dict_

    @abc.abstractmethod
    def to_json_basic(self):
        pass

    def to_json_with_usage(self):
        pass
