import abc


class SingletonInstanceMixin(abc.ABC):
    _instance = {}

    def __new__(cls, *args, **kwargs):
        data = kwargs.get("data", None)
        instance_id = kwargs.get("instance_id", None)
        if (not data) and (not instance_id):
            raise ValueError

        if data:
            instance_id = cls._get_instance_id(data)
            instance = cls._instance.get(instance_id, None)
            if instance:
                return instance
            instance = super().__init__(cls)
            return instance
        if instance_id:
            return cls._instance[instance_id]

    @staticmethod
    @abc.abstractmethod
    def _get_instance_id(data):
        raise NotImplementedError

    @property
    def instance_id(self):
        return self._get_instance_id(self.data)


class NamespacePathMixin(abc.ABC):
    def get_path(self, delimiter: str = "/", filename:bool=False):
        path = delimiter.join(self.namespace)
        if not filename:
            return path[:-5]
        return path

