import abc
from data_model.tool.tool import SingletonInstanceMixin


class InterpageMixin(SingletonInstanceMixin):
    def get_mixed_interpage_data(self, prev, next):
        return {
            "prev": {
                "name": prev.name.to_json_basic() if prev else "[NO_PREV]",
                "namespace": prev.namespace if prev else "[NO_PREV]"
            },
            "next": {
                "name": next.name.to_json_basic() if next else "[NO_NEXT]",
                "namespace": next.namespace if next else "[NO_NEXT]"
            }
        }

    def get_interpage_data(self):
        return self.get_mixed_interpage_data(self.interpage_prev, self.interpage_next)

    @abc.abstractmethod
    def _get_instance_offset(self, offset: int):
        raise NotImplementedError

    @property
    def interpage_prev(self):
        return self._get_instance_offset(-1)

    @property
    def interpage_next(self):
        return self._get_instance_offset(1)
