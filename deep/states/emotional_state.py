"""
Tracker d'état émotionnel émergent.

Les émotions ne sont pas programmées directement — elles ÉMERGENT
de l'interaction entre:
- L'amygdale (évaluation de la saillance)
- L'insula (ressenti corporel)
- Les neurotransmetteurs (bain chimique)

Modèle dimensionnel de Russell (1980):
- Valence: négatif → positif
- Arousal: calme → excité

Les étiquettes émotionnelles émergent des positions dans cet espace.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deep.regions.amygdala import Amygdala
    from deep.regions.insula import Insula
    from deep.core.neurotransmitter import NeurotransmitterSystem


# Carte des émotions dans l'espace valence × arousal (modèle circomplexe)
# Format: (min_valence, max_valence, min_arousal, max_arousal) → label
EMOTION_MAP = [
    # Haute arousal, valence positive
    ( 0.5,  1.0,  0.65, 1.0, "joy",           "joie / euphorie"),
    ( 0.25, 0.7,  0.55, 0.9, "excitement",    "excitation / enthousiasme"),
    ( 0.15, 0.55, 0.45, 0.75,"interest",      "intérêt / curiosité"),
    ( 0.3,  0.8,  0.35, 0.7, "enthusiasm",    "enthousiasme / élan"),

    # Arousal moyen, valence positive
    ( 0.3,  0.7,  0.25, 0.55,"pleasure",      "plaisir / bien-être"),
    ( 0.2,  0.6,  0.15, 0.45,"satisfaction",  "satisfaction / plaisir"),

    # Basse arousal, valence positive
    ( 0.35, 1.0,  0.0,  0.35,"contentment",   "contentement / sérénité"),
    ( 0.1,  0.45, 0.0,  0.25,"calm",          "calme / relaxation"),
    ( 0.45, 1.0,  0.15, 0.5, "happiness",     "bonheur / épanouissement"),

    # Haute arousal, valence négative
    (-1.0, -0.45, 0.6,  1.0, "fear",          "peur / terreur"),
    (-0.7, -0.25, 0.5,  0.9, "anger",         "colère / frustration"),
    (-0.5, -0.15, 0.45, 0.8, "anxiety",       "anxiété / inquiétude"),
    (-0.8, -0.35, 0.7,  1.0, "panic",         "panique / détresse"),
    (-0.6, -0.2,  0.35, 0.65,"unease",        "malaise / tension"),

    # Basse arousal, valence négative
    (-1.0, -0.35, 0.0,  0.45,"sadness",       "tristesse / mélancolie"),
    (-0.5, -0.05, 0.05, 0.35,"boredom",       "ennui / apathie"),
    (-0.6, -0.15, 0.0,  0.2, "depression",    "abattement / déprime"),
    (-0.4, -0.1,  0.15, 0.45,"melancholy",    "mélancolie / nostalgie"),

    # Zone centrale (large, couvre l'espace indéfini)
    (-0.3,  0.3,  0.15, 0.55,"neutral",       "neutre / équilibré"),
    (-0.15, 0.35, 0.35, 0.65,"alert",         "alerte / attentif"),
    (-0.2,  0.2,  0.55, 0.85,"aroused",       "éveillé / activé"),
    (-0.3,  0.15, 0.0,  0.2, "tired",         "fatigué / somnolent"),
    ( 0.0,  0.4,  0.0,  0.5, "serene",        "serein / tranquille"),
]


def _label_emotion(valence: float, arousal: float) -> tuple[str, str]:
    """Trouve l'étiquette émotionnelle correspondant à (valence, arousal)."""
    candidates = []
    for min_v, max_v, min_a, max_a, label, label_fr in EMOTION_MAP:
        if min_v <= valence <= max_v and min_a <= arousal <= max_a:
            # Distance au centre de la zone
            center_v = (min_v + max_v) / 2
            center_a = (min_a + max_a) / 2
            dist = ((valence - center_v)**2 + (arousal - center_a)**2) ** 0.5
            candidates.append((dist, label, label_fr))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1], candidates[0][2]
    return "undefined", "indéfini"


class EmotionalStateTracker:
    """Suit l'état émotionnel émergent du cerveau."""

    def __init__(self):
        self._valence: float = 0.0
        self._arousal: float = 0.3
        self._label: str = "neutral"
        self._label_fr: str = "neutre"
        self._intensity: float = 0.0
        self._history: list[dict] = []
        self._dominant_emotion_duration: int = 0
        self._last_label: str = "neutral"

    def update(
        self,
        amygdala: "Amygdala",
        insula: "Insula",
        nt: "NeurotransmitterSystem",
    ) -> None:
        """Met à jour l'état émotionnel à partir de multiples sources."""

        # Valence: combinaison amygdale + insula + neurotransmetteurs
        amygdala_valence = amygdala.emotional_valence
        insula_valence   = insula.felt_emotion.get("valence", 0.0)
        nt_valence       = nt.mood_valence

        # Intégration pondérée (l'amygdale a le plus de poids)
        integrated_valence = (
            amygdala_valence * 0.4
            + insula_valence * 0.3
            + nt_valence * 0.3
        )

        # Arousal: combinaison amygdale + insula + noradrénaline
        amygdala_arousal = amygdala.emotional_arousal
        insula_arousal   = insula.felt_emotion.get("arousal", 0.3)
        nt_arousal       = nt.arousal_level

        integrated_arousal = (
            amygdala_arousal * 0.4
            + insula_arousal * 0.3
            + nt_arousal * 0.3
        )

        # Lissage temporel — plus rapide pour les signaux intenses (inertie adaptative)
        intensity_factor = min(1.0, abs(integrated_valence) + integrated_arousal)
        smoothing = max(0.4, 0.7 - intensity_factor * 0.3)
        self._valence = self._valence * smoothing + integrated_valence * (1 - smoothing)
        self._arousal = self._arousal * smoothing + integrated_arousal * (1 - smoothing)

        # Intensité émotionnelle
        self._intensity = (abs(self._valence) + self._arousal) / 2

        # Étiquette émotionnelle
        self._label, self._label_fr = _label_emotion(self._valence, self._arousal)

        # Durée de l'émotion dominante
        if self._label == self._last_label:
            self._dominant_emotion_duration += 1
        else:
            self._dominant_emotion_duration = 1
        self._last_label = self._label

        # Historique
        self._history.append({
            "valence":   round(self._valence, 3),
            "arousal":   round(self._arousal, 3),
            "label":     self._label,
            "intensity": round(self._intensity, 3),
        })
        if len(self._history) > 100:
            self._history.pop(0)

    def current_state(self) -> dict:
        return {
            "label":     self._label,
            "label_fr":  self._label_fr,
            "valence":   round(self._valence, 3),
            "arousal":   round(self._arousal, 3),
            "intensity": round(self._intensity, 3),
            "duration":  self._dominant_emotion_duration,
        }

    def get_history(self) -> list[dict]:
        return list(self._history)
