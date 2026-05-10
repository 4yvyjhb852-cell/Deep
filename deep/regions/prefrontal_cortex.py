"""
Cortex Préfrontal (Prefrontal Cortex — PFC)

Le PFC est le siège de la pensée complexe, de la personnalité et
du comportement social. C'est ce qui nous distingue le plus des autres animaux.

Rôles:
- Mémoire de travail (maintien et manipulation d'informations actives)
- Planification et prise de décision
- Contrôle inhibiteur (supprimer les impulsions)
- Régulation émotionnelle (top-down sur l'amygdale)
- Attention sélective (top-down sur le thalamus)
- Flexibilité cognitive (changer de règle selon le contexte)
- Intégration du marqueur somatique (Damasio: les émotions guident la décision)
- Traitement du langage (Broca, aire 44/45)
- Théorie de l'esprit (mentalisation)
- Conscience réflexive (méta-cognition)

Divisions importantes:
- DLPFC (dorsolatéral): mémoire de travail, raisonnement abstrait
- VMPFC (ventromédial): décision sous incertitude, marqueur somatique
- OFC (orbitofrontal): valeur, récompense, prise de décision morale
- ACC (cingulaire antérieur): détection de conflits, monitoring d'erreur
"""
from __future__ import annotations
from collections import deque
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


class WorkingMemory:
    """Mémoire de travail — capacité limitée, ~7±2 éléments."""
    CAPACITY = 7

    def __init__(self):
        self._slots: deque = deque(maxlen=self.CAPACITY)
        self._focus: dict | None = None

    def add(self, item: dict, priority: float = 0.5) -> None:
        self._slots.append({"item": item, "priority": priority})

    def get_all(self) -> list[dict]:
        return [s["item"] for s in self._slots]

    def get_focus(self) -> dict | None:
        if not self._slots:
            return None
        return max(self._slots, key=lambda s: s["priority"])["item"]

    def clear_low_priority(self, threshold: float = 0.2) -> None:
        self._slots = deque(
            [s for s in self._slots if s["priority"] > threshold],
            maxlen=self.CAPACITY
        )

    @property
    def load(self) -> float:
        """Charge cognitive 0–1."""
        return len(self._slots) / self.CAPACITY


