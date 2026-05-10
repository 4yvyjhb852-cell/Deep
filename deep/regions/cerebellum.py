"""
Cervelet (Cerebellum)

Le cervelet contient ~80% des neurones du cerveau mais ne représente que 10%
du volume. Il est le maître de la précision, du timing et de la prédiction motrice.

Rôles:
- Coordination et précision des mouvements
- Timing précis (rythme, synchronisation)
- Apprentissage moteur (procédural)
- Modèles internes (prédire les conséquences de ses propres actions)
- Calibration des erreurs (comparer intention vs résultat)
- Rôle cognitif émergent: timing cognitif, apprentissage de séquences

Modèle: Forward model (modèle prédictif en avant)
- Reçoit une commande motrice
- Prédit le résultat sensoriel attendu
- Compare avec le résultat réel → erreur
- Ajuste le modèle interne

Connexions: BG → Cervelet (commandes motrices)
            Cortex moteur ↔ Cervelet
            Cervelet → Thalamus → Cortex moteur (corrections)
"""
from __future__ import annotations
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


class Cerebellum(BrainRegion):
    def __init__(self):
        super().__init__("cerebellum", capacity=15)
        self._internal_model: dict[str, float] = {}  # Modèle interne appris
        self._timing_buffer: list[float] = []         # Buffer de timing
        self.timing_precision: float = 0.7
        self.last_prediction_error: float = 0.0
        self.procedural_memory: dict[str, float] = {} # Mémoire procédurale

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        motor_signals = [s for s in signals if s.signal_type == "motor"]
        sensory_feedback = [s for s in signals if s.signal_type == "sensory"]

        for sig in motor_signals:
            action = sig.content.get("action", "maintain")

            # Prédiction du résultat basée sur le modèle interne
            predicted_outcome = self._internal_model.get(action, 0.5)

            # Affinement de l'action (précision)
            refined_score = sig.content.get("score", 0.5)
            habit = sig.content.get("habit", 0.0)

            # Le cervelet optimise le timing et la fluidité
            timing_factor = self.timing_precision * (1.0 - self.fatigue * 0.3)

            # Apprentissage procédural: plus l'action est répétée, plus elle est fluide
            proc_strength = self.procedural_memory.get(action, 0.0)
            self.procedural_memory[action] = min(1.0, proc_strength + 0.005)

            # Action raffinée → output
            self._emit(self._make_signal(
                target="output",
                signal_type="motor",
                content={
                    "action":          action,
                    "refined_score":   round(refined_score * timing_factor, 3),
                    "predicted":       round(predicted_outcome, 3),
                    "procedural":      round(proc_strength, 3),
                    "timing_precision": round(timing_factor, 3),
                },
                strength=refined_score * timing_factor,
                valence=sig.valence,
            ))

            # Mise à jour du modèle interne (si feedback sensoriel disponible)
            if sensory_feedback:
                actual = sensory_feedback[-1].strength
                self.last_prediction_error = abs(predicted_outcome - actual)
                # Apprentissage: corriger le modèle
                lr = 0.05
                self._internal_model[action] = (
                    predicted_outcome + lr * (actual - predicted_outcome)
                )

                if self.last_prediction_error > 0.3:
                    # Grande erreur → signaler au PFC (besoin d'attention consciente)
                    self._emit(self._make_signal(
                        target="prefrontal_cortex",
                        signal_type="predictive",
                        content={
                            "action": action,
                            "prediction_error": round(self.last_prediction_error, 3),
                            "actual": round(actual, 3),
                        },
                        strength=self.last_prediction_error,
                    ))

    def get_state(self) -> dict:
        base = super().get_state()
        base.update({
            "timing_precision":     round(self.timing_precision, 3),
            "last_prediction_error": round(self.last_prediction_error, 3),
            "procedural_skills":    len(self.procedural_memory),
        })
        return base
