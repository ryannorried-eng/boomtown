from abc import ABC, abstractmethod
from typing import Any


class OddsCollector(ABC):
    @abstractmethod
    def collect(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class FeatureEngineer(ABC):
    @abstractmethod
    def build_features(self, source_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise NotImplementedError


class PredictiveModel(ABC):
    @abstractmethod
    def predict(self, features: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise NotImplementedError


class Recommender(ABC):
    @abstractmethod
    def recommend(self, predictions: list[dict[str, Any]], market_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise NotImplementedError


class CloseCapture(ABC):
    @abstractmethod
    def capture(self, picks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise NotImplementedError


class Settler(ABC):
    @abstractmethod
    def settle(self, picks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        raise NotImplementedError
