"""
Système de neurotransmetteurs — le "bain chimique" du cerveau.

Les neurotransmetteurs modulent TOUS les traitements régionaux.
Ils ne transportent pas d'information précise mais colorent et amplifient
les signaux, créant des états globaux (humeur, éveil, motivation…).

Modèle dimensionnel basé sur la neurochimie réelle:
- Dopamine    → motivation, récompense, apprentissage, concentration
- Sérotonine  → humeur, bien-être, tolérance au stress, régulation sociale
- Noradrénaline → éveil, attention, réponse au stress (fight-or-flight)
- Acétylcholine → mémoire, attention fine, plasticité
- GABA        → inhibition, calme, réduction anxiété
- Glutamate   → excitation, apprentissage, mémoire
- Cortisol    → hormone de stress (axe HPA)
- Ocytocine   → confiance, attachement, empathie
- Endorphines → plaisir, soulagement de la douleur
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np


# Niveaux de base (état "équilibré" au repos)
BASELINE = {
    "dopamine":       0.50,
    "serotonin":      0.60,
    "norepinephrine": 0.35,
    "acetylcholine":  0.50,
    "gaba":           0.55,
    "glutamate":      0.50,
    "cortisol":       0.25,
    "oxytocin":       0.40,
    "endorphins":     0.45,
}

# Vitesse de retour au niveau de base (récupération naturelle)
RECOVERY_RATE = {
    "dopamine":       0.05,
    "serotonin":      0.02,
    "norepinephrine": 0.08,
    "acetylcholine":  0.06,
    "gaba":           0.04,
    "glutamate":      0.07,
    "cortisol":       0.01,   # cortisol descend lentement
    "oxytocin":       0.03,
    "endorphins":     0.03,
}


@dataclass
class NeurotransmitterSystem:
    """
    État chimique global du cerveau.
    Chaque valeur est dans [0.0, 1.0].
    """
    dopamine:       float = 0.50
    serotonin:      float = 0.60
    norepinephrine: float = 0.35
    acetylcholine:  float = 0.50
    gaba:           float = 0.55
    glutamate:      float = 0.50
    cortisol:       float = 0.25
    oxytocin:       float = 0.40
    endorphins:     float = 0.45

    def _clamp(self, v: float) -> float:
        return max(0.0, min(1.0, v))

    def modulate(self, deltas: dict[str, float]) -> None:
        """Applique des variations à plusieurs neurotransmetteurs simultanément."""
        for nt, delta in deltas.items():
            if hasattr(self, nt):
                current = getattr(self, nt)
                setattr(self, nt, self._clamp(current + delta))

    def decay_to_baseline(self) -> None:
        """Retour progressif aux niveaux de base (homéostasie)."""
        for nt, base in BASELINE.items():
            rate = RECOVERY_RATE[nt]
            current = getattr(self, nt)
            new_val = current + (base - current) * rate
            setattr(self, nt, self._clamp(new_val))

    # --- Propriétés émergentes dérivées des neurotransmetteurs ---

    @property
    def mood_valence(self) -> float:
        """Valence de l'humeur (-1 négatif → +1 positif).
        Calibré pour que les NTs au repos donnent une valence légèrement positive (~0.1).
        """
        positive = (self.serotonin * 0.4 + self.dopamine * 0.3
                    + self.endorphins * 0.2 + self.oxytocin * 0.1)
        negative = (self.cortisol * 0.5 + max(0, self.norepinephrine - 0.6) * 0.3
                    + max(0, self.glutamate - 0.7) * 0.2)
        # *2 - 0.7 centre la baseline (~0.395) autour de 0.09 ≈ humeur neutre positive
        return max(-1.0, min(1.0, self._clamp(positive - negative) * 2 - 0.7))

    @property
    def arousal_level(self) -> float:
        """Niveau d'éveil global (0 endormi → 1 hypervigilant)."""
        return self._clamp(
            self.norepinephrine * 0.4 + self.dopamine * 0.3
            + self.glutamate * 0.2 - self.gaba * 0.3
        )

    @property
    def stress_level(self) -> float:
        """Niveau de stress (0 zen → 1 panique)."""
        return self._clamp(
            self.cortisol * 0.5 + self.norepinephrine * 0.3
            + max(0, self.glutamate - 0.5) * 0.2
            - self.gaba * 0.2 - self.serotonin * 0.1
        )

    @property
    def motivation(self) -> float:
        """Motivation / drive (0 apathique → 1 très motivé)."""
        return self._clamp(
            self.dopamine * 0.6 + self.norepinephrine * 0.2
            + self.endorphins * 0.1 - self.cortisol * 0.2
        )

    @property
    def social_openness(self) -> float:
        """Ouverture sociale (0 retrait → 1 très sociable)."""
        return self._clamp(
            self.oxytocin * 0.5 + self.serotonin * 0.3
            + self.endorphins * 0.1 - self.cortisol * 0.2
        )

    @property
    def memory_encoding_efficiency(self) -> float:
        """Efficacité d'encodage mémoriel."""
        return self._clamp(
            self.acetylcholine * 0.5 + self.dopamine * 0.2
            + self.norepinephrine * 0.2 - self.cortisol * 0.2
        )

    def snapshot(self) -> dict[str, float]:
        return {
            "dopamine":       self.dopamine,
            "serotonin":      self.serotonin,
            "norepinephrine": self.norepinephrine,
            "acetylcholine":  self.acetylcholine,
            "gaba":           self.gaba,
            "glutamate":      self.glutamate,
            "cortisol":       self.cortisol,
            "oxytocin":       self.oxytocin,
            "endorphins":     self.endorphins,
            # Propriétés émergentes
            "→ mood_valence":            round(self.mood_valence, 3),
            "→ arousal_level":           round(self.arousal_level, 3),
            "→ stress_level":            round(self.stress_level, 3),
            "→ motivation":              round(self.motivation, 3),
            "→ social_openness":         round(self.social_openness, 3),
            "→ memory_encoding_efficiency": round(self.memory_encoding_efficiency, 3),
        }