class PrefrontalCortex(BrainRegion):
    def __init__(self):
        super().__init__("prefrontal_cortex", capacity=30)
        self._fatigue_managed_internally = True  # Gère sa propre fatigue
        self.working_memory = WorkingMemory()
        self.current_plan: list[str] = []
        self.emotional_state: dict = {"fear": 0.0, "reward": 0.0, "valence": 0.0}
        self.inhibition_signal: float = 0.0   # Force du contrôle inhibiteur
        self.attention_focus: str | None = None
        self.cognitive_load: float = 0.0
        self.prediction_error: float = 0.0    # Écart entre attendu et reçu
        self._expected_state: dict = {}

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        sensory_inputs = []
        emotional_inputs = []
        mnemonic_inputs = []
        arousal_inputs = []

        for sig in signals:
            if sig.signal_type == "sensory":
                sensory_inputs.append(sig)
            elif sig.signal_type == "emotional":
                emotional_inputs.append(sig)
            elif sig.signal_type == "mnemonic":
                mnemonic_inputs.append(sig)
            elif sig.signal_type == "arousal":
                arousal_inputs.append(sig)

        # --- Mise à jour du marqueur somatique (Damasio) ---
        # Les signaux émotionnels de l'amygdale informent la décision
        if emotional_inputs:
            em = emotional_inputs[-1]  # Dernier signal émotionnel
            self.emotional_state = em.content

        # --- Mémoire de travail ---
        for sig in sensory_inputs:
            priority = sig.strength * (1 + abs(sig.valence) * 0.5)
            self.working_memory.add(sig.content, priority=priority)

        for sig in mnemonic_inputs:
            if sig.content.get("retrieved"):
                self.working_memory.add(sig.content, priority=0.8)

        # --- Charge cognitive ---
        self.cognitive_load = (
            self.working_memory.load * 0.6
            + self.fatigue * 0.3
            + nt.cortisol * 0.1
        )

        # La fatigue du PFC s'accumule avec la charge cognitive (pas l'activation brute)
        # Le PFC est la région la plus sujette à la fatigue cognitive
        has_external = any(s.signal_type in ("sensory", "emotional") for s in signals)
        if has_external and self.cognitive_load > 0.05:
            # Sous charge cognitive externe: accumulation proportionnelle à la charge
            self.fatigue = min(1.0, self.fatigue + self.cognitive_load * 0.15)
        elif not has_external:
            # Repos ou pensée interne seulement: récupération
            self.fatigue = max(0.0, self.fatigue - 0.03)

        # --- Erreur de prédiction (cerveau = machine prédictive, Friston) ---
        # Compare les valeurs numériques entre l'état prédit et l'état reçu
        if sensory_inputs and self._expected_state:
            received = sensory_inputs[0].content
            all_keys = set(self._expected_state.keys()) | set(received.keys())
            numeric_errors = []
            for key in all_keys:
                exp_val = self._expected_state.get(key, 0.0)
                rec_val = received.get(key, 0.0)
                if isinstance(exp_val, (int, float)) and isinstance(rec_val, (int, float)):
                    numeric_errors.append(abs(float(exp_val) - float(rec_val)))
            if numeric_errors:
                self.prediction_error = min(1.0, sum(numeric_errors) / len(numeric_errors))
            else:
                self.prediction_error *= 0.9
        else:
            self.prediction_error *= 0.9

        # --- Régulation émotionnelle (top-down sur l'amygdale) ---
        fear = self.emotional_state.get("fear", 0.0)
        inhibition_needed = fear * nt.serotonin
        self.inhibition_signal = inhibition_needed

        # --- Génération d'outputs ---
        # 1. Direction de l'attention → Thalamus
        self._emit(self._make_signal(
            target="thalamus",
            signal_type="executive",
            content={
                "attention_direction": min(1.0, max(0.1,
                    0.5 + self.prediction_error * 0.3
                    - self.cognitive_load * 0.2
                )),
                "inhibit": self.inhibition_signal > 0.5,
            },
            strength=max(0.2, 1.0 - self.cognitive_load),
            arousal=nt.arousal_level,
        ))

        # 2. Si besoin de récupération mémorielle
        focus = self.working_memory.get_focus()
        if focus and self.prediction_error > 0.4:
            self._emit(self._make_signal(
                target="hippocampus",
                signal_type="executive",
                content={"retrieve": list(focus.keys())[0] if focus else None},
                strength=0.6,
            ))

        # 3. Décision / Action → Noyaux gris
        if not self.cognitive_load > 0.9:  # Si pas en surcharge
            decision = self._make_decision(nt)
            if decision:
                self._emit(self._make_signal(
                    target="basal_ganglia",
                    signal_type="executive",
                    content=decision,
                    strength=max(0.3, nt.motivation),
                    valence=self.emotional_state.get("valence", 0.0),
                ))

        # 4. Signal intéroceptif → Insula (conscience du corps)
        if abs(self.emotional_state.get("valence", 0.0)) > 0.3:
            self._emit(self._make_signal(
                target="insula",
                signal_type="interoceptive",
                content={"monitored_state": self.emotional_state},
                strength=0.5,
            ))

        # Nettoyage de la mémoire de travail
        self.working_memory.clear_low_priority()

        # Mise à jour de l'état prédit
        if sensory_inputs:
            self._expected_state = sensory_inputs[-1].content.copy()

    def _make_decision(self, nt: NeurotransmitterSystem) -> dict | None:
        """
        Prise de décision intégrant:
        - Les informations en mémoire de travail
        - Le marqueur somatique (état émotionnel)
        - La motivation (dopamine)
        - La fatigue
        """
        focus = self.working_memory.get_focus()
        if not focus:
            return None

        fear = self.emotional_state.get("fear", 0.0)
        reward = self.emotional_state.get("reward", 0.0)
        valence = self.emotional_state.get("valence", 0.0)

        # Marqueur somatique: si peur élevée → tendance à éviter
        if fear > 0.4 and nt.serotonin < 0.5:
            action = "avoid"
            confidence = fear
        elif reward > 0.25 and nt.dopamine > 0.4:
            action = "approach"
            confidence = reward * nt.motivation
        elif self.prediction_error > 0.35:
            action = "explore"   # Curiosité → explorer l'inattendu
            confidence = self.prediction_error * 0.6
        elif valence > 0.2:
            action = "engage"
            confidence = valence * 0.7
        else:
            action = "maintain"
            confidence = 0.3

        return {
            "action": action,
            "confidence": round(confidence, 3),
            "working_memory_load": round(self.working_memory.load, 3),
            "cognitive_load": round(self.cognitive_load, 3),
        }

    def get_state(self) -> dict:
        base = super().get_state()
        base.update({
            "cognitive_load":  round(self.cognitive_load, 3),
            "wm_load":         round(self.working_memory.load, 3),
            "prediction_error": round(self.prediction_error, 3),
            "inhibition":      round(self.inhibition_signal, 3),
            "emotional_state": self.emotional_state,
        })
        return base
