#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         DEEP SANCTUARY v0.1                                 ║
║              Architecture Cognitive Humaine — Fichier Unique                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Simulation d'un cerveau humain où émotions, états et comportements          ║
║  ÉMERGENT de l'interaction entre composantes — sans être programmés          ║
║  directement.                                                                ║
║                                                                              ║
║  USAGE:                                                                      ║
║    python3 deep_sanctuary.py                    # expérience émotions        ║
║    python3 deep_sanctuary.py --demo             # démo rapide                ║
║    python3 deep_sanctuary.py --exp stress       # stress & récupération      ║
║    python3 deep_sanctuary.py --exp curiosity    # curiosité vs anxiété       ║
║    python3 deep_sanctuary.py --exp memory       # mémoire émotionnelle       ║
║    python3 deep_sanctuary.py --exp fatigue      # fatigue cognitive          ║
║    python3 deep_sanctuary.py --exp all          # toutes les expériences     ║
║    python3 deep_sanctuary.py --ticks 30         # simulation libre           ║
║                                                                              ║
║  API PYTHON:                                                                 ║
║    brain = DeepBrain()                                                       ║
║    r = brain.perceive({"modality":"threat","threat":0.8,"valence":-0.7,     ║
║                         "arousal":0.9,"intensity":0.9})                      ║
║    print(r.emotion, r.valence, r.action, r.stress)                          ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Bases théoriques:                                                           ║
║  • Global Workspace Theory (Baars, Dehaene)                                 ║
║  • Predictive Processing (Friston)                                           ║
║  • Somatic Marker Hypothesis (Damasio)                                       ║
║  • Hebbian Learning / LTP / LTD                                              ║
║  • Dimensional Emotion Model (Russell: Valence × Arousal)                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import argparse
import math
import random
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Optional

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — SIGNAL NEURAL
# Unité de communication entre les régions cérébrales
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NeuralSignal:
    """
    Unité fondamentale d'information circulant dans le cerveau.
    Modélise un potentiel d'action avec sa charge émotionnelle.
    """
    source:     str              # Région émettrice
    target:     str              # Région cible (ou "broadcast")
    signal_type: str             # sensory / emotional / mnemonic / executive / motor /
                                 # reward / arousal / predictive / interoceptive / internal
    content:    dict[str, Any]   # Contenu sémantique
    strength:   float = 1.0      # Intensité 0.0–1.0
    valence:    float = 0.0      # Valence émotionnelle -1.0 → +1.0
    arousal:    float = 0.5      # Niveau d'éveil 0.0 → 1.0
    timestamp:  float = field(default_factory=time.time)

    def __post_init__(self):
        self.strength = max(0.0, min(1.0, self.strength))
        self.valence  = max(-1.0, min(1.0, self.valence))
        self.arousal  = max(0.0, min(1.0, self.arousal))

    def attenuate(self, factor: float) -> "NeuralSignal":
        return NeuralSignal(
            source=self.source, target=self.target,
            signal_type=self.signal_type, content=self.content.copy(),
            strength=self.strength * factor, valence=self.valence,
            arousal=self.arousal * factor, timestamp=self.timestamp,
        )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — NEUROTRANSMETTEURS
# Bain chimique global modulant tous les traitements
# ─────────────────────────────────────────────────────────────────────────────

BASELINE_NT = {
    "dopamine": 0.50, "serotonin": 0.60, "norepinephrine": 0.35,
    "acetylcholine": 0.50, "gaba": 0.55, "glutamate": 0.50,
    "cortisol": 0.25, "oxytocin": 0.40, "endorphins": 0.45,
}
RECOVERY_RATE = {
    "dopamine": 0.05, "serotonin": 0.02, "norepinephrine": 0.08,
    "acetylcholine": 0.06, "gaba": 0.04, "glutamate": 0.07,
    "cortisol": 0.01, "oxytocin": 0.03, "endorphins": 0.03,
}

@dataclass
class NeurotransmitterSystem:
    """
    État neurochimique global du cerveau. Valeurs dans [0.0, 1.0].
    Les propriétés émergentes (humeur, stress, motivation...) se calculent
    automatiquement depuis ces niveaux.
    """
    dopamine:       float = 0.50   # Récompense, motivation, apprentissage
    serotonin:      float = 0.60   # Humeur, bien-être, tolérance stress
    norepinephrine: float = 0.35   # Éveil, attention, fight-or-flight
    acetylcholine:  float = 0.50   # Mémoire, attention fine
    gaba:           float = 0.55   # Inhibition, calme, anti-anxiété
    glutamate:      float = 0.50   # Excitation, apprentissage
    cortisol:       float = 0.25   # Stress (axe HPA)
    oxytocin:       float = 0.40   # Lien social, confiance
    endorphins:     float = 0.45   # Plaisir, analgésie

    def _c(self, v: float) -> float:
        return max(0.0, min(1.0, v))

    def modulate(self, deltas: dict[str, float]) -> None:
        for k, d in deltas.items():
            if hasattr(self, k):
                setattr(self, k, self._c(getattr(self, k) + d))

    def decay_to_baseline(self) -> None:
        for nt, base in BASELINE_NT.items():
            rate = RECOVERY_RATE[nt]
            cur = getattr(self, nt)
            setattr(self, nt, self._c(cur + (base - cur) * rate))

    @property
    def mood_valence(self) -> float:
        pos = self.serotonin * 0.4 + self.dopamine * 0.3 + self.endorphins * 0.2 + self.oxytocin * 0.1
        neg = self.cortisol * 0.5 + max(0, self.norepinephrine - 0.6) * 0.3 + max(0, self.glutamate - 0.7) * 0.2
        return max(-1.0, min(1.0, self._c(pos - neg) * 2 - 0.7))

    @property
    def arousal_level(self) -> float:
        return self._c(self.norepinephrine * 0.4 + self.dopamine * 0.3 + self.glutamate * 0.2 - self.gaba * 0.3)

    @property
    def stress_level(self) -> float:
        return self._c(self.cortisol * 0.5 + self.norepinephrine * 0.3 + max(0, self.glutamate - 0.5) * 0.2 - self.gaba * 0.2 - self.serotonin * 0.1)

    @property
    def motivation(self) -> float:
        return self._c(self.dopamine * 0.6 + self.norepinephrine * 0.2 + self.endorphins * 0.1 - self.cortisol * 0.2)

    @property
    def social_openness(self) -> float:
        return self._c(self.oxytocin * 0.5 + self.serotonin * 0.3 + self.endorphins * 0.1 - self.cortisol * 0.2)

    @property
    def memory_encoding_efficiency(self) -> float:
        return self._c(self.acetylcholine * 0.5 + self.dopamine * 0.2 + self.norepinephrine * 0.2 - self.cortisol * 0.2)

    def snapshot(self) -> dict:
        return {k: round(getattr(self, k), 3) for k in BASELINE_NT}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — RÉGION CÉRÉBRALE (CLASSE DE BASE)
# ─────────────────────────────────────────────────────────────────────────────

class BrainRegion(ABC):
    def __init__(self, name: str, capacity: int = 10):
        self.name = name
        self.activation: float = 0.0
        self.fatigue:    float = 0.0
        self._input_buffer: deque[NeuralSignal] = deque(maxlen=capacity)
        self._output_buffer: list[NeuralSignal] = []
        self._history: list[dict] = []
        self._tick: int = 0
        self._fatigue_managed_internally: bool = False

    def receive(self, signal: NeuralSignal) -> None:
        self._input_buffer.append(signal)

    def process(self, nt: NeurotransmitterSystem) -> list[NeuralSignal]:
        self._tick += 1
        signals_in = list(self._input_buffer)
        self._input_buffer.clear()
        self._output_buffer = []

        if signals_in:
            avg_strength = sum(s.strength for s in signals_in) / len(signals_in)
            self.activation = min(1.0, self.activation * 0.7 + avg_strength * 0.3)
            self._process_signals(signals_in, nt)
        else:
            self.activation *= 0.85

        if not self._fatigue_managed_internally:
            if self.activation > 0.15:
                self.fatigue = min(1.0, self.fatigue + (self.activation - 0.15) * 0.05)
            elif len(signals_in) == 0:
                self.fatigue = max(0.0, self.fatigue - 0.008)

        self._history.append({"tick": self._tick, "activation": round(self.activation, 3), "fatigue": round(self.fatigue, 3)})
        if len(self._history) > 500:
            self._history.pop(0)
        return list(self._output_buffer)

    @abstractmethod
    def _process_signals(self, signals: list[NeuralSignal], nt: NeurotransmitterSystem) -> None: ...

    def _emit(self, s: NeuralSignal) -> None:
        self._output_buffer.append(s)

    def _make(self, target, stype, content, strength=0.5, valence=0.0, arousal=0.5) -> NeuralSignal:
        return NeuralSignal(
            source=self.name, target=target, signal_type=stype, content=content,
            strength=max(0.0, min(1.0, strength * (1.0 - self.fatigue * 0.5))),
            valence=valence, arousal=arousal,
        )

    def get_state(self) -> dict:
        return {"region": self.name, "activation": round(self.activation, 3), "fatigue": round(self.fatigue, 3)}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — LES 11 RÉGIONS CÉRÉBRALES
