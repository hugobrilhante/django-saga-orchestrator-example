from abc import ABC
from abc import abstractmethod


class ActionAbstract(ABC):
    @abstractmethod
    def execute(self, data: dict, transaction_id: str) -> tuple:
        pass


class PublisherAbstract(ABC):
    @abstractmethod
    def send(self, destination: str, body: dict) -> None:
        pass
