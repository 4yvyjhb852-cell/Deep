"""
Classe de base pour toutes les régions cérébrales.

Chaque région:
- Reçoit des signaux entrants
- Les traite selon sa logique propre
- Émet des signaux vers d'autres régions
- Maintient un état interne d'activation
- Est modulée par les neurotransmetteurs
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from collections import deque

from deep.core.neural_signal import NeuralSignal

if TYPE_CHECKING:
    from deep.core.neurotransmitter import NeurotransmitterSystem


class BrainRegion(ABC):
    """Région cérébrale abstraite."""

    def __init__(self, name: str, capacity: int = 10):
        self.name = name
        self.activation: float = 0.0          # Niveau d'activation actuel 0–1
        self.fatigue: float = 0.0             # Fatigue accumulée 0–1
        self._input_buffer: deque[NeuralSignal] = deque(maxlen=capacity)
        self._output_buffer: list[NeuralSignal] = []
        self._history: list[dict] = []
        self._tick: int = 0
        # Si True, la sous-classe gère la fatigue elle-même dans _process_signals
        self._fatigue_managed_internally: bool = False

    def receive(self, signal: NeuralSignal) -> None:
        """Reçoit un signal entrant."""
        self._input_buffer.append(signal)

    def process(self, nt: "NeurotransmitterSystem") -> list[NeuralSignal]:
        """
        Traite tous les signaux en buffer et retourne les signaux émis.
        Appelle _process_signals() implémentée par chaque sous-classe.
        """
        self._tick += 1
        signals_in = list(self._input_buffer)
        self._input_buffer.clear()
        self._output_buffer = []

        if signals_in:
            # L'activation monte selon la force moyenne des signaux reçus
            avg_strength = sum(s.strength for s in signals_in) / len(signals_in)
            self.activation = min(1.0, self.activation * 0.7 + avg_strength * 0.3)
            self._process_signals(signals_in, nt)
        else:
            # Décroissance naturelle de l'activation
            self.activation *= 0.85

        # La fatigue: la sous-classe peut gérer elle-même via _update_fatigue()
        # Par défaut: accumulation proportionnelle à l'activation
        if not self._fatigue_managed_internally:
            if self.activation > 0.15:
                accumulation = (self.activation - 0.15) * 0.05
                self.fatigue = min(1.0, self.fatigue + accumulation)
            elif len(signals_in) == 0:
                # Récupération uniquement au vrai repos (aucun signal reçu)
                self.fatigue = max(0.0, self.fatigue - 0.008)

        # Enregistrement pour analyse
        self._history.append({
            "tick": self._tick,
            "activation": round(self.activation, 3),
            "fatigue": round(self.fatigue, 3),
            "signals_in": len(signals_in),
            "signals_out": len(self._output_buffer),
        })
        if len(self._history) > 500:
            self._history.pop(0)

        return list(self._output_buffer)

    @abstractmethod
    def _process_signals(
        self, signals: list[NeuralSignal], nt: "NeurotransmitterSystem"
    ) -> None:
        """Logique de traitement propre à chaque région."""
        ...

    def _emit(self, signal: NeuralSignal) -> None:
        """Émet un signal de sortie."""
        self._output_buffer.append(signal)

    def _make_signal(
        self,
        target: str,
        signal_type: str,
        content: dict,
        strength: float = 0.5,
        valence: float = 0.0,
        arousal: float = 0.5,
    ) -> NeuralSignal:
        return NeuralSignal(
            source=self.name,
            target=target,
            signal_type=signal_type,
            content=content,
            strength=max(0.0, min(1.0, strength * (1.0 - self.fatigue * 0.5))),
            valence=valence,
            arousal=arousal,
        )

    def get_state(self) -> dict:
        return {
            "region": self.name,
            "activation": round(self.activation, 3),
            "fatigue": round(self.fatigue, 3),
            "tick": self._tick,
        }