# ─────────────────────────────────────────────────────────────────────────────

class Brainstem(BrainRegion):
    """Tronc cérébral: éveil, survie, SRAA, réponse fight-or-flight."""
    def __init__(self):
        super().__init__("brainstem", 20)
        self.arousal_drive = 0.4
        self.vital_rhythm  = 0

    def _process_signals(self, signals, nt):
        self.vital_rhythm += 1
        threat_level = max_arousal = 0.0
        for s in signals:
            if s.signal_type == "sensory":
                threat_level = max(threat_level, s.content.get("threat", 0) * s.strength)
                max_arousal  = max(max_arousal, s.strength * s.content.get("novelty", 0.3))

        self.arousal_drive = min(1.0, max(0.1, self.arousal_drive * 0.8 + max_arousal * 0.2 + nt.norepinephrine * 0.1))
        self._emit(self._make("thalamus", "arousal",
            {"arousal_drive": self.arousal_drive, "tick": self.vital_rhythm},
            strength=max(0.1, min(1.0, self.arousal_drive + nt.norepinephrine * 0.3 - nt.gaba * 0.2)),
            arousal=self.arousal_drive))

        if threat_level > 0.5:
            self._emit(self._make("amygdala", "sensory",
                {"threat": threat_level, "source": "brainstem_rapid"},
                strength=threat_level, valence=-threat_level, arousal=min(1.0, threat_level * 1.2)))
            nt.modulate({"norepinephrine": threat_level * 0.3, "cortisol": 0.05})

        if math.sin(self.vital_rhythm * 0.1) < -0.05:
            nt.modulate({"gaba": 0.01, "norepinephrine": -0.01})


class Thalamus(BrainRegion):
    """Routeur sensoriel, porte attentionnelle (top-down + bottom-up)."""
    def __init__(self):
        super().__init__("thalamus", 30)
        self.attention_gate = 0.5

    def _process_signals(self, signals, nt):
        arousal_in = sensory = executive = 0.0
        sensory_signals = []
        for s in signals:
            if s.signal_type == "arousal":   arousal_in = max(arousal_in, s.strength)
            elif s.signal_type == "sensory": sensory_signals.append(s)
            elif s.signal_type == "executive": executive = max(executive, s.content.get("attention_direction", 0.5))

        top_down = executive if executive > 0 else self.attention_gate
        self.attention_gate = min(1.0, max(0.1,
            arousal_in * 0.3 + top_down * 0.3 + nt.acetylcholine * 0.2 + nt.norepinephrine * 0.1 - nt.gaba * 0.2))

        for s in sensory_signals:
            rs = s.strength * self.attention_gate
            if rs > 0.05:
                self._emit(NeuralSignal("thalamus", "sensory_cortex", "sensory",
                    s.content, rs, s.valence, s.arousal * self.attention_gate))
            if s.content.get("threat", 0) > 0.2 or s.valence < -0.3:
                self._emit(NeuralSignal("thalamus", "amygdala", "sensory",
                    s.content, s.strength * 0.8, s.valence, s.arousal))

        self._emit(self._make("prefrontal_cortex", "arousal",
            {"attention_gate": self.attention_gate, "arousal": arousal_in},
            strength=self.attention_gate, arousal=arousal_in))


class Amygdala(BrainRegion):
    """Évaluation émotionnelle rapide, peur/récompense, conditionnement."""
    def __init__(self):
        super().__init__("amygdala", 20)
        self.fear_level        = 0.0
        self.reward_signal     = 0.0
        self.emotional_valence = 0.0
        self.emotional_arousal = 0.0
        self._conditioning: dict[str, float] = {}

    def _process_signals(self, signals, nt):
        max_threat = max_reward = total_v = total_a = 0.0
        n = len(signals)
        for s in signals:
            t = s.content.get("threat", 0.0)
            r = s.content.get("reward", 0.0)
            sid = s.content.get("stimulus_id", "")
            if sid and sid in self._conditioning:
                c = self._conditioning[sid]
                t = max(t, -c if c < 0 else 0)
                r = max(r, c if c > 0 else 0)
            max_threat = max(max_threat, t * s.strength)
            max_reward = max(max_reward, r * s.strength)
            total_v += s.valence * s.strength
            total_a += s.arousal * s.strength

        avg_v = total_v / n if n else 0.0
        avg_a = total_a / n if n else 0.0
        dv = 0.5 if abs(avg_v) > 0.5 else 0.65
        da = 0.5 if avg_a > 0.6 else 0.65

        self.fear_level    = self.fear_level * 0.6 + max_threat * 0.4
        self.reward_signal = self.reward_signal * 0.6 + max_reward * 0.4
        composite_v = avg_v * 0.6 + self.reward_signal * 0.25 - self.fear_level * 0.15
        self.emotional_valence = self.emotional_valence * dv + composite_v * (1 - dv)
        self.emotional_arousal = self.emotional_arousal * da + avg_a * (1 - da)

        if self.fear_level > 0.3:
            nt.modulate({"norepinephrine": self.fear_level * 0.1, "cortisol": self.fear_level * 0.05, "gaba": -self.fear_level * 0.03})
        if self.reward_signal > 0.3:
            nt.modulate({"dopamine": self.reward_signal * 0.1, "endorphins": self.reward_signal * 0.05})

        intensity = max(abs(self.emotional_valence), self.fear_level, self.reward_signal)
        if intensity > 0.1:
            self._emit(self._make("prefrontal_cortex", "emotional",
                {"fear": round(self.fear_level, 3), "reward": round(self.reward_signal, 3),
                 "valence": round(self.emotional_valence, 3), "arousal": round(self.emotional_arousal, 3)},
                strength=intensity, valence=self.emotional_valence, arousal=self.emotional_arousal))
            self._emit(self._make("hippocampus", "emotional",
                {"emotional_tag": round(intensity, 3), "valence": round(self.emotional_valence, 3)},
                strength=intensity * 0.8, valence=self.emotional_valence, arousal=self.emotional_arousal))
            if self.emotional_arousal > 0.4:
                self._emit(self._make("insula", "emotional",
                    {"body_arousal": self.emotional_arousal, "valence": self.emotional_valence},
                    strength=self.emotional_arousal * 0.7, arousal=self.emotional_arousal))

    def condition(self, stimulus_id: str, value: float) -> None:
        prev = self._conditioning.get(stimulus_id, 0.0)
        self._conditioning[stimulus_id] = prev * 0.7 + value * 0.3

    def get_state(self) -> dict:
        s = super().get_state()
        s.update({"fear": round(self.fear_level, 3), "reward": round(self.reward_signal, 3),
                  "valence": round(self.emotional_valence, 3), "e_arousal": round(self.emotional_arousal, 3)})
        return s


@dataclass
class MemoryTrace:
    episode_id:     int
    content:        dict
    emotional_tag:  float
    valence:        float
    encoded_at:     float = field(default_factory=time.time)
    strength:       float = 1.0
    consolidated:   bool  = False
    retrieval_count: int  = 0

    def decay(self, rate: float = 0.001) -> None:
        if not self.consolidated:
            self.strength = max(0.0, self.strength - rate * (1 - self.emotional_tag * 0.5))

    def reinforce(self, amount: float = 0.1) -> None:
        self.strength = min(1.0, self.strength + amount)
        self.retrieval_count += 1


