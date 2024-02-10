from abc import ABC
from abc import abstractmethod


class ActionAbstract(ABC):
	@abstractmethod
	def perform(self, data: dict, sender: str, transaction_id: str) -> tuple:
		pass


class CompensationAbstract(ABC):
	@abstractmethod
	def compensate(self, data: dict, sender: str, transaction_id: str) -> tuple:
		pass


class PublisherAbstract(ABC):
	@abstractmethod
	def send(self, destination: str, body: dict) -> None:
		pass
