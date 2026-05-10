"""
Thalamus

Le thalamus est le grand routeur du cerveau.
Presque toutes les informations sensorielles passent par lui
avant d'atteindre le cortex (sauf l'olfaction).

Rôles:
- Relai sensoriel → filtre et amplifie selon l'attention
- Porte de l'éveil (modulation du niveau de conscience)
- Synchronisation des oscillations corticales (ondes gamma, alpha, delta)
- Régulation de la conscience (le thalamus "éteint" le cortex pendant le sommeil)

Connexions: Brainstem → Thalamus → Cortex sensoriel, PFC
            Thalamus ↔ Cortex (boucle réciproque bidirectionnelle)
"""
from __future__ import annotations
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


class Thalamus(BrainRegion):
    def __init__(self):
        super().__init__("thalamus", capacity=30)
        self.attention_gate: float = 0.5     # Ouverture de la porte attentionnelle
        self.sensory_buffer: list[dict] = [] # Signaux sensoriels en attente de routage

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        arousal_received = 0.0
        sensory_signals = []
        executive_signals = []  # Top-down depuis PFC → modulent l'attention

        for sig in signals:
            if sig.signal_type == "arousal":
                arousal_received = max(arousal_received, sig.strength)
            elif sig.signal_type == "sensory":
                sensory_signals.append(sig)
            elif sig.signal_type == "executive":
                # Top-down attention: le PFC peut élargir ou restreindre la porte
                executive_signals.append(sig)

        # La porte attentionnelle est modulée par:
        # - L'éveil (noradrénaline, arousal du tronc)
        # - Les instructions top-down du PFC
        # - L'acétylcholine (attention fine)
        attention_top_down = (
            sum(s.content.get("attention_direction", 0.5) for s in executive_signals)
            / max(1, len(executive_signals))
        ) if executive_signals else self.attention_gate

        self.attention_gate = min(1.0, max(0.1,
            arousal_received * 0.3
            + attention_top_down * 0.3
            + nt.acetylcholine * 0.2
            + nt.norepinephrine * 0.1
            - nt.gaba * 0.2
        ))

        # Routage des signaux sensoriels vers le cortex sensoriel
        # La force est modulée par la porte attentionnelle
        for sig in sensory_signals:
            routed_strength = sig.strength * self.attention_gate
            if routed_strength > 0.05:  # Seuil minimal de transmission
                self._emit(NeuralSignal(
                    source="thalamus",
                    target="sensory_cortex",
                    signal_type="sensory",
                    content=sig.content,
                    strength=routed_strength,
                    valence=sig.valence,
                    arousal=min(1.0, sig.arousal * self.attention_gate),
                ))

        # Aussi vers l'amygdale (voie rapide, non filtrée — détection de menace)
        for sig in sensory_signals:
            if sig.content.get("threat", 0) > 0.2 or sig.valence < -0.3:
                self._emit(NeuralSignal(
                    source="thalamus",
                    target="amygdala",
                    signal_type="sensory",
                    content=sig.content,
                    strength=sig.strength * 0.8,  # Voie rapide, peu filtrée
                    valence=sig.valence,
                    arousal=sig.arousal,
                ))

        # Signal de retour vers le PFC: état de la porte attentionnelle
        self._emit(self._make_signal(
            target="prefrontal_cortex",
            signal_type="arousal",
            content={"attention_gate": self.attention_gate, "arousal": arousal_received},
            strength=self.attention_gate,
            arousal=arousal_received,
        ))