class Hippocampus(BrainRegion):
    """Mémoire épisodique, encodage (renforcé par émotion), récupération."""
    def __init__(self):
        super().__init__("hippocampus", 20)
        self._episode_counter   = 0
        self._memory_traces: list[MemoryTrace] = []
        self.current_emotional_tag = 0.0

    def _process_signals(self, signals, nt):
        retrieval_cue = None
        new_content   = {}
        emotional_tag = self.current_emotional_tag

        for s in signals:
            if s.signal_type == "emotional":
                emotional_tag = max(emotional_tag, s.content.get("emotional_tag", 0))
                self.current_emotional_tag = emotional_tag * 0.8
            elif s.signal_type == "sensory":
                new_content.update(s.content)
                if abs(s.valence) > 0.3 or s.arousal > 0.6:
                    emotional_tag = max(emotional_tag, (abs(s.valence) * 0.6 + s.arousal * 0.4) * s.strength)
            elif s.signal_type == "executive" and s.content.get("retrieve"):
                retrieval_cue = s.content["retrieve"]

        if new_content:
            eff = nt.memory_encoding_efficiency * max(0.2, 1.0 - nt.cortisol * 0.5)
            if eff > 0.2:
                self._episode_counter += 1
                self._memory_traces.append(MemoryTrace(
                    episode_id=self._episode_counter, content=new_content.copy(),
                    emotional_tag=emotional_tag,
                    valence=sum(s.valence for s in signals) / max(1, len(signals)),
                    strength=eff,
                ))
                self._emit(self._make("prefrontal_cortex", "mnemonic",
                    {"episode_id": self._episode_counter, "encoded": True,
                     "strength": round(eff, 3), "emotional_tag": round(emotional_tag, 3)},
                    strength=eff * 0.7))

        if retrieval_cue:
            recalled = self._retrieve(retrieval_cue)
            if recalled:
                self._emit(self._make("prefrontal_cortex", "mnemonic",
                    {"retrieved": True, "cue": retrieval_cue, "memory": recalled.content,
                     "emotional_tag": recalled.emotional_tag, "valence": recalled.valence},
                    strength=recalled.strength, valence=recalled.valence))

        for t in self._memory_traces: t.decay()
        self._memory_traces = [t for t in self._memory_traces if t.strength > 0.01]

    def _retrieve(self, cue) -> Optional[MemoryTrace]:
        if not self._memory_traces: return None
        if isinstance(cue, str):
            candidates = [t for t in self._memory_traces if any(cue in str(v) for v in t.content.values())]
        else:
            candidates = self._memory_traces
        if not candidates: return None
        best = max(candidates, key=lambda t: t.strength * (1 + t.emotional_tag))
        best.reinforce()
        return best

    def get_state(self) -> dict:
        s = super().get_state()
        s.update({"memory_traces": len(self._memory_traces), "total_episodes": self._episode_counter})
        return s


class WorkingMemory:
    CAPACITY = 7
    def __init__(self):
        self._slots: deque = deque(maxlen=self.CAPACITY)

    def add(self, item: dict, priority: float = 0.5) -> None:
        self._slots.append({"item": item, "priority": priority})

    def get_focus(self) -> Optional[dict]:
        if not self._slots: return None
        return max(self._slots, key=lambda s: s["priority"])["item"]

    def clear_low_priority(self, threshold: float = 0.2) -> None:
        self._slots = deque([s for s in self._slots if s["priority"] > threshold], maxlen=self.CAPACITY)

    @property
    def load(self) -> float:
        return len(self._slots) / self.CAPACITY


class PrefrontalCortex(BrainRegion):
    """Exécutif: planification, décision, mémoire de travail, prédiction (Friston)."""
    def __init__(self):
        super().__init__("prefrontal_cortex", 30)
        self._fatigue_managed_internally = True
        self.working_memory    = WorkingMemory()
        self.emotional_state   = {"fear": 0.0, "reward": 0.0, "valence": 0.0}
        self.inhibition_signal = 0.0
        self.cognitive_load    = 0.0
        self.prediction_error  = 0.0
        self._expected_state: dict = {}

    def _process_signals(self, signals, nt):
        sensory = [s for s in signals if s.signal_type == "sensory"]
        emotional = [s for s in signals if s.signal_type == "emotional"]
        mnemonic  = [s for s in signals if s.signal_type == "mnemonic"]

        if emotional:
            self.emotional_state = emotional[-1].content

        for s in sensory:
            self.working_memory.add(s.content, priority=s.strength * (1 + abs(s.valence) * 0.5))
        for s in mnemonic:
            if s.content.get("retrieved"):
                self.working_memory.add(s.content, priority=0.8)

        self.cognitive_load = self.working_memory.load * 0.6 + self.fatigue * 0.3 + nt.cortisol * 0.1

        has_external = any(s.signal_type in ("sensory", "emotional") for s in signals)
        if has_external and self.cognitive_load > 0.05:
            self.fatigue = min(1.0, self.fatigue + self.cognitive_load * 0.15)
        elif not has_external:
            self.fatigue = max(0.0, self.fatigue - 0.03)

        if sensory and self._expected_state:
            received = sensory[0].content
            all_keys = set(self._expected_state.keys()) | set(received.keys())
            errs = [abs(float(self._expected_state.get(k, 0)) - float(received.get(k, 0)))
                    for k in all_keys
                    if isinstance(self._expected_state.get(k, 0), (int, float))
                    and isinstance(received.get(k, 0), (int, float))]
            self.prediction_error = min(1.0, sum(errs) / max(1, len(errs))) if errs else self.prediction_error * 0.9
        else:
            self.prediction_error *= 0.9

        fear = self.emotional_state.get("fear", 0.0)
        self.inhibition_signal = fear * nt.serotonin

        self._emit(self._make("thalamus", "executive",
            {"attention_direction": min(1.0, max(0.1, 0.5 + self.prediction_error * 0.3 - self.cognitive_load * 0.2)),
             "inhibit": self.inhibition_signal > 0.5},
            strength=max(0.2, 1.0 - self.cognitive_load), arousal=nt.arousal_level))

        focus = self.working_memory.get_focus()
        if focus and self.prediction_error > 0.4:
            self._emit(self._make("hippocampus", "executive",
                {"retrieve": list(focus.keys())[0] if focus else None}, strength=0.6))

        if self.cognitive_load < 0.9:
            decision = self._decide(nt)
            if decision:
                self._emit(self._make("basal_ganglia", "executive", decision,
                    strength=max(0.3, nt.motivation), valence=self.emotional_state.get("valence", 0.0)))

        if abs(self.emotional_state.get("valence", 0.0)) > 0.3:
            self._emit(self._make("insula", "interoceptive",
                {"monitored_state": self.emotional_state}, strength=0.5))

        self.working_memory.clear_low_priority()
        if sensory:
            self._expected_state = sensory[-1].content.copy()

    def _decide(self, nt) -> Optional[dict]:
        focus = self.working_memory.get_focus()
        if not focus: return None
        fear   = self.emotional_state.get("fear", 0.0)
        reward = self.emotional_state.get("reward", 0.0)
        valence = self.emotional_state.get("valence", 0.0)

        if fear > 0.4 and nt.serotonin < 0.5:
            action, confidence = "avoid", fear
        elif reward > 0.25 and nt.dopamine > 0.4:
            action, confidence = "approach", reward * nt.motivation
        elif self.prediction_error > 0.35:
            action, confidence = "explore", self.prediction_error * 0.6
        elif valence > 0.2:
            action, confidence = "engage", valence * 0.7
        else:
            action, confidence = "maintain", 0.3
        return {"action": action, "confidence": round(confidence, 3),
                "working_memory_load": round(self.working_memory.load, 3),
                "cognitive_load": round(self.cognitive_load, 3)}

    def get_state(self) -> dict:
        s = super().get_state()
        s.update({"cognitive_load": round(self.cognitive_load, 3),
                  "wm_load": round(self.working_memory.load, 3),
                  "prediction_error": round(self.prediction_error, 3),
                  "emotional_state": self.emotional_state})
        return s


class BasalGanglia(BrainRegion):
    """Sélection d'action (Winner-Take-All) + apprentissage Actor-Critic (TD-error)."""
    def __init__(self):
        super().__init__("basal_ganglia", 15)
        self._action_values = {k: 0.5 for k in ["approach","avoid","explore","engage","maintain","rest"]}
        self._last_action: Optional[str] = None
        self._last_value:  float = 0.0
        self.selected_action: Optional[str] = None
        self.habit_strength: dict[str, float] = {}

    def _process_signals(self, signals, nt):
        executive = [s for s in signals if s.signal_type == "executive"]
        rewards   = [s for s in signals if s.signal_type == "reward"]

        for s in rewards:
            if self._last_action:
                td_err = s.content.get("reward_received", 0.0) - self._last_value
                lr = nt.dopamine * 0.1
                self._action_values[self._last_action] = min(1.0, max(0.0,
                    self._action_values[self._last_action] + lr * td_err))
                if td_err > 0.2:   nt.modulate({"dopamine":  td_err * 0.1})
                elif td_err < -0.2: nt.modulate({"dopamine": td_err * 0.05})

        if not executive: return
        last = executive[-1]
        suggested = last.content.get("action", "maintain")
        confidence = last.content.get("confidence", 0.5)

        scores = {}
        for a, base in self._action_values.items():
            score = base * 0.5
            if a == suggested: score += confidence * 0.4
            score += self.habit_strength.get(a, 0.0) * 0.3 * nt.dopamine
            score *= max(0.2, nt.motivation)
            scores[a] = score

        selected = max(scores, key=scores.get)
        self.selected_action = selected
        self._last_action = selected
        self._last_value  = self._action_values.get(selected, 0.5)

        self.habit_strength[selected] = min(1.0, self.habit_strength.get(selected, 0.0) + 0.01)
        for a in self.habit_strength:
            if a != selected:
                self.habit_strength[a] = max(0.0, self.habit_strength[a] - 0.005)

        self._emit(self._make("cerebellum", "motor",
            {"action": selected, "score": round(scores[selected], 3),
             "habit": round(self.habit_strength.get(selected, 0.0), 3)},
            strength=scores[selected], valence=last.valence))
        self._emit(self._make("prefrontal_cortex", "reward",
            {"action_selected": selected, "action_score": round(scores[selected], 3)}, strength=0.4))

    def get_state(self) -> dict:
        s = super().get_state()
        s.update({"selected_action": self.selected_action,
                  "action_values": {k: round(v, 3) for k, v in self._action_values.items()}})
        return s


