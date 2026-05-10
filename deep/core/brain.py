"""
Brain — L'orchestrateur central.

Le cerveau est la somme de ses régions, mais aussi plus que cette somme.
Les propriétés émergentes (émotions, conscience, état de soi) apparaissent
de l'INTERACTION entre les régions, pas d'une région seule.

Architecture de communication:
- Chaque région émet des signaux avec une cible nommée
- Le Brain route ces signaux vers les régions cibles
- Certains signaux sont "broadcast" (réseau global)
- Les neurotransmetteurs sont partagés globalement (état chimique du cerveau)

Théorie sous-jacente: Global Workspace Theory (Baars)
- Les régions spécialisées traitent en parallèle
- Un "espace de travail global" permet la diffusion large des informations
- La conscience émerge quand un signal gagne l'accès à cet espace global
"""
from __future__ import annotations
from typing import Any
import time

from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem
from deep.regions.brainstem import Brainstem
from deep.regions.thalamus import Thalamus
from deep.regions.amygdala import Amygdala
from deep.regions.hippocampus import Hippocampus
from deep.regions.prefrontal_cortex import PrefrontalCortex
from deep.regions.basal_ganglia import BasalGanglia
from deep.regions.cerebellum import Cerebellum
from deep.regions.insula import Insula
from deep.regions.cingulate_cortex import CingulateCortex
from deep.regions.sensory_cortex import SensoryCortex
from deep.regions.default_mode_network import DefaultModeNetwork
from deep.states.emotional_state import EmotionalStateTracker
from deep.states.consciousness import ConsciousnessMonitor


class Brain:
    """
    Le cerveau complet. Orchestre toutes les régions.
    """

    def __init__(self):
        # Système de neurotransmetteurs partagé
        self.nt = NeurotransmitterSystem()

        # Régions cérébrales
        self.brainstem    = Brainstem()
        self.thalamus     = Thalamus()
        self.amygdala     = Amygdala()
        self.hippocampus  = Hippocampus()
        self.pfc          = PrefrontalCortex()
        self.basal_ganglia = BasalGanglia()
        self.cerebellum   = Cerebellum()
        self.insula       = Insula()
        self.cingulate    = CingulateCortex()
        self.sensory_cortex = SensoryCortex()
        self.dmn          = DefaultModeNetwork()

        # Carte des régions par nom
        self._regions = {
            "brainstem":          self.brainstem,
            "thalamus":           self.thalamus,
            "amygdala":           self.amygdala,
            "hippocampus":        self.hippocampus,
            "prefrontal_cortex":  self.pfc,
            "basal_ganglia":      self.basal_ganglia,
            "cerebellum":         self.cerebellum,
            "insula":             self.insula,
            "cingulate_cortex":   self.cingulate,
            "sensory_cortex":     self.sensory_cortex,
            "default_mode_network": self.dmn,
        }

        # Suivi des états émergents
        self.emotional_tracker = EmotionalStateTracker()
        self.consciousness_monitor = ConsciousnessMonitor()

        # Journal de la simulation
        self._tick: int = 0
        self._output_log: list[dict] = []
        self._action_history: list[str] = []
        self.last_action: str | None = None

    # -------------------------------------------------------------------------
    # Interface publique
    # -------------------------------------------------------------------------

    def perceive(self, stimulus: dict[str, Any]) -> dict:
        """
        Point d'entrée principal: soumet un stimulus sensoriel au cerveau.
        Retourne l'état émergent après traitement.
        """
        signal = NeuralSignal(
            source="environment",
            target="brainstem",
            signal_type="sensory",
            content=stimulus,
            strength=stimulus.get("intensity", 0.5),
            valence=stimulus.get("valence", 0.0),
            arousal=stimulus.get("arousal", 0.3),
        )
        self.brainstem.receive(signal)
        self.thalamus.receive(signal)   # Double voie: rapide (tronc) et lente (thalamus)
        return self.tick()

    def tick(self) -> dict:
        """
        Avance d'un cycle de traitement (une "pensée").
        Toutes les régions traitent leurs signaux en parallèle,
        puis les signaux sont échangés.
        """
        self._tick += 1

        # Chaque région traite ses signaux entrants et émet des signaux sortants
        all_emitted: list[NeuralSignal] = []
        for region in self._regions.values():
            emitted = region.process(self.nt)
            all_emitted.extend(emitted)

        # Routage des signaux émis vers les régions cibles
        for signal in all_emitted:
            target = signal.target
            if target in self._regions:
                self._regions[target].receive(signal)
            elif target == "output":
                # Signal de sortie motrice → action
                action = signal.content.get("action")
                if action:
                    self.last_action = action
                    self._action_history.append(action)
                    if len(self._action_history) > 100:
                        self._action_history.pop(0)
            elif target == "broadcast":
                # Diffusion à toutes les régions (Global Workspace)
                for region in self._regions.values():
                    region.receive(signal)

        # Le DMN reçoit un signal vide à chaque tick pour s'activer au repos
        self.dmn.receive(NeuralSignal(
            source="brain",
            target="default_mode_network",
            signal_type="internal",
            content={"tick": self._tick},
            strength=0.1,
        ))

        # Homéostasie neurochimique
        self.nt.decay_to_baseline()

        # Mise à jour des états émergents
        self.emotional_tracker.update(self.amygdala, self.insula, self.nt)
        self.consciousness_monitor.update(
            self.pfc, self.thalamus, self.dmn, all_emitted, self._tick
        )

        state = self.get_state()
        self._output_log.append(state)
        if len(self._output_log) > 200:
            self._output_log.pop(0)

        return state

    def inject_reward(self, reward_value: float) -> None:
        """Injecte un signal de récompense (feedback d'une action)."""
        signal = NeuralSignal(
            source="environment",
            target="basal_ganglia",
            signal_type="reward",
            content={"reward_received": reward_value},
            strength=abs(reward_value),
            valence=reward_value,
        )
        self.basal_ganglia.receive(signal)
        # La récompense module aussi l'amygdale et les neurotransmetteurs
        if reward_value > 0:
            self.nt.modulate({"dopamine": reward_value * 0.1,
                              "serotonin": reward_value * 0.03})
        else:
            self.nt.modulate({"cortisol": abs(reward_value) * 0.05})

    # -------------------------------------------------------------------------
    # État global
    # -------------------------------------------------------------------------

    def get_state(self) -> dict:
        """Retourne l'état complet du cerveau à ce tick."""
        return {
            "tick": self._tick,
            "timestamp": time.time(),
            # États des régions
            "regions": {name: region.get_state()
                        for name, region in self._regions.items()},
            # Neurotransmetteurs
            "neurotransmitters": self.nt.snapshot(),
            # États émergents
            "emotional_state":   self.emotional_tracker.current_state(),
            "consciousness":     self.consciousness_monitor.current_state(),
            # Action courante
            "last_action":       self.last_action,
        }

    def get_summary(self) -> dict:
        """Résumé compact de l'état pour affichage."""
        emo = self.emotional_tracker.current_state()
        con = self.consciousness_monitor.current_state()
        return {
            "tick":        self._tick,
            "emotion":     emo.get("label", "unknown"),
            "valence":     round(self.nt.mood_valence, 3),
            "arousal":     round(self.nt.arousal_level, 3),
            "stress":      round(self.nt.stress_level, 3),
            "motivation":  round(self.nt.motivation, 3),
            "action":      self.last_action,
            "consciousness_level": round(con.get("level", 0), 3),
            "mind_wandering": self.dmn.mind_wandering,
            "pfc_load":    round(self.pfc.cognitive_load, 3),
        }
