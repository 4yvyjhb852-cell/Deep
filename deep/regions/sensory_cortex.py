"""
Cortex Sensoriel (Sensory Cortex)

Regroupe les différentes aires sensorielles primaires et associatives:
- Cortex visuel (V1-V5)
- Cortex auditif (A1, A2)
- Cortex somatosensoriel (S1, S2)
- Cortex olfactif (voie directe, sans thalamus)
- Cortex gustatif

En pratique ici, c'est le premier niveau de traitement conscient
des informations sensorielles.

Rôles:
- Traitement des caractéristiques sensorielles (quoi, où, comment?)
- Reconnaissance de patterns (visages, voix, objets)
- Intégration multimodale
- Génération de représentations perceptuelles

Connexions: Thalamus → Cortex sensoriel (entrée)
            Cortex sensoriel → Hippocampe (encodage mémoriel)
            Cortex sensoriel → Amygdale (voie lente, consciente)
            Cortex sensoriel → PFC (représentations pour la cognition)
"""
from __future__ import annotations
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


class SensoryCortex(BrainRegion):
    def __init__(self):
        super().__init__("sensory_cortex", capacity=20)
        self._feature_buffer: list[dict] = []      # Features extraites
        self._recognition_cache: dict[str, float] = {}  # Cache de reconnaissance

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        for sig in signals:
            if sig.signal_type != "sensory":
                continue

            content = sig.content
            # Extraction de features (traitement de bas niveau)
            features = {
                "modality":  content.get("modality", "unknown"),
                "intensity": sig.strength,
                "novelty":   content.get("novelty", 0.3),
                "pattern":   content.get("pattern", ""),
                "location":  content.get("location", ""),
            }
            self._feature_buffer.append(features)
            if len(self._feature_buffer) > 20:
                self._feature_buffer.pop(0)

            # Reconnaissance (pattern matching simplifié)
            pattern = features["pattern"]
            if pattern:
                recognition = self._recognition_cache.get(pattern, 0.0)
                # Plus un pattern a été vu, plus la reconnaissance est rapide/forte
                self._recognition_cache[pattern] = min(1.0, recognition + 0.05)
                recognized = recognition > 0.2
            else:
                recognized = False
                recognition = 0.0

            processed_strength = sig.strength * (
                nt.acetylcholine * 0.3 + 0.7  # L'ACh améliore la perception
            )

            # → Hippocampe: encoder ce qui est perçu
            self._emit(self._make_signal(
                target="hippocampus",
                signal_type="sensory",
                content={
                    **content,
                    "features":    features,
                    "recognized":  recognized,
                    "recognition_strength": round(recognition, 3),
                    "novelty":     features["novelty"],
                },
                strength=processed_strength * 0.7,
                valence=sig.valence,
                arousal=sig.arousal,
            ))

            # → PFC: représentation pour la cognition
            self._emit(self._make_signal(
                target="prefrontal_cortex",
                signal_type="sensory",
                content={
                    **content,
                    "features":   features,
                    "recognized": recognized,
                    "novelty":    features["novelty"],
                },
                strength=processed_strength * 0.6,
                valence=sig.valence,
                arousal=sig.arousal,
            ))

            # → Amygdale (voie consciente lente): si valence forte
            if abs(sig.valence) > 0.3 or content.get("threat", 0) > 0.2:
                self._emit(self._make_signal(
                    target="amygdala",
                    signal_type="sensory",
                    content=content,
                    strength=processed_strength * 0.5,
                    valence=sig.valence,
                    arousal=sig.arousal,
                ))

    def get_state(self) -> dict:
        base = super().get_state()
        base.update({
            "patterns_known": len(self._recognition_cache),
            "recent_features": len(self._feature_buffer),
        })
        return base