class Cerebellum(BrainRegion):
    """Timing, modèle interne prédictif, mémoire procédurale."""
    def __init__(self):
        super().__init__("cerebellum", 15)
        self._internal_model: dict[str, float] = {}
        self.timing_precision      = 0.7
        self.last_prediction_error = 0.0
        self.procedural_memory: dict[str, float] = {}

    def _process_signals(self, signals, nt):
        motor   = [s for s in signals if s.signal_type == "motor"]
        sfback  = [s for s in signals if s.signal_type == "sensory"]
        for s in motor:
            action  = s.content.get("action", "maintain")
            predicted = self._internal_model.get(action, 0.5)
            refined   = s.content.get("score", 0.5)
            proc = self.procedural_memory.get(action, 0.0)
            self.procedural_memory[action] = min(1.0, proc + 0.005)
            timing = self.timing_precision * (1.0 - self.fatigue * 0.3)
            self._emit(self._make("output", "motor",
                {"action": action, "refined_score": round(refined * timing, 3),
                 "predicted": round(predicted, 3), "procedural": round(proc, 3)},
                strength=refined * timing, valence=s.valence))
            if sfback:
                actual = sfback[-1].strength
                self.last_prediction_error = abs(predicted - actual)
                self._internal_model[action] = predicted + 0.05 * (actual - predicted)
                if self.last_prediction_error > 0.3:
                    self._emit(self._make("prefrontal_cortex", "predictive",
                        {"action": action, "prediction_error": round(self.last_prediction_error, 3)},
                        strength=self.last_prediction_error))


class Insula(BrainRegion):
    """Intéroception, ressenti corporel subjectif, empathie."""
    def __init__(self):
        super().__init__("insula", 15)
        self.body_state = {"heart_rate": 0.5, "muscle_tension": 0.3, "gut_feeling": 0.5, "energy": 0.7}
        self.felt_emotion: dict = {}
        self.empathy_signal = 0.0

    def _process_signals(self, signals, nt):
        for s in signals:
            if s.signal_type == "emotional":
                arousal = s.content.get("body_arousal", s.arousal)
                valence = s.content.get("valence", s.valence)
                self.body_state["heart_rate"]    = min(1.0, self.body_state["heart_rate"] * 0.7 + arousal * 0.3)
                self.body_state["muscle_tension"]= min(1.0, self.body_state["muscle_tension"] * 0.8 + max(0, -valence) * arousal * 0.3)
                self.body_state["gut_feeling"]   = min(1.0, max(0.0, 0.5 + valence * 0.3 + (nt.serotonin - 0.5) * 0.2))
                self.felt_emotion = {
                    "valence": round(valence, 3), "arousal": round(arousal, 3),
                    "body_tension": round(self.body_state["muscle_tension"], 3),
                    "gut_feeling":  round(self.body_state["gut_feeling"], 3),
                    "subjective_intensity": round((abs(valence) + arousal + self.body_state["heart_rate"]) / 3, 3),
                }
            elif s.signal_type == "interoceptive":
                monitored = s.content.get("monitored_state", {})
                if monitored: self.empathy_signal = abs(monitored.get("valence", 0.0)) * 0.5

        self.body_state["energy"] = max(0.1, min(1.0, self.body_state["energy"] - self.fatigue * 0.01 + nt.dopamine * 0.005))
        si = self.felt_emotion.get("subjective_intensity", 0.0)
        if si > 0.2:
            self._emit(self._make("cingulate_cortex", "interoceptive",
                {"felt_emotion": self.felt_emotion, "body_state": {k: round(v, 3) for k, v in self.body_state.items()}},
                strength=si, valence=self.felt_emotion.get("valence", 0.0), arousal=self.felt_emotion.get("arousal", 0.5)))

    def get_state(self) -> dict:
        s = super().get_state()
        s.update({"body_state": {k: round(v, 3) for k, v in self.body_state.items()}, "felt_emotion": self.felt_emotion})
        return s


class CingulateCortex(BrainRegion):
    """Monitoring de conflit, détection d'erreur, détresse, alarme cognitive."""
    def __init__(self):
        super().__init__("cingulate_cortex", 15)
        self.conflict_level = 0.0
        self.error_signal   = 0.0
        self.distress_level = 0.0

    def _process_signals(self, signals, nt):
        interoceptive = [s for s in signals if s.signal_type == "interoceptive"]
        predictive    = [s for s in signals if s.signal_type == "predictive"]

        valences = [s.valence for s in signals if s.valence != 0]
        if len(valences) >= 2:
            max_v, min_v = max(valences), min(valences)
            self.conflict_level = min(1.0, (max_v - min_v) / 2) if max_v > 0.3 and min_v < -0.3 else self.conflict_level * 0.8
        else:
            self.conflict_level *= 0.8

        for s in predictive:
            self.error_signal = max(self.error_signal * 0.7, s.content.get("prediction_error", 0.0))

        for s in interoceptive:
            felt = s.content.get("felt_emotion", {})
            neg_v = max(0, -felt.get("valence", 0.0))
            si    = felt.get("subjective_intensity", 0.0)
            self.distress_level = min(1.0, self.distress_level * 0.7 + (neg_v * 0.3 + self.conflict_level * 0.2 + si * 0.2))

        if self.distress_level > 0.4: nt.modulate({"cortisol": self.distress_level * 0.02})
        if self.error_signal > 0.5:   nt.modulate({"norepinephrine": self.error_signal * 0.05})
        if self.conflict_level > 0.5: nt.modulate({"acetylcholine": self.conflict_level * 0.03})

        alarm = max(self.conflict_level, self.error_signal, self.distress_level)
        if alarm > 0.2:
            self._emit(self._make("prefrontal_cortex", "executive",
                {"conflict": round(self.conflict_level, 3), "error": round(self.error_signal, 3),
                 "distress": round(self.distress_level, 3), "alarm": round(alarm, 3)},
                strength=alarm, valence=-self.distress_level, arousal=min(1.0, alarm * 1.2)))

    def get_state(self) -> dict:
        s = super().get_state()
        s.update({"conflict": round(self.conflict_level, 3), "error": round(self.error_signal, 3), "distress": round(self.distress_level, 3)})
        return s


class SensoryCortex(BrainRegion):
    """Traitement perceptuel, reconnaissance de patterns, intégration multimodale."""
    def __init__(self):
        super().__init__("sensory_cortex", 20)
        self._recognition_cache: dict[str, float] = {}

    def _process_signals(self, signals, nt):
        for s in signals:
            if s.signal_type != "sensory": continue
            content = s.content
            pattern = content.get("pattern", "")
            if pattern:
                rec = self._recognition_cache.get(pattern, 0.0)
                self._recognition_cache[pattern] = min(1.0, rec + 0.05)
                recognized = rec > 0.2
            else:
                recognized = False; rec = 0.0

            ps = s.strength * (nt.acetylcholine * 0.3 + 0.7)
            self._emit(NeuralSignal("sensory_cortex", "hippocampus", "sensory",
                {**content, "recognized": recognized, "recognition_strength": round(rec, 3)},
                ps * 0.7, s.valence, s.arousal))
            self._emit(NeuralSignal("sensory_cortex", "prefrontal_cortex", "sensory",
                {**content, "recognized": recognized, "novelty": content.get("novelty", 0.3)},
                ps * 0.6, s.valence, s.arousal))
            if abs(s.valence) > 0.3 or content.get("threat", 0) > 0.2:
                self._emit(NeuralSignal("sensory_cortex", "amygdala", "sensory",
                    content, ps * 0.5, s.valence, s.arousal))


