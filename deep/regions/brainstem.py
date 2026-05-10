"""
Tronc cérébral (Brainstem)

Le tronc cérébral est la structure la plus primitive et la plus essentielle.
Il gère:
- Les fonctions vitales (rythme cardiaque, respiration — ici modélisés comme
  un "battement" de base qui pulse à chaque tick)
- L'éveil et le niveau de conscience (système réticulaire activateur ascendant, SRAA)
- Le filtrage initial des stimuli entrants (quoi mérite l'attention?)
- La réponse de survie immédiate (danger → alerte maximale)

Connexions réelles: → Thalamus (éveil), → Amygdale (menace directe),
                    → Cortex (modulation de l'éveil)
"""
from __future__ import annotations
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem
import math


class Brainstem(BrainRegion):
    def __init__(self):
        super().__init__("brainstem", capacity=20)
        self.arousal_drive: float = 0.4      # Drive d'éveil de base
        self.vital_rhythm: int = 0           # Compteur de rythme vital
        self.threat_detected: bool = False

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        self.vital_rhythm += 1
        threat_level = 0.0
        max_arousal = 0.0

        for sig in signals:
            if sig.signal_type == "sensory":
                # Évaluation rapide de la menace (avant toute cognition)
                if sig.content.get("threat", 0) > 0.5:
                    threat_level = max(threat_level, sig.content["threat"])

                # Évaluation de la nouveauté → éveil
                novelty = sig.content.get("novelty", 0.3)
                max_arousal = max(max_arousal, sig.strength * novelty)

        # Mise à jour du niveau d'éveil
        self.arousal_drive = min(1.0, max(0.1,
            self.arousal_drive * 0.8 + max_arousal * 0.2
            + nt.norepinephrine * 0.1
        ))

        # Signal d'éveil permanent vers le thalamus (SRAA)
        arousal_signal_strength = (
            self.arousal_drive
            + nt.norepinephrine * 0.3
            - nt.gaba * 0.2
        )
        self._emit(self._make_signal(
            target="thalamus",
            signal_type="arousal",
            content={"arousal_drive": self.arousal_drive, "tick": self.vital_rhythm},
            strength=max(0.1, min(1.0, arousal_signal_strength)),
            arousal=self.arousal_drive,
        ))

        # Si menace détectée → signal d'urgence direct vers l'amygdale
        if threat_level > 0.5:
            self.threat_detected = True
            self._emit(self._make_signal(
                target="amygdala",
                signal_type="sensory",
                content={"threat": threat_level, "source": "brainstem_rapid"},
                strength=threat_level,
                valence=-(threat_level),
                arousal=min(1.0, threat_level * 1.2),
            ))
            # Noradrénaline → burst d'éveil (fight-or-flight)
            nt.modulate({"norepinephrine": threat_level * 0.3, "cortisol": 0.05})
        else:
            self.threat_detected = False

        # Rythme vital — oscillation sinusoïdale simulant le cycle veille/activité
        # (très simplifié: le vrai cycle circadien est sur ~24h)
        circadian_phase = math.sin(self.vital_rhythm * 0.1) * 0.1
        if circadian_phase < -0.05:
            # Phase basse → légère inhibition générale
            nt.modulate({"gaba": 0.01, "norepinephrine": -0.01})
