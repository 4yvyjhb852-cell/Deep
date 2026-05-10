"""
Deep Sanctuary — API publique

Interface simplifiée et documentée pour utiliser le cerveau de façon
programmatique. C'est l'entrée recommandée pour une IA ou un programme externe.

USAGE RAPIDE:
    from deep.api import DeepBrain
    brain = DeepBrain()
    result = brain.perceive({"modality": "visual", "valence": 0.5, "arousal": 0.4, "intensity": 0.6})
    print(result.emotion)        # ex: "serene"
    print(result.action)         # ex: "approach"
    print(result.consciousness)  # ex: 0.62
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from deep.core.brain import Brain
from deep.core.neurotransmitter import NeurotransmitterSystem


# ---------------------------------------------------------------------------
# Types de sortie
# ---------------------------------------------------------------------------

@dataclass
class PerceptionResult:
    """
    Résultat d'un cycle de perception.
    Retourné par DeepBrain.perceive() et DeepBrain.tick().
    """

    # --- État émotionnel ---
    emotion: str          # Étiquette anglaise: "joy","fear","sadness","calm","anxiety",...
    emotion_fr: str       # Étiquette française: "joie","peur","tristesse","calme",...
    valence: float        # Valence émotionnelle  -1.0 (très négatif) → +1.0 (très positif)
    arousal: float        # Niveau d'éveil        0.0 (calme) → 1.0 (très activé)
    emotion_intensity: float  # Intensité globale 0.0 → 1.0
    emotion_duration: int     # Nombre de ticks dans cet état émotionnel

    # --- Conscience ---
    consciousness: float     # Niveau de conscience 0.0 (inconscient) → 1.0 (hyperconscient)
    consciousness_label: str # "unconscious","subconscious","conscious","focused","heightened"
    meta_awareness: float    # Méta-conscience / introspection 0.0 → 1.0
    mind_wandering: bool     # Le cerveau est-il en rêverie (DMN actif)?

    # --- Décision / Action ---
    action: Optional[str]   # Action sélectionnée: "approach","avoid","explore","engage","maintain","rest"
    action_confidence: float # Confiance dans l'action 0.0 → 1.0

    # --- Charge cognitive ---
    cognitive_load: float   # Charge du PFC 0.0 → 1.0  (>0.9 = surcharge)
    pfc_fatigue: float      # Fatigue préfrontale 0.0 → 1.0

    # --- Neurochimie (résumé) ---
    stress: float           # Niveau de stress émergent 0.0 → 1.0
    motivation: float       # Motivation 0.0 → 1.0
    mood: float             # Humeur neurochimique -1.0 → +1.0

    # --- Mémoire ---
    memory_count: int        # Nombre de traces mnésiques actives
    last_encoded: bool       # Un souvenir vient-il d'être encodé ce tick?

    # --- Tick ---
    tick: int                # Numéro du cycle de traitement (temps interne)

    # --- Snapshot complet optionnel ---
    _full_state: dict = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict:
        """Sérialise en dictionnaire JSON-compatible."""
        return {
            "tick":               self.tick,
            "emotion":            self.emotion,
            "emotion_fr":         self.emotion_fr,
            "valence":            self.valence,
            "arousal":            self.arousal,
            "emotion_intensity":  self.emotion_intensity,
            "emotion_duration":   self.emotion_duration,
            "consciousness":      self.consciousness,
            "consciousness_label": self.consciousness_label,
            "meta_awareness":     self.meta_awareness,
            "mind_wandering":     self.mind_wandering,
            "action":             self.action,
            "action_confidence":  self.action_confidence,
            "cognitive_load":     self.cognitive_load,
            "pfc_fatigue":        self.pfc_fatigue,
            "stress":             self.stress,
            "motivation":         self.motivation,
            "mood":               self.mood,
            "memory_count":       self.memory_count,
            "last_encoded":       self.last_encoded,
        }

    def __str__(self) -> str:
        wander = " [mind-wandering]" if self.mind_wandering else ""
        return (
            f"[tick={self.tick}] "
            f"émotion={self.emotion_fr} "
            f"(v={self.valence:+.2f}, a={self.arousal:.2f}) | "
            f"action={self.action} | "
            f"conscience={self.consciousness:.2f} "
            f"[{self.consciousness_label}]{wander}"
        )


@dataclass
class NeurochemistryState:
    """Snapshot complet de la neurochimie."""
    dopamine:       float  # Motivation, récompense
    serotonin:      float  # Humeur, bien-être
    norepinephrine: float  # Éveil, attention
    acetylcholine:  float  # Mémoire, attention fine
    gaba:           float  # Inhibition, calme
    glutamate:      float  # Excitation
    cortisol:       float  # Stress
    oxytocin:       float  # Lien social
    endorphins:     float  # Plaisir, analgésie

    def to_dict(self) -> dict:
        return {
            "dopamine": self.dopamine, "serotonin": self.serotonin,
            "norepinephrine": self.norepinephrine, "acetylcholine": self.acetylcholine,
            "gaba": self.gaba, "glutamate": self.glutamate,
            "cortisol": self.cortisol, "oxytocin": self.oxytocin,
            "endorphins": self.endorphins,
        }


# ---------------------------------------------------------------------------
# Constantes: valeurs valides pour les inputs
# ---------------------------------------------------------------------------

VALID_MODALITIES = [
    "visual",       # Stimulus visuel
    "auditory",     # Stimulus auditif
    "tactile",      # Stimulus tactile
    "olfactory",    # Stimulus olfactif
    "taste",        # Stimulus gustatif
    "social",       # Interaction sociale
    "threat",       # Menace / danger
    "reward",       # Récompense
    "cognitive",    # Tâche cognitive / effort mental
    "internal",     # Pensée interne
    "music",        # Musique
    "pain",         # Douleur
    "unknown",      # Inconnu / ambigu
]

VALID_ACTIONS = ["approach", "avoid", "explore", "engage", "maintain", "rest"]

VALID_CONSCIOUSNESS_LABELS = [
    "unconscious",   # < 0.2
    "subconscious",  # 0.2–0.4
    "conscious",     # 0.4–0.65
    "focused",       # 0.65–0.85
    "heightened",    # > 0.85
]


# ---------------------------------------------------------------------------
# Interface principale
# ---------------------------------------------------------------------------

class DeepBrain:
    """
    Interface simplifiée pour le cerveau Deep Sanctuary.

    CYCLE DE VIE:
        brain = DeepBrain()
        result = brain.perceive(stimulus)   # Soumettre un stimulus
        brain.tick()                         # Avancer sans stimulus
        brain.reward(0.8)                    # Donner un feedback de récompense
        brain.inject({"cortisol": 0.3})     # Modifier directement des neurotransmetteurs

    TOUT EST NORMALISÉ entre 0.0 et 1.0 (sauf valence: -1.0 à +1.0).
    """

    def __init__(self):
        self._brain = Brain()

    # -----------------------------------------------------------------------
    # Méthodes principales
    # -----------------------------------------------------------------------

    def perceive(self, stimulus: dict) -> PerceptionResult:
        """
        Soumet un stimulus sensoriel au cerveau et retourne l'état résultant.

        PARAMÈTRES DU STIMULUS (tous optionnels sauf indication):
        ┌─────────────────┬──────────────┬────────────────────────────────────────────────┐
        │ Clé             │ Type / Range │ Description                                    │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ modality        │ str          │ Type de stimulus (voir VALID_MODALITIES)        │
        │                 │              │ défaut: "unknown"                              │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ intensity       │ float [0,1]  │ Intensité brute du stimulus                    │
        │                 │              │ défaut: 0.5                                    │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ valence         │ float [-1,1] │ Charge émotionnelle:                           │
        │                 │              │  -1.0 = très négatif/douloureux                │
        │                 │              │   0.0 = neutre                                 │
        │                 │              │  +1.0 = très positif/plaisant                  │
        │                 │              │ défaut: 0.0                                    │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ arousal         │ float [0,1]  │ Niveau d'activation:                           │
        │                 │              │  0.0 = endormant, 1.0 = très excitant          │
        │                 │              │ défaut: 0.3                                    │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ novelty         │ float [0,1]  │ Nouveauté du stimulus (inconnu → curiosité)    │
        │                 │              │ défaut: 0.5                                    │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ threat          │ float [0,1]  │ Niveau de menace/danger perçu                  │
        │                 │              │ défaut: 0.0                                    │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ reward          │ float [0,1]  │ Valeur de récompense immédiate                 │
        │                 │              │ défaut: 0.0                                    │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ pattern         │ str          │ Identifiant du pattern visuel/perceptuel        │
        │                 │              │ (pour la reconnaissance et l'habituation)       │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ stimulus_id     │ str          │ Identifiant unique du stimulus                 │
        │                 │              │ (pour le conditionnement et la mémoire)        │
        ├─────────────────┼──────────────┼────────────────────────────────────────────────┤
        │ location        │ str          │ Localisation spatiale (pour mémoire spatiale)  │
        └─────────────────┴──────────────┴────────────────────────────────────────────────┘

        RETOURNE: PerceptionResult (voir la classe)

        EXEMPLES:
            # Voir quelque chose de beau
            brain.perceive({"modality":"visual","valence":0.6,"arousal":0.4,"intensity":0.7})

            # Danger soudain
            brain.perceive({"modality":"threat","threat":0.9,"valence":-0.8,"arousal":0.95})

            # Interaction sociale positive
            brain.perceive({"modality":"social","reward":0.5,"valence":0.5,"arousal":0.4})

            # Tâche cognitive difficile
            brain.perceive({"modality":"cognitive","novelty":0.8,"intensity":0.9,"arousal":0.7})
        """
        state = self._brain.perceive(stimulus)
        return self._to_result(state)

    def tick(self) -> PerceptionResult:
        """
        Avance d'un cycle sans stimulus externe.
        Utile pour: laisser le cerveau se reposer, observer la décroissance
        des états, laisser le DMN s'activer (mind-wandering).

        RETOURNE: PerceptionResult
        """
        state = self._brain.tick()
        return self._to_result(state)

    def reward(self, value: float) -> None:
        """
        Injecte un signal de récompense/punition en retour d'une action.
        À appeler après perceive() si l'action produit un feedback.

        PARAMÈTRES:
            value: float [-1.0, 1.0]
                +1.0 = récompense maximale (renforce l'action)
                 0.0 = neutre
                -1.0 = punition maximale (inhibe l'action)

        EFFET: Modifie les valeurs d'action dans les noyaux gris,
               module la dopamine (TD-error).
        """
        self._brain.inject_reward(max(-1.0, min(1.0, value)))

    def inject(self, neurotransmitters: dict[str, float]) -> None:
        """
        Modifie directement les niveaux de neurotransmetteurs.
        Simule: médicaments, drogues, états physiologiques, interventions.

        PARAMÈTRES:
            neurotransmitters: dict avec les variations (delta, pas valeur absolue)
                Clés valides: "dopamine","serotonin","norepinephrine","acetylcholine",
                              "gaba","glutamate","cortisol","oxytocin","endorphins"
                Valeur: float [-1.0, +1.0] = delta appliqué au niveau actuel

        EXEMPLES:
            brain.inject({"serotonin": -0.3})         # Déprime sérotonine (dépression)
            brain.inject({"dopamine": 0.4})            # Boost dopamine (stimulant)
            brain.inject({"cortisol": 0.5})            # Stress intense
            brain.inject({"gaba": 0.3, "cortisol": -0.2})  # Anxiolytique
            brain.inject({"oxytocin": 0.2})            # Contact social/affectif
        """
        self._brain.nt.modulate(neurotransmitters)

    # -----------------------------------------------------------------------
    # Lecture d'état
    # -----------------------------------------------------------------------

    def get_neurochemistry(self) -> NeurochemistryState:
        """
        Retourne l'état neurochimique complet (valeurs absolues 0–1).

        RETOURNE: NeurochemistryState
        """
        nt = self._brain.nt
        return NeurochemistryState(
            dopamine=round(nt.dopamine, 3),
            serotonin=round(nt.serotonin, 3),
            norepinephrine=round(nt.norepinephrine, 3),
            acetylcholine=round(nt.acetylcholine, 3),
            gaba=round(nt.gaba, 3),
            glutamate=round(nt.glutamate, 3),
            cortisol=round(nt.cortisol, 3),
            oxytocin=round(nt.oxytocin, 3),
            endorphins=round(nt.endorphins, 3),
        )

    def get_region_activations(self) -> dict[str, float]:
        """
        Retourne le niveau d'activation de chaque région cérébrale (0–1).

        RÉGIONS:
            brainstem, thalamus, amygdala, hippocampus, prefrontal_cortex,
            basal_ganglia, cerebellum, insula, cingulate_cortex,
            sensory_cortex, default_mode_network
        """
        return {
            name: round(region.activation, 3)
            for name, region in self._brain._regions.items()
        }

    def get_memory_traces(self) -> list[dict]:
        """
        Retourne les traces mnésiques actives (mémoire épisodique).

        CHAQUE TRACE:
            episode_id:    int   — identifiant unique
            strength:      float — force de la trace (0=oublié, 1=fort)
            emotional_tag: float — marquage émotionnel (0=neutre, 1=intense)
            valence:       float — valence de l'épisode
            retrieval_count: int — nombre de récupérations
        """
        return [
            {
                "episode_id":     t.episode_id,
                "strength":       round(t.strength, 3),
                "emotional_tag":  round(t.emotional_tag, 3),
                "valence":        round(t.valence, 3),
                "retrieval_count": t.retrieval_count,
            }
            for t in self._brain.hippocampus._memory_traces
        ]

    def get_emotional_history(self) -> list[dict]:
        """
        Retourne l'historique des états émotionnels (jusqu'à 100 ticks).

        CHAQUE ENTRÉE: {"valence": float, "arousal": float, "label": str, "intensity": float}
        """
        return self._brain.emotional_tracker.get_history()

    @property
    def tick_count(self) -> int:
        """Nombre de cycles de traitement écoulés depuis la création."""
        return self._brain._tick

    # -----------------------------------------------------------------------
    # Conversion interne
    # -----------------------------------------------------------------------

    def _to_result(self, state: dict) -> PerceptionResult:
        emo = state["emotional_state"]
        con = state["consciousness"]
        nt  = self._brain.nt

        # Action depuis les noyaux gris
        bg_state = state["regions"].get("basal_ganglia", {})
        action = bg_state.get("selected_action") or state.get("last_action")

        # Confiance dans l'action
        pfc_state = state["regions"]["prefrontal_cortex"]

        # Dernier encodage mémoriel
        prev_count = getattr(self, "_prev_memory_count", 0)
        current_count = len(self._brain.hippocampus._memory_traces)
        last_encoded = current_count > prev_count
        self._prev_memory_count = current_count

        return PerceptionResult(
            tick=state["tick"],
            emotion=emo["label"],
            emotion_fr=emo["label_fr"],
            valence=emo["valence"],
            arousal=emo["arousal"],
            emotion_intensity=emo["intensity"],
            emotion_duration=emo["duration"],
            consciousness=con["level"],
            consciousness_label=con["label"],
            meta_awareness=con["meta_awareness"],
            mind_wandering=self._brain.dmn.mind_wandering,
            action=action,
            action_confidence=round(
                self._brain.basal_ganglia._action_values.get(action or "maintain", 0.5), 3
            ),
            cognitive_load=pfc_state.get("cognitive_load", 0.0),
            pfc_fatigue=pfc_state.get("fatigue", 0.0),
            stress=round(nt.stress_level, 3),
            motivation=round(nt.motivation, 3),
            mood=round(nt.mood_valence, 3),
            memory_count=current_count,
            last_encoded=last_encoded,
            _full_state=state,
        )
