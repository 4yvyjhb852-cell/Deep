"""
Cortex Cingulaire Antérieur (Anterior Cingulate Cortex — ACC)

L'ACC est le "moniteur de conflits" du cerveau — il détecte quand quelque
chose ne va pas, quand il y a un conflit entre des tendances contraires.

Rôles:
- Détection de conflits (deux réponses concurrentes activées simultanément)
- Monitoring d'erreur (ERN — Error-Related Negativity: "j'ai fait une erreur!")
- Régulation de la douleur (composante affective de la douleur)
- Attention à la douleur et à la détresse
- Régulation émotionnelle (interface cognition–émotion)
- Décision sous incertitude morale
- Conscience de ses propres états mentaux

L'ACC "sonne l'alarme" lorsqu'il détecte un problème, mobilisant
les ressources cognitives pour corriger le cours de l'action.

Connexions: Insula → ACC (signaux intéroceptifs)
            ACC ↔ PFC (monitoring d'erreur → adaptation)
            ACC → Amygdale (régulation descendante)
            ACC → Thalamus (allocation d'attention)
"""
from __future__ import annotations
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


class CingulateCortex(BrainRegion):
    def __init__(self):
        super().__init__("cingulate_cortex", capacity=15)
        self.conflict_level: float = 0.0
        self.error_signal: float = 0.0
        self.pain_affect: float = 0.0       # Composante affective de la douleur
        self.distress_level: float = 0.0    # Détresse globale

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        interoceptive = [s for s in signals if s.signal_type == "interoceptive"]
        predictive    = [s for s in signals if s.signal_type == "predictive"]
        emotional     = [s for s in signals if s.signal_type == "emotional"]

        # --- Détection de conflits ---
        # Les signaux de très haute et très basse valence simultanés = conflit
        valences = [s.valence for s in signals if s.valence != 0]
        if len(valences) >= 2:
            max_v = max(valences)
            min_v = min(valences)
            if max_v > 0.3 and min_v < -0.3:
                self.conflict_level = min(1.0, (max_v - min_v) / 2)
            else:
                self.conflict_level *= 0.8
        else:
            self.conflict_level *= 0.8

        # --- Signal d'erreur ---
        for sig in predictive:
            pred_error = sig.content.get("prediction_error", 0.0)
            self.error_signal = max(self.error_signal * 0.7, pred_error)

        # --- Intégration intéroceptive ---
        for sig in interoceptive:
            felt = sig.content.get("felt_emotion", {})
            body = sig.content.get("body_state", {})
            pain = body.get("pain_level", 0.0)
            self.pain_affect = max(self.pain_affect * 0.8, pain)

            # Détresse = combinaison douleur + émotion négative + conflit
            intensity = felt.get("subjective_intensity", 0.0)
            neg_valence = max(0, -felt.get("valence", 0.0))
            self.distress_level = min(1.0,
                self.distress_level * 0.7
                + (neg_valence * 0.3 + pain * 0.3 + self.conflict_level * 0.2
                   + intensity * 0.2)
            )

        # --- Modulation neurochimique ---
        if self.distress_level > 0.4:
            # La détresse augmente le cortisol
            nt.modulate({"cortisol": self.distress_level * 0.02})
        if self.error_signal > 0.5:
            # Erreur détectée → boost d'attention (noradrénaline)
            nt.modulate({"norepinephrine": self.error_signal * 0.05})
        if self.conflict_level > 0.5:
            # Conflit → mobilisation de l'acétylcholine (attention fine)
            nt.modulate({"acetylcholine": self.conflict_level * 0.03})

        # --- Output: alarme vers le PFC si nécessaire ---
        alarm = max(self.conflict_level, self.error_signal, self.distress_level)
        if alarm > 0.2:
            self._emit(self._make_signal(
                target="prefrontal_cortex",
                signal_type="executive",
                content={
                    "conflict":    round(self.conflict_level, 3),
                    "error":       round(self.error_signal, 3),
                    "distress":    round(self.distress_level, 3),
                    "pain_affect": round(self.pain_affect, 3),
                    "alarm":       round(alarm, 3),
                },
                strength=alarm,
                valence=-self.distress_level,  # Signal de détresse = valence négative
                arousal=min(1.0, alarm * 1.2),
            ))

    def get_state(self) -> dict:
        base = super().get_state()
        base.update({
            "conflict":  round(self.conflict_level, 3),
            "error":     round(self.error_signal, 3),
            "pain":      round(self.pain_affect, 3),
            "distress":  round(self.distress_level, 3),
        })
        return base
