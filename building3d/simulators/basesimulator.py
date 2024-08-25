from abc import ABC, abstractmethod


class BaseSimulator(ABC):

    @abstractmethod
    def forward(self): ...

    @abstractmethod
    def is_finished(self) -> bool: ...