class DefaultModeNetwork(BrainRegion):
    """Rêverie, narration de soi, associations créatives. Actif au repos."""
    def __init__(self):
        super().__init__("default_mode_network", 10)
        self.self_model = {"identity_coherence": 0.7, "narrative_strength": 0.5, "rumination_tendency": 0.3}
        self.mind_wandering = False
        self.creative_associations: list[tuple] = []

    def _process_signals(self, signals, nt):
        ext_demands = sum(s.strength for s in signals if s.signal_type in ("sensory", "executive"))
        dmn_act = max(0.0, 0.7 - ext_demands * 0.8) * max(0.2, 1.0 - nt.norepinephrine * 0.5)
        self.activation = self.activation * 0.6 + dmn_act * 0.4

        if self.activation < 0.2:
            self.mind_wandering = False; return
        self.mind_wandering = True

        if nt.stress_level > 0.6 and nt.serotonin < 0.4:
            thought_type = "rumination"; tv = -0.5
            self.self_model["rumination_tendency"] = min(1.0, self.self_model["rumination_tendency"] + 0.02)
            nt.modulate({"serotonin": -0.01, "cortisol": 0.01})
        elif nt.mood_valence > 0.3 and nt.dopamine > 0.5:
            thought_type = "creative_daydream"; tv = 0.4
            self._creative_association(); nt.modulate({"dopamine": 0.005})
        elif nt.serotonin > 0.6:
            thought_type = "self_narrative"; tv = 0.2
            self.self_model["narrative_strength"] = min(1.0, self.self_model["narrative_strength"] + 0.01)
        else:
            thought_type = "mind_wandering"; tv = 0.0

        if self.activation > 0.4:
            self._emit(self._make("prefrontal_cortex", "internal",
                {"thought_type": thought_type, "dmn_activation": round(self.activation, 3),
                 "self_model": self.self_model.copy(), "mind_wandering": self.mind_wandering},
                strength=self.activation * 0.5, valence=tv, arousal=self.activation * 0.3))

    def _creative_association(self) -> None:
        concepts = ["memory","emotion","future","self","other","pattern","structure","flow","emergence","connection"]
        if len(concepts) >= 2:
            a = random.choice(concepts); b = random.choice([c for c in concepts if c != a])
            self.creative_associations.append((a, b, round(random.uniform(0.3, 1.0), 2)))
            if len(self.creative_associations) > 20: self.creative_associations.pop(0)

    def get_state(self) -> dict:
        s = super().get_state()
        s.update({"mind_wandering": self.mind_wandering, "self_model": {k: round(v, 3) for k, v in self.self_model.items()}})
        return s


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — ÉTATS ÉMERGENTS: ÉMOTION & CONSCIENCE
# ─────────────────────────────────────────────────────────────────────────────

EMOTION_MAP = [
    ( 0.5,  1.0,  0.65, 1.0,  "joy",          "joie / euphorie"),
    ( 0.25, 0.7,  0.55, 0.9,  "excitement",   "excitation / enthousiasme"),
    ( 0.15, 0.55, 0.45, 0.75, "interest",     "intérêt / curiosité"),
    ( 0.3,  0.8,  0.35, 0.7,  "enthusiasm",   "enthousiasme / élan"),
    ( 0.3,  0.7,  0.25, 0.55, "pleasure",     "plaisir / bien-être"),
    ( 0.2,  0.6,  0.15, 0.45, "satisfaction", "satisfaction / plaisir"),
    ( 0.35, 1.0,  0.0,  0.35, "contentment",  "contentement / sérénité"),
    ( 0.1,  0.45, 0.0,  0.25, "calm",         "calme / relaxation"),
    ( 0.45, 1.0,  0.15, 0.5,  "happiness",    "bonheur / épanouissement"),
    (-1.0, -0.45, 0.6,  1.0,  "fear",         "peur / terreur"),
    (-0.7, -0.25, 0.5,  0.9,  "anger",        "colère / frustration"),
    (-0.5, -0.15, 0.45, 0.8,  "anxiety",      "anxiété / inquiétude"),
    (-0.8, -0.35, 0.7,  1.0,  "panic",        "panique / détresse"),
    (-0.6, -0.2,  0.35, 0.65, "unease",       "malaise / tension"),
    (-1.0, -0.35, 0.0,  0.45, "sadness",      "tristesse / mélancolie"),
    (-0.5, -0.05, 0.05, 0.35, "boredom",      "ennui / apathie"),
    (-0.6, -0.15, 0.0,  0.2,  "depression",   "abattement / déprime"),
    (-0.4, -0.1,  0.15, 0.45, "melancholy",   "mélancolie / nostalgie"),
    (-0.3,  0.3,  0.15, 0.55, "neutral",      "neutre / équilibré"),
    (-0.15, 0.35, 0.35, 0.65, "alert",        "alerte / attentif"),
    (-0.2,  0.2,  0.55, 0.85, "aroused",      "éveillé / activé"),
    (-0.3,  0.15, 0.0,  0.2,  "tired",        "fatigué / somnolent"),
    ( 0.0,  0.4,  0.0,  0.5,  "serene",       "serein / tranquille"),
]

def _label_emotion(valence: float, arousal: float) -> tuple[str, str]:
    candidates = []
    for min_v, max_v, min_a, max_a, label, label_fr in EMOTION_MAP:
        if min_v <= valence <= max_v and min_a <= arousal <= max_a:
            cv = (min_v + max_v) / 2; ca = (min_a + max_a) / 2
            dist = ((valence - cv)**2 + (arousal - ca)**2) ** 0.5
            candidates.append((dist, label, label_fr))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1], candidates[0][2]
    return "neutral", "neutre / équilibré"


class EmotionalStateTracker:
    def __init__(self):
        self._valence = 0.0; self._arousal = 0.3
        self._label = "neutral"; self._label_fr = "neutre / équilibré"
        self._intensity = 0.0; self._duration = 1; self._last_label = "neutral"
        self._history: list[dict] = []

    def update(self, amygdala: Amygdala, insula: Insula, nt: NeurotransmitterSystem) -> None:
        iv = amygdala.emotional_valence * 0.4 + insula.felt_emotion.get("valence", 0.0) * 0.3 + nt.mood_valence * 0.3
        ia = amygdala.emotional_arousal * 0.4 + insula.felt_emotion.get("arousal", 0.3) * 0.3 + nt.arousal_level * 0.3
        intensity_f = min(1.0, abs(iv) + ia)
        smoothing = max(0.4, 0.7 - intensity_f * 0.3)
        self._valence = self._valence * smoothing + iv * (1 - smoothing)
        self._arousal = self._arousal * smoothing + ia * (1 - smoothing)
        self._intensity = (abs(self._valence) + self._arousal) / 2
        self._label, self._label_fr = _label_emotion(self._valence, self._arousal)
        self._duration = self._duration + 1 if self._label == self._last_label else 1
        self._last_label = self._label
        self._history.append({"valence": round(self._valence, 3), "arousal": round(self._arousal, 3),
                               "label": self._label, "intensity": round(self._intensity, 3)})
        if len(self._history) > 100: self._history.pop(0)

    def current_state(self) -> dict:
        return {"label": self._label, "label_fr": self._label_fr,
                "valence": round(self._valence, 3), "arousal": round(self._arousal, 3),
                "intensity": round(self._intensity, 3), "duration": self._duration}

    def get_history(self) -> list[dict]:
        return list(self._history)


class ConsciousnessMonitor:
    def __init__(self):
        self._level = 0.5; self._meta = 0.0; self._content = "background"
        self._workspace: list = []; self._history: list[dict] = []

    def update(self, pfc: PrefrontalCortex, thalamus: Thalamus,
               dmn: DefaultModeNetwork, signals: list[NeuralSignal], tick: int) -> None:
        gate = thalamus.attention_gate
        pfc_act = pfc.activation
        pfc_ff = max(0.2, 1.0 - pfc.fatigue * 0.6)
        strong = [s for s in signals if s.strength > 0.4]
        diversity = len(set(s.signal_type for s in strong))
        richness = min(1.0, diversity * 0.15 + len(strong) * 0.05)
        dmn_c = dmn.activation * 0.3 if dmn.mind_wandering else 0.0
        new_level = gate * 0.25 + pfc_act * 0.30 + pfc_ff * 0.15 + richness * 0.20 + dmn_c * 0.10
        self._level = self._level * 0.8 + new_level * 0.2
        if pfc.cognitive_load < 0.7 and pfc_act > 0.4:
            int_sigs = [s for s in signals if s.signal_type == "internal"]
            self._meta = min(1.0, self._meta * 0.8 + len(int_sigs) * 0.1) if int_sigs else self._meta * 0.9
        else:
            self._meta *= 0.85
        self._content = (f"{max(strong, key=lambda s: s.strength).source}→{max(strong, key=lambda s: s.strength).signal_type}"
                         if strong else ("internal_thought" if dmn.mind_wandering else "background"))
        self._workspace = [{"source": s.source, "type": s.signal_type, "strength": round(s.strength, 3)} for s in strong[:5]]
        self._history.append({"tick": tick, "level": round(self._level, 3), "meta": round(self._meta, 3)})
        if len(self._history) > 100: self._history.pop(0)

    def current_state(self) -> dict:
        label = ("unconscious" if self._level < 0.2 else "subconscious" if self._level < 0.4
                 else "conscious" if self._level < 0.65 else "focused" if self._level < 0.85 else "heightened")
        return {"level": round(self._level, 3), "label": label,
                "meta_awareness": round(self._meta, 3), "content": self._content,
                "global_workspace": self._workspace}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — CERVEAU ORCHESTRATEUR
