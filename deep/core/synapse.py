"""
Synapse — modèle de connexion entre deux régions cérébrales.

Implémente:
- Plasticité synaptique (Hebbian: les connexions utilisées se renforcent)
- Potentiation à long terme (LTP) et dépression à long terme (LTD)
- Poids synaptique (force de la connexion)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from deep.core.neural_signal import NeuralSignal


@dataclass
class Synapse:
    """Connexion pondérée entre deux régions."""
    pre:    str          # Région présynaptique
    post:   str          # Région postsynaptique
    weight: float = 0.5  # Force de la connexion 0.0–1.0
    plastic: bool = True # La connexion peut-elle se modifier?

    # Paramètres d'apprentissage
    ltp_rate: float = 0.01   # Long-term potentiation
    ltd_rate: float = 0.005  # Long-term depression
    decay_rate: float = 0.001

    _activation_history: list[float] = field(default_factory=list, repr=False)

    def transmit(self, signal: NeuralSignal) -> NeuralSignal:
        """Transmet un signal en le modulant par le poids synaptique."""
        if self.plastic:
            self._record(signal.strength)
        return signal.attenuate(self.weight)

    def _record(self, activation: float) -> None:
        self._activation_history.append(activation)
        if len(self._activation_history) > 100:
            self._activation_history.pop(0)

    def hebbian_update(self, pre_activity: float, post_activity: float) -> None:
        """
        Règle de Hebb: 'Neurons that fire together, wire together'.
        Si pré et post sont actifs simultanément → LTP (renforcement).
        Si seul le pré est actif → LTD (affaiblissement).
        """
        if not self.plastic:
            return
        if pre_activity > 0.3 and post_activity > 0.3:
            # Co-activation → potentiation
            delta = self.ltp_rate * pre_activity * post_activity
            self.weight = min(1.0, self.weight + delta)
        elif pre_activity > 0.3 and post_activity < 0.1:
            # Activité pré sans réponse post → dépression
            delta = self.ltd_rate * pre_activity
            self.weight = max(0.01, self.weight - delta)
        # Décroissance lente (forgetting)
        self.weight = max(0.01, self.weight - self.decay_rate * 0.1)
