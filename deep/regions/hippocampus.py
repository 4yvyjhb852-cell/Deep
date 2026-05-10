"""
Hippocampe (Hippocampus)

Le siège de la mémoire épisodique et de la navigation spatiale/temporelle.

Rôles:
- Encodage de nouveaux souvenirs épisodiques (ce qui m'est arrivé)
- Consolidation: transfert vers le cortex pour stockage à long terme
- Récupération: réactivation des souvenirs pertinents
- Apprentissage contextuel: "dans quel contexte cela s'est passé?"
- Mémoire spatiale (carte cognitive de l'environnement)
- Pattern completion: un indice partiel → rappel du tout

Propriétés clés:
- L'encodage est renforcé par l'émotion (amygdale) et l'attention (PFC)
- L'encodage est renforcé par l'acétylcholine
- Le cortisol élevé DÉGRADE l'encodage (stress chronique = perte mémoire)
- La consolidation se fait pendant le sommeil (modélisé comme phase de repos)

Connexions: → Cortex entorhinal → Néocortex (stockage à long terme)
            ← Amygdale (marquage émotionnel)
            ← PFC (récupération intentionnelle)
            → PFC (contexte mémorisé)
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


@dataclass
class MemoryTrace:
    """Trace mémorielle épisodique."""
    episode_id: int
    content: dict
    emotional_tag: float       # Force du marquage émotionnel
    valence: float
    encoded_at: float = field(default_factory=time.time)
    strength: float = 1.0      # Force de la trace (décroît avec le temps)
    consolidated: bool = False  # Transférée en mémoire long terme?
    retrieval_count: int = 0   # Nombre de récupérations

    def decay(self, rate: float = 0.001) -> None:
        """Décroissance de la trace mémorielle (oubli naturel)."""
        if not self.consolidated:
            emotional_protection = self.emotional_tag * 0.5
            self.strength = max(0.0, self.strength - rate * (1 - emotional_protection))

    def reinforce(self, amount: float = 0.1) -> None:
        """Renforcement à chaque récupération."""
        self.strength = min(1.0, self.strength + amount)
        self.retrieval_count += 1


class Hippocampus(BrainRegion):
    def __init__(self):
        super().__init__("hippocampus", capacity=20)
        self._episode_counter: int = 0
        self._working_episode: dict = {}    # Épisode en cours d'encodage
        self._memory_traces: list[MemoryTrace] = []
        self._consolidation_queue: list[MemoryTrace] = []
        self.current_emotional_tag: float = 0.0

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        retrieval_cue = None
        new_content = {}
        emotional_tag = self.current_emotional_tag

        for sig in signals:
            if sig.signal_type == "emotional":
                # L'amygdale booste l'encodage
                emotional_tag = max(emotional_tag, sig.content.get("emotional_tag", 0))
                self.current_emotional_tag = emotional_tag * 0.8  # Décroissance

            elif sig.signal_type == "sensory":
                # Contenu sensoriel → encodage épisodique
                new_content.update(sig.content)
                # Les signaux à forte valence portent leur propre tag émotionnel
                if abs(sig.valence) > 0.3 or sig.arousal > 0.6:
                    direct_tag = (abs(sig.valence) * 0.6 + sig.arousal * 0.4) * sig.strength
                    emotional_tag = max(emotional_tag, direct_tag)

            elif sig.signal_type == "executive":
                # PFC demande une récupération
                if sig.content.get("retrieve"):
                    retrieval_cue = sig.content.get("retrieve")

        # Encodage d'un nouvel épisode si contenu présent
        if new_content:
            # L'efficacité d'encodage dépend des neurotransmetteurs
            encoding_efficiency = nt.memory_encoding_efficiency
            # Le cortisol dégrade l'encodage
            encoding_efficiency *= max(0.2, 1.0 - nt.cortisol * 0.5)

            if encoding_efficiency > 0.2:
                self._episode_counter += 1
                trace = MemoryTrace(
                    episode_id=self._episode_counter,
                    content=new_content.copy(),
                    emotional_tag=emotional_tag,
                    valence=sum(s.valence for s in signals) / max(1, len(signals)),
                    strength=encoding_efficiency,
                )
                self._memory_traces.append(trace)

                # Signal de confirmation d'encodage → PFC
                self._emit(self._make_signal(
                    target="prefrontal_cortex",
                    signal_type="mnemonic",
                    content={
                        "episode_id": self._episode_counter,
                        "encoded": True,
                        "strength": round(encoding_efficiency, 3),
                        "emotional_tag": round(emotional_tag, 3),
                    },
                    strength=encoding_efficiency * 0.7,
                ))

        # Récupération mémorielle
        if retrieval_cue:
            recalled = self._retrieve(retrieval_cue)
            if recalled:
                self._emit(self._make_signal(
                    target="prefrontal_cortex",
                    signal_type="mnemonic",
                    content={
                        "retrieved": True,
                        "cue": retrieval_cue,
                        "memory": recalled.content,
                        "emotional_tag": recalled.emotional_tag,
                        "valence": recalled.valence,
                    },
                    strength=recalled.strength,
                    valence=recalled.valence,
                ))

        # Décroissance des traces (oubli naturel)
        for trace in self._memory_traces:
            trace.decay()
        self._memory_traces = [t for t in self._memory_traces if t.strength > 0.01]

    def _retrieve(self, cue: str | dict) -> MemoryTrace | None:
        """Récupération par similarité (pattern completion)."""
        if not self._memory_traces:
            return None

        if isinstance(cue, str):
            # Recherche par clé de contenu
            candidates = [
                t for t in self._memory_traces
                if any(cue in str(v) for v in t.content.values())
            ]
        else:
            candidates = self._memory_traces

        if not candidates:
            return None

        # Sélectionne la trace la plus forte (force × marquage émotionnel)
        best = max(candidates, key=lambda t: t.strength * (1 + t.emotional_tag))
        best.reinforce()
        return best

    def get_state(self) -> dict:
        base = super().get_state()
        base.update({
            "memory_traces": len(self._memory_traces),
            "total_episodes": self._episode_counter,
            "avg_strength": round(
                sum(t.strength for t in self._memory_traces) / max(1, len(self._memory_traces)),
                3
            ),
        })
        return base
