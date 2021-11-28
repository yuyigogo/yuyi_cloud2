from abc import ABC, abstractmethod


class BaseHybridCloudScript(ABC):
    @classmethod
    @abstractmethod
    def run_script(cls, customer_id):
        pass
