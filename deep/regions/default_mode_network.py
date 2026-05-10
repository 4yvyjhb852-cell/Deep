"""
Réseau du Mode par Défaut (Default Mode Network — DMN)

Le DMN est actif au REPOS — quand on ne fait rien de particulier.
C'est le réseau de la vie intérieure, de la rumination, de la créativité,
et du sens du soi.

Rôles:
- Pensée auto-référentielle ("je", "moi", "mon histoire")
- Rumination et pensée spontanée (mind-wandering)
- Imagination et simulation mentale (simuler le futur, se souvenir du passé)
- Intégration narrative du soi (raconter l'histoire de soi-même)
- Empathie et mentalisation (imaginer l'état mental d'autrui)
- Créativité (associations libres entre concepts distants)

Paradoxe: actif au repos = "cher en énergie même sans tâche"
Le DMN est INHIBÉ pendant les tâches qui nécessitent de l'attention externe.
Quand l'attention est mobilisée vers l'extérieur → DMN se tait.
Quand l'attention se relâche → DMN s'active.

Ce réseau est lié à la dépression (rumination excessive),
à la méditation (silence du DMN = présence), et à la créativité.
"""
from __future__ import annotations
import random
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


class DefaultModeNetwork(BrainRegion):
    def __init__(self):
        super().__init__("default_mode_network", capacity=10)
        self.self_model: dict = {
            "identity_coherence": 0.7,    # Sentiment de cohérence identitaire
            "narrative_strength": 0.5,    # Force du récit de soi
            "rumination_tendency": 0.3,   # Tendance à la rumination
        }
        self.mind_wandering: bool = False
        self.creative_associations: list[tuple] = []  # Associations créatives
        self.daydream_content: str = ""

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        # Le DMN est inhibé si l'attention externe est forte
        external_demands = sum(
            s.strength for s in signals
            if s.signal_type in ("sensory", "executive")
        )

        # Le DMN s'active en l'absence de demandes externes
        dmn_activation = max(0.0, 0.7 - external_demands * 0.8)
        dmn_activation *= max(0.2, 1.0 - nt.norepinephrine * 0.5)  # NE inhibe le DMN

        self.activation = self.activation * 0.6 + dmn_activation * 0.4

        if self.activation < 0.2:
            self.mind_wandering = False
            return

        # --- Mind-wandering ---
        self.mind_wandering = True

        # Type de pensée spontanée selon l'état neurochimique
        valence_mood = nt.mood_valence
        stress = nt.stress_level
        serotonin = nt.serotonin

        if stress > 0.6 and serotonin < 0.4:
            # Rumination anxieuse
            thought_type = "rumination"
            thought_valence = -0.5
            self.self_model["rumination_tendency"] = min(1.0,
                self.self_model["rumination_tendency"] + 0.02
            )
            nt.modulate({"serotonin": -0.01, "cortisol": 0.01})

        elif valence_mood > 0.3 and nt.dopamine > 0.5:
            # Rêverie créative positive
            thought_type = "creative_daydream"
            thought_valence = 0.4
            # Les associations créatives = connexions entre concepts distants
            self._generate_creative_association()
            nt.modulate({"dopamine": 0.005})

        elif nt.serotonin > 0.6:
            # Réflexion narrative positive (intégration du soi)
            thought_type = "self_narrative"
            thought_valence = 0.2
            self.self_model["narrative_strength"] = min(1.0,
                self.self_model["narrative_strength"] + 0.01
            )
            self.self_model["identity_coherence"] = min(1.0,
                self.self_model["identity_coherence"] + 0.005
            )
        else:
            # Errance mentale neutre
            thought_type = "mind_wandering"
            thought_valence = 0.0

        # Émission: les pensées du DMN peuvent remonter à la conscience (PFC)
        if self.activation > 0.4:
            self._emit(self._make_signal(
                target="prefrontal_cortex",
                signal_type="internal",
                content={
                    "thought_type":       thought_type,
                    "dmn_activation":     round(self.activation, 3),
                    "self_model":         self.self_model.copy(),
                    "creative_count":     len(self.creative_associations),
                    "mind_wandering":     self.mind_wandering,
                },
                strength=self.activation * 0.5,
                valence=thought_valence,
                arousal=self.activation * 0.3,  # Le DMN est peu aroused
            ))

    def _generate_creative_association(self) -> None:
        """Simule une association créative entre deux concepts."""
        concepts = ["memory", "emotion", "future", "self", "other", "pattern",
                    "structure", "flow", "emergence", "connection"]
        if len(concepts) >= 2:
            a = random.choice(concepts)
            b = random.choice([c for c in concepts if c != a])
            assoc = (a, b, round(random.uniform(0.3, 1.0), 2))
            self.creative_associations.append(assoc)
            if len(self.creative_associations) > 20:
                self.creative_associations.pop(0)

    def get_state(self) -> dict:
        base = super().get_state()
        base.update({
            "mind_wandering":       self.mind_wandering,
            "self_model":           {k: round(v, 3) for k, v in self.self_model.items()},
            "creative_associations": len(self.creative_associations),
        })
        return base
