"""
Insula (Cortex insulaire)

L'insula est le "corps intérieur" du cerveau — elle crée la conscience
du corps et des états internes (intéroception).

Rôles:
- Intéroception: conscience du rythme cardiaque, respiration, douleur, faim
- Conscience émotionnelle subjective (transformer les signaux corporels
  en "ressentis" conscients)
- Empathie (simuler les états internes d'autrui)
- Dégoût et répugnance
- Conscience du moment présent (présence)
- Intégration corps-esprit (le "feeling" des émotions)

Note clé: Damasio argue que sans l'insula, on ne "ressent" pas vraiment les
émotions — on les calcule sans les vivre. L'insula est ce qui transforme un
état émotionnel en EXPÉRIENCE subjective.

Connexions: Amygdale ↔ Insula (bidirectionnel)
            PFC → Insula (régulation)
            Insula → Cingulaire antérieur (conscience des conflits)
            Insula → PFC (signaux intéroceptifs conscients)
"""
from __future__ import annotations
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


class Insula(BrainRegion):
    def __init__(self):
        super().__init__("insula", capacity=15)
        self.body_state: dict[str, float] = {
            "heart_rate":    0.5,   # Normalisé 0–1
            "muscle_tension": 0.3,
            "gut_feeling":   0.5,
            "pain_level":    0.0,
            "energy":        0.7,
        }
        self.felt_emotion: dict = {}      # L'émotion "ressentie" (vs calculée)
        self.empathy_signal: float = 0.0

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        for sig in signals:
            if sig.signal_type == "emotional":
                # Transformer l'émotion en état corporel ressenti
                arousal = sig.content.get("body_arousal", sig.arousal)
                valence = sig.content.get("valence", sig.valence)

                # L'arousal se manifeste dans le corps
                self.body_state["heart_rate"] = min(1.0,
                    self.body_state["heart_rate"] * 0.7 + arousal * 0.3
                )
                self.body_state["muscle_tension"] = min(1.0,
                    self.body_state["muscle_tension"] * 0.8
                    + max(0, -valence) * arousal * 0.3
                )

                # Le "gut feeling" est une intégration de valence et d'état corporel
                self.body_state["gut_feeling"] = min(1.0, max(0.0,
                    0.5 + valence * 0.3 + (nt.serotonin - 0.5) * 0.2
                ))

                # L'émotion ressentie: combinaison du signal émotionnel + état corporel
                self.felt_emotion = {
                    "valence":      round(valence, 3),
                    "arousal":      round(arousal, 3),
                    "body_tension": round(self.body_state["muscle_tension"], 3),
                    "gut_feeling":  round(self.body_state["gut_feeling"], 3),
                    "subjective_intensity": round(
                        (abs(valence) + arousal + self.body_state["heart_rate"]) / 3, 3
                    ),
                }

            elif sig.signal_type == "interoceptive":
                # Signal depuis le PFC: monitoring conscient
                monitored = sig.content.get("monitored_state", {})
                if monitored:
                    self.empathy_signal = abs(monitored.get("valence", 0.0)) * 0.5

        # L'énergie décroît avec la fatigue
        self.body_state["energy"] = max(0.1, min(1.0,
            self.body_state["energy"] - self.fatigue * 0.01
            + nt.dopamine * 0.005
        ))

        # Si état corporel significatif → signaler à la conscience (PFC, cingulaire)
        subjective_intensity = self.felt_emotion.get("subjective_intensity", 0.0)
        if subjective_intensity > 0.2 or self.body_state["pain_level"] > 0.1:
            self._emit(self._make_signal(
                target="cingulate_cortex",
                signal_type="interoceptive",
                content={
                    "felt_emotion":  self.felt_emotion,
                    "body_state":    {k: round(v, 3) for k, v in self.body_state.items()},
                    "empathy":       round(self.empathy_signal, 3),
                },
                strength=max(subjective_intensity, self.body_state["pain_level"]),
                valence=self.felt_emotion.get("valence", 0.0),
                arousal=self.felt_emotion.get("arousal", 0.5),
            ))

    def get_state(self) -> dict:
        base = super().get_state()
        base.update({
            "body_state":   {k: round(v, 3) for k, v in self.body_state.items()},
            "felt_emotion": self.felt_emotion,
            "empathy":      round(self.empathy_signal, 3),
        })
        return base