# ─────────────────────────────────────────────────────────────────────────────

class Brain:
    """Orchestre toutes les régions. Les états émergent de leurs interactions."""

    def __init__(self):
        self.nt             = NeurotransmitterSystem()
        self.brainstem      = Brainstem()
        self.thalamus       = Thalamus()
        self.amygdala       = Amygdala()
        self.hippocampus    = Hippocampus()
        self.pfc            = PrefrontalCortex()
        self.basal_ganglia  = BasalGanglia()
        self.cerebellum     = Cerebellum()
        self.insula         = Insula()
        self.cingulate      = CingulateCortex()
        self.sensory_cortex = SensoryCortex()
        self.dmn            = DefaultModeNetwork()

        self._regions = {
            "brainstem": self.brainstem, "thalamus": self.thalamus,
            "amygdala": self.amygdala, "hippocampus": self.hippocampus,
            "prefrontal_cortex": self.pfc, "basal_ganglia": self.basal_ganglia,
            "cerebellum": self.cerebellum, "insula": self.insula,
            "cingulate_cortex": self.cingulate, "sensory_cortex": self.sensory_cortex,
            "default_mode_network": self.dmn,
        }
        self.emotional_tracker   = EmotionalStateTracker()
        self.consciousness_monitor = ConsciousnessMonitor()
        self._tick       = 0
        self.last_action: Optional[str] = None

    def perceive(self, stimulus: dict[str, Any]) -> dict:
        sig = NeuralSignal("environment", "brainstem", "sensory", stimulus,
                           stimulus.get("intensity", 0.5), stimulus.get("valence", 0.0), stimulus.get("arousal", 0.3))
        self.brainstem.receive(sig)
        self.thalamus.receive(sig)
        return self.tick()

    def tick(self) -> dict:
        self._tick += 1
        all_emitted: list[NeuralSignal] = []
        for region in self._regions.values():
            all_emitted.extend(region.process(self.nt))

        for sig in all_emitted:
            t = sig.target
            if t in self._regions:   self._regions[t].receive(sig)
            elif t == "output":
                action = sig.content.get("action")
                if action: self.last_action = action
            elif t == "broadcast":
                for region in self._regions.values(): region.receive(sig)

        self.dmn.receive(NeuralSignal("brain", "default_mode_network", "internal",
                                      {"tick": self._tick}, 0.1))
        self.nt.decay_to_baseline()
        self.emotional_tracker.update(self.amygdala, self.insula, self.nt)
        self.consciousness_monitor.update(self.pfc, self.thalamus, self.dmn, all_emitted, self._tick)
        return self.get_state()

    def inject_reward(self, value: float) -> None:
        sig = NeuralSignal("environment", "basal_ganglia", "reward",
                           {"reward_received": value}, abs(value), value)
        self.basal_ganglia.receive(sig)
        if value > 0: self.nt.modulate({"dopamine": value * 0.1, "serotonin": value * 0.03})
        else:          self.nt.modulate({"cortisol": abs(value) * 0.05})

    def get_state(self) -> dict:
        return {
            "tick": self._tick,
            "regions": {n: r.get_state() for n, r in self._regions.items()},
            "neurotransmitters": self.nt.snapshot(),
            "emotional_state":   self.emotional_tracker.current_state(),
            "consciousness":     self.consciousness_monitor.current_state(),
            "last_action":       self.last_action,
        }

    def get_summary(self) -> dict:
        emo = self.emotional_tracker.current_state()
        con = self.consciousness_monitor.current_state()
        return {
            "tick": self._tick, "emotion": emo["label"], "emotion_fr": emo["label_fr"],
            "valence": round(self.nt.mood_valence, 3), "arousal": round(self.nt.arousal_level, 3),
            "stress": round(self.nt.stress_level, 3), "motivation": round(self.nt.motivation, 3),
            "action": self.last_action, "consciousness_level": round(con["level"], 3),
            "mind_wandering": self.dmn.mind_wandering, "pfc_load": round(self.pfc.cognitive_load, 3),
        }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — API PUBLIQUE (pour utilisation programmatique)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PerceptionResult:
    """
    Résultat d'un cycle de perception. Retourné par DeepBrain.perceive() / tick().

    CHAMPS PRINCIPAUX:
        emotion        str        étiquette anglaise: "joy","fear","calm","anxiety"...
        emotion_fr     str        étiquette française: "joie / euphorie"...
        valence        float      -1.0 (très négatif) → +1.0 (très positif)
        arousal        float       0.0 (calme) → 1.0 (très activé)
        action         str|None   "approach","avoid","explore","engage","maintain","rest"
        consciousness  float       0.0 → 1.0
        stress         float       0.0 → 1.0
        motivation     float       0.0 → 1.0
        mood           float      -1.0 → +1.0
        pfc_fatigue    float       0.0 → 1.0
        mind_wandering bool        True si en rêverie (DMN actif)
        memory_count   int         nombre de traces mnésiques actives
        tick           int         cycle interne
    """
    emotion:             str
    emotion_fr:          str
    valence:             float
    arousal:             float
    emotion_intensity:   float
    emotion_duration:    int
    consciousness:       float
    consciousness_label: str
    meta_awareness:      float
    mind_wandering:      bool
    action:              Optional[str]
    action_confidence:   float
    cognitive_load:      float
    pfc_fatigue:         float
    stress:              float
    motivation:          float
    mood:                float
    memory_count:        int
    last_encoded:        bool
    tick:                int
    _full_state:         dict = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict:
        return {
            "tick": self.tick, "emotion": self.emotion, "emotion_fr": self.emotion_fr,
            "valence": self.valence, "arousal": self.arousal,
            "emotion_intensity": self.emotion_intensity, "emotion_duration": self.emotion_duration,
            "consciousness": self.consciousness, "consciousness_label": self.consciousness_label,
            "meta_awareness": self.meta_awareness, "mind_wandering": self.mind_wandering,
            "action": self.action, "action_confidence": self.action_confidence,
            "cognitive_load": self.cognitive_load, "pfc_fatigue": self.pfc_fatigue,
            "stress": self.stress, "motivation": self.motivation, "mood": self.mood,
            "memory_count": self.memory_count, "last_encoded": self.last_encoded,
        }

    def __str__(self) -> str:
        wander = " [mind-wandering]" if self.mind_wandering else ""
        return (f"[tick={self.tick}] {self.emotion_fr} "
                f"(v={self.valence:+.2f}, a={self.arousal:.2f}) | "
                f"action={self.action} | "
                f"conscience={self.consciousness:.2f} [{self.consciousness_label}]{wander}")


