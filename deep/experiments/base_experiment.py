"""Classe de base pour toutes les expériences."""
from __future__ import annotations
from abc import ABC, abstractmethod
from deep.core.brain import Brain


class Experiment(ABC):
    """Protocole d'expérimentation sur le cerveau."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.results: list[dict] = []

    @abstractmethod
    def run(self, brain: Brain) -> dict:
        """Exécute l'expérience et retourne les résultats."""
        ...

    def _record(self, tick: int, data: dict) -> None:
        self.results.append({"tick": tick, **data})

    def summary(self) -> dict:
        return {
            "experiment": self.name,
            "ticks":      len(self.results),
            "results":    self.results,
        }
