"""
Amygdale (Amygdala)

L'amygdale est le "détecteur de saillance émotionnelle" — en particulier la peur,
mais aussi la récompense, la surprise et tout ce qui a une charge affective forte.

Rôles:
- Évaluation émotionnelle rapide (avant la cognition consciente)
- Déclenchement des réponses de peur (freeze / fight / flight)
- Marquage émotionnel des souvenirs (mémorisation émotionnelle → hippocampe)
- Modulation de l'attention vers les stimuli émotionnellement chargés
- Conditionnement (apprentissage par association stimulus–émotion)

Connexions: Thalamus → Amygdale (voie rapide, non consciente)
            Cortex sensoriel → Amygdale (voie lente, consciente)
            Amygdale → Hippocampe (marquage mémoriel)
            Amygdale → PFC (modulation de l'exécutif)
            Amygdale → Tronc (déclenchement physiologique)
            Amygdale ↔ Insula (interoception émotionnelle)
"""
from __future__ import annotations
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


class Amygdala(BrainRegion):
    def __init__(self):
        super().__init__("amygdala", capacity=20)
        self.fear_level: float = 0.0
        self.reward_signal: float = 0.0
        self.emotional_valence: float = 0.0     # État émotionnel courant
        self.emotional_arousal: float = 0.0
        self._conditioning: dict[str, float] = {}  # Associations apprises

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        max_threat = 0.0
        max_reward = 0.0
        total_valence = 0.0
        total_arousal = 0.0
        count = 0

        for sig in signals:
            threat = sig.content.get("threat", 0.0)
            reward = sig.content.get("reward", 0.0)
            stimulus_id = sig.content.get("stimulus_id", "")

            # Vérification des conditionnements appris
            if stimulus_id and stimulus_id in self._conditioning:
                conditioned = self._conditioning[stimulus_id]
                threat = max(threat, conditioned if conditioned < 0 else 0)
                reward = max(reward, conditioned if conditioned > 0 else 0)

            max_threat = max(max_threat, threat * sig.strength)
            max_reward = max(max_reward, reward * sig.strength)
            total_valence += sig.valence * sig.strength
            total_arousal += sig.arousal * sig.strength
            count += 1

        if count > 0:
            avg_valence = total_valence / count
            avg_arousal = total_arousal / count
        else:
            avg_valence = 0.0
            avg_arousal = 0.0

        # Mise à jour des états internes — réponse plus rapide pour les signaux forts
        decay_v = 0.5 if abs(avg_valence) > 0.5 else 0.65
        decay_a = 0.5 if avg_arousal > 0.6 else 0.65
        self.fear_level    = self.fear_level * 0.6 + max_threat * 0.4
        self.reward_signal = self.reward_signal * 0.6 + max_reward * 0.4
        # La valence émotionnelle intègre valence du signal ET reward/fear
        composite_valence = (avg_valence * 0.6
                             + self.reward_signal * 0.25
                             - self.fear_level * 0.15)
        self.emotional_valence = self.emotional_valence * decay_v + composite_valence * (1 - decay_v)
        self.emotional_arousal = self.emotional_arousal * decay_a + avg_arousal * (1 - decay_a)

        # Modulation neurochimique
        if self.fear_level > 0.3:
            nt.modulate({
                "norepinephrine": self.fear_level * 0.1,
                "cortisol":       self.fear_level * 0.05,
                "gaba":          -self.fear_level * 0.03,
            })
        if self.reward_signal > 0.3:
            nt.modulate({
                "dopamine":    self.reward_signal * 0.1,
                "endorphins":  self.reward_signal * 0.05,
            })

        emotional_intensity = max(abs(self.emotional_valence), self.fear_level,
                                  self.reward_signal)

        if emotional_intensity > 0.1:
            # Signal émotionnel vers le PFC (module la prise de décision)
            self._emit(self._make_signal(
                target="prefrontal_cortex",
                signal_type="emotional",
                content={
                    "fear":    round(self.fear_level, 3),
                    "reward":  round(self.reward_signal, 3),
                    "valence": round(self.emotional_valence, 3),
                    "arousal": round(self.emotional_arousal, 3),
                },
                strength=emotional_intensity,
                valence=self.emotional_valence,
                arousal=self.emotional_arousal,
            ))

            # Signal vers l'hippocampe: les moments émotionnellement intenses
            # sont mieux mémorisés (marquage émotionnel)
            self._emit(self._make_signal(
                target="hippocampus",
                signal_type="emotional",
                content={
                    "emotional_tag": round(emotional_intensity, 3),
                    "valence":       round(self.emotional_valence, 3),
                },
                strength=emotional_intensity * 0.8,
                valence=self.emotional_valence,
                arousal=self.emotional_arousal,
            ))

            # Signal vers l'insula si arousal élevé (ressenti corporel)
            if self.emotional_arousal > 0.4:
                self._emit(self._make_signal(
                    target="insula",
                    signal_type="emotional",
                    content={"body_arousal": self.emotional_arousal,
                             "valence": self.emotional_valence},
                    strength=self.emotional_arousal * 0.7,
                    arousal=self.emotional_arousal,
                ))

    def condition(self, stimulus_id: str, emotional_value: float) -> None:
        """Apprentissage par conditionnement (pavlovien)."""
        prev = self._conditioning.get(stimulus_id, 0.0)
        self._conditioning[stimulus_id] = prev * 0.7 + emotional_value * 0.3

    def get_state(self) -> dict:
        base = super().get_state()
        base.update({
            "fear":     round(self.fear_level, 3),
            "reward":   round(self.reward_signal, 3),
            "valence":  round(self.emotional_valence, 3),
            "e_arousal": round(self.emotional_arousal, 3),
            "conditioned_stimuli": len(self._conditioning),
        })
        return base