class DeepBrain:
    """
    Interface simplifiée pour Deep Sanctuary.

    USAGE MINIMAL:
        brain = DeepBrain()
        result = brain.perceive({"modality": "threat", "threat": 0.8,
                                  "valence": -0.7, "arousal": 0.9, "intensity": 0.9})
        print(result.emotion)    # "fear"
        print(result.action)     # "avoid"
        print(result.stress)     # ex: 0.45

    PARAMÈTRES DU STIMULUS (tous optionnels):
        modality    str         "visual","auditory","social","threat","reward","cognitive",
                                "music","pain","internal","unknown"...
        intensity   float 0–1   intensité brute
        valence     float -1–+1 charge émotionnelle
        arousal     float 0–1   niveau d'activation
        novelty     float 0–1   nouveauté (→ curiosité)
        threat      float 0–1   danger perçu
        reward      float 0–1   récompense immédiate
        pattern     str         identifiant visuel (habituation)
        stimulus_id str         ID unique (conditionnement / mémoire)

    MÉTHODES:
        perceive(stimulus)       → PerceptionResult
        tick()                   → PerceptionResult  (repos, sans stimulus)
        reward(value -1 à +1)    → None  (feedback d'apprentissage)
        inject({"cortisol":0.3}) → None  (modifier des neurotransmetteurs)
        get_neurochemistry()     → dict  (niveaux NT complets)
        get_region_activations() → dict  (activation de chaque région)
        get_memory_traces()      → list  (traces mnésiques)
        get_emotional_history()  → list  (historique émotionnel)
    """

    def __init__(self):
        self._brain = Brain()
        self._prev_mem_count = 0

    def perceive(self, stimulus: dict) -> PerceptionResult:
        return self._to_result(self._brain.perceive(stimulus))

    def tick(self) -> PerceptionResult:
        return self._to_result(self._brain.tick())

    def reward(self, value: float) -> None:
        self._brain.inject_reward(max(-1.0, min(1.0, value)))

    def inject(self, neurotransmitters: dict[str, float]) -> None:
        self._brain.nt.modulate(neurotransmitters)

    def get_neurochemistry(self) -> dict:
        nt = self._brain.nt
        return {k: round(getattr(nt, k), 3) for k in BASELINE_NT}

    def get_region_activations(self) -> dict[str, float]:
        return {n: round(r.activation, 3) for n, r in self._brain._regions.items()}

    def get_memory_traces(self) -> list[dict]:
        return [{"episode_id": t.episode_id, "strength": round(t.strength, 3),
                 "emotional_tag": round(t.emotional_tag, 3), "valence": round(t.valence, 3),
                 "retrieval_count": t.retrieval_count}
                for t in self._brain.hippocampus._memory_traces]

    def get_emotional_history(self) -> list[dict]:
        return self._brain.emotional_tracker.get_history()

    @property
    def tick_count(self) -> int:
        return self._brain._tick

    def _to_result(self, state: dict) -> PerceptionResult:
        emo = state["emotional_state"]; con = state["consciousness"]; nt = self._brain.nt
        bg  = state["regions"].get("basal_ganglia", {}); pfc = state["regions"]["prefrontal_cortex"]
        action = bg.get("selected_action") or state.get("last_action")
        cur_count = len(self._brain.hippocampus._memory_traces)
        last_enc  = cur_count > self._prev_mem_count
        self._prev_mem_count = cur_count
        return PerceptionResult(
            tick=state["tick"], emotion=emo["label"], emotion_fr=emo["label_fr"],
            valence=emo["valence"], arousal=emo["arousal"],
            emotion_intensity=emo["intensity"], emotion_duration=emo["duration"],
            consciousness=con["level"], consciousness_label=con["label"],
            meta_awareness=con["meta_awareness"], mind_wandering=self._brain.dmn.mind_wandering,
            action=action,
            action_confidence=round(self._brain.basal_ganglia._action_values.get(action or "maintain", 0.5), 3),
            cognitive_load=pfc.get("cognitive_load", 0.0), pfc_fatigue=pfc.get("fatigue", 0.0),
            stress=round(nt.stress_level, 3), motivation=round(nt.motivation, 3),
            mood=round(nt.mood_valence, 3), memory_count=cur_count, last_encoded=last_enc,
            _full_state=state,
        )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — VISUALISATION TERMINAL
# ─────────────────────────────────────────────────────────────────────────────

def _bar(v: float, w: int = 20) -> str:
    filled = int(max(0.0, min(1.0, v)) * w)
    return "█" * filled + "░" * (w - filled)

def _vbar(v: float, w: int = 20) -> str:
    c = w // 2; pos = int((v + 1) / 2 * w)
    bar = list("─" * w); bar[c] = "┼"
    if pos > c:
        for i in range(c, min(pos, w)): bar[i] = "+"
    elif pos < c:
        for i in range(max(pos, 0), c): bar[i] = "-"
    bar[max(0, min(pos, w-1))] = "●"
    return "".join(bar)

def print_state(brain: Brain) -> None:
    st = brain.get_state(); sm = brain.get_summary(); nt = brain.nt
    emo = st["emotional_state"]; con = st["consciousness"]
    print(f"\n{'━'*72}")
    print(f"  DEEP SANCTUARY  tick #{st['tick']:>4d}")
    print(f"{'━'*72}")
    ec = "🟢" if emo["valence"] > 0.3 else ("🔴" if emo["valence"] < -0.3 else "🟡")
    print(f"\n  {ec} ÉMOTION: {emo['label_fr'].upper():<30s} (durée: {emo['duration']} ticks)")
    print(f"     Valence:  {_vbar(emo['valence'], 24)} {emo['valence']:+.3f}")
    print(f"     Éveil:    {_bar(emo['arousal'], 24)} {emo['arousal']:.3f}")
    print(f"     Intensité:{_bar(emo['intensity'], 24)} {emo['intensity']:.3f}")
    print(f"\n  CONSCIENCE: [{con['label'].upper()}]  niveau={con['level']:.3f}  méta={con['meta_awareness']:.3f}")
    if brain.dmn.mind_wandering: print(f"  ✦ mind-wandering actif")
    print(f"\n  NEUROTRANSMETTEURS:")
    for name, role, val in [
        ("Dopamine",      "motivation",  nt.dopamine),
        ("Sérotonine",    "humeur",      nt.serotonin),
        ("Noradrénaline", "éveil",       nt.norepinephrine),
        ("Acétylcholine", "mémoire",     nt.acetylcholine),
        ("GABA",          "inhibition",  nt.gaba),
        ("Cortisol",      "stress",      nt.cortisol),
        ("Ocytocine",     "social",      nt.oxytocin),
        ("Endorphines",   "plaisir",     nt.endorphins),
    ]:
        alert = " ⚠" if (name == "Cortisol" and val > 0.6) else ""
        print(f"  {name:<14s} {_bar(val, 16)} {val:.3f}  ({role}){alert}")
    print(f"\n  RÉGIONS ACTIVES:")
    for name, rs in st["regions"].items():
        a = rs["activation"]; f = rs["fatigue"]
        if a > 0.08:
            fa = " ⚠fatigue" if f > 0.5 else ""
            print(f"  {name:<28s} {_bar(a, 12)} act={a:.2f}  fat={f:.2f}{fa}")
    print(f"\n  ACTION: {sm['action']}  |  PFC charge: {sm['pfc_load']:.3f}")
    print(f"{'━'*72}\n")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 — EXPÉRIENCES
# ─────────────────────────────────────────────────────────────────────────────

def exp_emotion(brain: Brain) -> None:
    print(f"\n{'='*60}\nEXPÉRIENCE: Émergence des émotions\n{'='*60}")
    print("\n[Phase 1] Stimulus de récompense positif")
    for i in range(5):
        brain.perceive({"modality":"reward","reward":0.8,"novelty":0.6,"intensity":0.7,
                        "valence":0.7,"arousal":0.6,"stimulus_id":"reward_A"})
        brain.inject_reward(0.8); sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: {sm['emotion']:15s} valence={sm['valence']:+.2f} arousal={sm['arousal']:.2f}")
    print("\n[Phase 2] Stimulus de menace")
    for i in range(5):
        brain.perceive({"modality":"threat","threat":0.85,"novelty":0.9,"intensity":0.9,
                        "valence":-0.8,"arousal":0.9,"stimulus_id":"threat_X"})
        sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: {sm['emotion']:15s} valence={sm['valence']:+.2f} arousal={sm['arousal']:.2f} stress={sm['stress']:.2f}")
    print("\n[Phase 3] Repos — retour homéostatique")
    for i in range(7):
        brain.tick(); sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: {sm['emotion']:15s} valence={sm['valence']:+.2f} mind_wandering={sm['mind_wandering']}")
    print("\n[Phase 4] Stimulus social + ocytocine")
    for i in range(4):
        brain.perceive({"modality":"social","reward":0.5,"valence":0.5,"arousal":0.4,"intensity":0.6})
        brain.nt.modulate({"oxytocin": 0.1}); sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: {sm['emotion']:15s} valence={sm['valence']:+.2f} social_open={brain.nt.social_openness:.2f}")


def exp_stress(brain: Brain) -> None:
    print(f"\n{'='*60}\nEXPÉRIENCE: Stress et récupération\n{'='*60}")
    print("\n[Phase 1] Baseline")
    for i in range(3):
        brain.tick(); sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: stress={sm['stress']:.3f}  cortisol={brain.nt.cortisol:.3f}")
    print("\n[Phase 2] Stresseur aigu")
    for i in range(3):
        brain.perceive({"modality":"threat","threat":0.95,"novelty":1.0,"intensity":1.0,"valence":-0.9,"arousal":1.0})
        sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: stress={sm['stress']:.3f}  cortisol={brain.nt.cortisol:.3f}  NE={brain.nt.norepinephrine:.3f}  action={sm['action']}")
    print("\n[Phase 3] Stress chronique")
    for i in range(8):
        brain.perceive({"modality":"threat","threat":0.5,"intensity":0.5,"valence":-0.4,"arousal":0.6})
        sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: cortisol={brain.nt.cortisol:.3f}  mémoire_enc={brain.nt.memory_encoding_efficiency:.3f}  pfc_load={sm['pfc_load']:.3f}")
    print("\n[Phase 4] Récupération")
    for i in range(10):
        brain.tick(); sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: stress={sm['stress']:.3f}  cortisol={brain.nt.cortisol:.3f}  émotion={sm['emotion']}")


