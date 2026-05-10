"""
Signal neural — l'unité de communication entre les régions cérébrales.

Basé sur le modèle du potentiel d'action et de la transmission synaptique.
Chaque signal porte: une source, une cible, un type, un contenu sémantique,
une force, une valence émotionnelle et un niveau d'éveil.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import time


# Types de signaux correspondant aux grandes voies neurales
SIGNAL_TYPES = {
    "sensory":      "Signal sensoriel (entrée perceptuelle)",
    "motor":        "Signal moteur (commande d'action)",
    "emotional":    "Signal émotionnel (amygdale / limbique)",
    "mnemonic":     "Signal mnésique (hippocampe)",
    "executive":    "Signal exécutif (cortex préfrontal)",
    "reward":       "Signal de récompense (noyaux gris)",
    "arousal":      "Signal d'éveil (tronc / thalamus)",
    "predictive":   "Signal prédictif (erreur de prédiction)",
    "interoceptive":"Signal intéroceptif (insula)",
    "social":       "Signal social (cognition sociale)",
    "inhibitory":   "Signal inhibiteur (GABA)",
    "internal":     "Signal interne (traitement en cours)",
}


@dataclass
class NeuralSignal:
    """Unité fondamentale d'information qui circule dans le cerveau."""

    source: str                          # Région émettrice
    target: str                          # Région cible (ou "broadcast")
    signal_type: str                     # Catégorie du signal
    content: dict[str, Any]             # Contenu sémantique du signal
    strength: float = 1.0               # Intensité 0.0–1.0
    valence: float = 0.0                # Valence émotionnelle -1.0 (négatif) → +1.0 (positif)
    arousal: float = 0.5                # Niveau d'éveil 0.0 (calme) → 1.0 (intense)
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.strength = max(0.0, min(1.0, self.strength))
        self.valence  = max(-1.0, min(1.0, self.valence))
        self.arousal  = max(0.0, min(1.0, self.arousal))

    def attenuate(self, factor: float) -> "NeuralSignal":
        """Retourne un signal atténué (modélise la perte synaptique)."""
        return NeuralSignal(
            source=self.source,
            target=self.target,
            signal_type=self.signal_type,
            content=self.content.copy(),
            strength=self.strength * factor,
            valence=self.valence,
            arousal=self.arousal * factor,
            timestamp=self.timestamp,
            metadata=self.metadata.copy(),
        )

    def __repr__(self) -> str:
        return (
            f"NeuralSignal({self.source}→{self.target} | "
            f"type={self.signal_type} | strength={self.strength:.2f} | "
            f"valence={self.valence:+.2f} | arousal={self.arousal:.2f})"
        )