def exp_curiosity(brain: Brain) -> None:
    print(f"\n{'='*60}\nEXPÉRIENCE: Curiosité vs Anxiété\n{'='*60}")
    print("\n[Phase 1] Nouveauté sécurisée → curiosité?")
    v1 = []
    for i in range(5):
        brain.perceive({"modality":"visual","novelty":0.9,"threat":0.0,"reward":0.3,
                        "intensity":0.5,"valence":0.2,"arousal":0.5,"pattern":f"novel_{i}"})
        sm = brain.get_summary(); v1.append(sm['valence'])
        print(f"  tick {sm['tick']:3d}: action={str(sm['action']):10s}  émotion={sm['emotion']:15s}  pred_err={brain.pfc.prediction_error:.3f}")
    print("\n[Phase 2] Habituation — même stimulus")
    for i in range(5):
        brain.perceive({"modality":"visual","novelty":0.1,"intensity":0.5,"valence":0.1,
                        "arousal":0.3,"pattern":"familiar_pattern"})
        sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: action={str(sm['action']):10s}  émotion={sm['emotion']:15s}  arousal={sm['arousal']:.3f}")
    print("\n[Phase 3] Nouveauté menaçante → anxiété?")
    v2 = []
    for i in range(5):
        brain.perceive({"modality":"unknown","novelty":0.9,"threat":0.6,"intensity":0.7,"valence":-0.4,"arousal":0.8})
        sm = brain.get_summary(); v2.append(sm['valence'])
        print(f"  tick {sm['tick']:3d}: action={str(sm['action']):10s}  émotion={sm['emotion']:15s}  valence={sm['valence']:+.3f}")
    avg1 = sum(v1)/len(v1); avg2 = sum(v2)/len(v2)
    print(f"\n  Résultat: nouveauté sécurisée={avg1:+.3f}  menaçante={avg2:+.3f}")
    print(f"  → Différenciation curiosité/anxiété: {'OUI ✓' if avg1 > avg2 else 'NON'}")


def exp_memory(brain: Brain) -> None:
    print(f"\n{'='*60}\nEXPÉRIENCE: Mémoire émotionnelle vs Neutre\n{'='*60}")
    print("\n[Phase 1] Encodage de stimuli neutres")
    for i in range(3):
        brain.perceive({"modality":"neutral","intensity":0.4,"valence":0.0,"arousal":0.2,"pattern":f"neutral_{i}"})
    neutral_traces = list(brain.hippocampus._memory_traces)
    print(f"  Épisodes encodés: {brain.hippocampus._episode_counter}")
    print("\n[Phase 2] Encodage de stimuli émotionnels")
    for i in range(3):
        v = 0.8 if i % 2 == 0 else -0.8
        brain.perceive({"modality":"emotional","intensity":0.9,"valence":v,"arousal":0.85,
                        "pattern":f"emotional_{i}","reward":0.7 if v > 0 else 0.0,"threat":0.0 if v > 0 else 0.7})
    emotional_traces = [t for t in brain.hippocampus._memory_traces if t not in neutral_traces]
    print(f"  Épisodes encodés: {brain.hippocampus._episode_counter}")
    for t in emotional_traces:
        print(f"    Trace #{t.episode_id}: force={t.strength:.3f}  tag_émotionnel={t.emotional_tag:.3f}  valence={t.valence:+.3f}")
    print("\n[Phase 3] Repos (consolidation)")
    for _ in range(5): brain.tick()
    print("\n[Phase 4] Comparaison des forces")
    all_t = brain.hippocampus._memory_traces
    neut = [t for t in all_t if t.emotional_tag < 0.2]
    emot = [t for t in all_t if t.emotional_tag >= 0.2]
    avg_n = sum(t.strength for t in neut) / max(1, len(neut))
    avg_e = sum(t.strength for t in emot) / max(1, len(emot))
    print(f"  Traces neutres       ({len(neut):2d}): force moyenne = {avg_n:.3f}")
    print(f"  Traces émotionnelles ({len(emot):2d}): force moyenne = {avg_e:.3f}")
    print(f"  → Avantage émotionnel: {avg_e - avg_n:+.3f}  {'OUI ✓' if avg_e > avg_n else 'NON'}")


def exp_fatigue(brain: Brain) -> None:
    print(f"\n{'='*60}\nEXPÉRIENCE: Fatigue cognitive et récupération\n{'='*60}")
    print("\n[Phase 1] Charge intensive")
    for i in range(12):
        brain.perceive({"modality":"cognitive","intensity":0.9,"novelty":0.7,"valence":0.1,"arousal":0.7,"pattern":f"task_{i%3}"})
        sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: PFC_fatigue={brain.pfc.fatigue:.3f}  PFC_load={sm['pfc_load']:.3f}  action={str(sm['action']):10s}  émotion={sm['emotion']}")
    peak = brain.pfc.fatigue
    print(f"\n  >> Fatigue PFC au pic: {peak:.3f}")
    print("\n[Phase 2] Repos — récupération")
    for i in range(8):
        brain.tick(); sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: PFC_fatigue={brain.pfc.fatigue:.3f}  mind_wandering={sm['mind_wandering']}  émotion={sm['emotion']}")
    recovered = brain.pfc.fatigue
    print(f"\n  >> Récupération: {peak:.3f} → {recovered:.3f}  {'OUI ✓' if recovered < peak * 0.7 else 'PARTIELLE'}")
    print("\n[Phase 3] Retour à la tâche")
    for i in range(4):
        brain.perceive({"modality":"cognitive","intensity":0.9,"novelty":0.7,"valence":0.1,"arousal":0.7,"pattern":f"task_{i%3}"})
        sm = brain.get_summary()
        print(f"  tick {sm['tick']:3d}: PFC_fatigue={brain.pfc.fatigue:.3f}  action={str(sm['action']):10s}")


def run_demo(brain: Brain) -> None:
    print("\n" + "="*72)
    print("  DEEP SANCTUARY — Démo")
    print("="*72)
    stimuli = [
        ("Paysage paisible",    {"modality":"visual","novelty":0.7,"valence":0.5,"arousal":0.3,"intensity":0.6,"pattern":"nature"}),
        ("Danger soudain",      {"modality":"threat","threat":0.8,"valence":-0.7,"arousal":0.9,"intensity":0.9,"novelty":0.9}),
        ("Contact social",      {"modality":"social","reward":0.5,"valence":0.5,"arousal":0.4,"intensity":0.6}),
        ("Musique entraînante", {"modality":"music", "reward":0.6,"valence":0.6,"arousal":0.5,"intensity":0.7}),
    ]
    for name, stim in stimuli:
        print(f"\n→ Stimulus: {name}")
        brain.perceive(stim)
        print_state(brain)
    print("\nRepos (4 ticks)...")
    for _ in range(4): brain.tick()
    print_state(brain)


def run_free(brain: Brain, ticks: int) -> None:
    print(f"\n{'='*72}\n  Simulation libre — {ticks} ticks\n{'='*72}")
    for i in range(ticks):
        if i % 5 == 2:
            brain.perceive({
                "modality": random.choice(["visual","sound","touch","social"]),
                "novelty": random.uniform(0.1, 0.9), "valence": random.uniform(-0.5, 0.8),
                "arousal": random.uniform(0.2, 0.7), "intensity": random.uniform(0.3, 0.8),
            })
        else:
            brain.tick()
        sm = brain.get_summary()
        wander = "[wandering]" if sm["mind_wandering"] else ""
        print(f"  tick {brain._tick:3d}: {sm['emotion']:15s}  v={sm['valence']:+.3f}  action={str(sm['action']):10s}  conscience={sm['consciousness_level']:.3f} {wander}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 — POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deep Sanctuary — Architecture Cognitive Humaine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
exemples:
  python3 deep_sanctuary.py --demo
  python3 deep_sanctuary.py --exp stress
  python3 deep_sanctuary.py --exp all
  python3 deep_sanctuary.py --ticks 30
        """
    )
    parser.add_argument("--demo",  action="store_true",  help="Démo rapide avec affichage complet")
    parser.add_argument("--exp",   type=str, default="emotion",
                        choices=["emotion","stress","curiosity","memory","fatigue","all"],
                        help="Expérience à lancer (défaut: emotion)")
    parser.add_argument("--ticks", type=int, default=0,   help="Simulation libre N ticks")
    args = parser.parse_args()

    brain = Brain()
    print("\n  ✦ Deep Sanctuary initialisé — cerveau prêt")

    if args.demo:
        run_demo(brain)
    elif args.ticks > 0:
        run_free(brain, args.ticks)
    elif args.exp == "all":
        for fn in [exp_emotion, exp_stress, exp_curiosity, exp_memory, exp_fatigue]:
            fn(Brain())   # cerveau frais pour chaque expérience
    elif args.exp == "emotion":
        exp_emotion(brain)
    elif args.exp == "stress":
        exp_stress(brain)
    elif args.exp == "curiosity":
        exp_curiosity(brain)
    elif args.exp == "memory":
        exp_memory(brain)
    elif args.exp == "fatigue":
        exp_fatigue(brain)

    print("\n  ✦ Simulation terminée.\n")


if __name__ == "__main__":
    main()
