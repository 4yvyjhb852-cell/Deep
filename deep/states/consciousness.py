"""
Moniteur de Conscience (Consciousness Monitor)

La conscience est l'une des grandes questions ouvertes de la science.
Ici on implémente une approximation basée sur la Global Workspace Theory
(Baars, Dehaene):

La conscience émerge quand:
1. Un contenu atteint le "Global Workspace" (PFC + réseau fronto-pariétal)
2. Ce contenu est "broadcast" largement à d'autres régions
3. Il y a une forte compétition entre représentations (attention sélective)
4. Il y a un niveau d'éveil suffisant (thalamus ouvert)

Niveaux de conscience implémentés:
- 0.0: Inconscient (tronc cérébral uniquement, traitement automatique)
- 0.3: Subconscient (traitement implicite, mémoire procédurale)
- 0.6: Conscient (accès au Global Workspace, attention dirigée)
- 0.9: Méta-conscient (conscience de sa propre conscience, introspection)

Phénomènes modélisés:
- Accès conscient vs traitement non conscient (cécité d'inattention)
- Fluctuations de la conscience (attention wandering)
- Corrélats neuraux de la conscience (NCC)
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deep.regions.prefrontal_cortex import PrefrontalCortex
    from deep.regions.thalamus import Thalamus
    from deep.regions.default_mode_network import DefaultModeNetwork
    from deep.core.neural_signal import NeuralSignal


class ConsciousnessMonitor:
    """Estime le niveau de conscience émergent."""

    def __init__(self):
        self._level: float = 0.5          # Niveau de conscience 0–1
        self._content: str = ""           # Contenu conscient actuel
        self._global_workspace: list = [] # Informations en espace global
        self._meta_awareness: float = 0.0 # Méta-conscience / introspection
        self._history: list[dict] = []
        self._tick: int = 0

    def update(
        self,
        pfc: "PrefrontalCortex",
        thalamus: "Thalamus",
        dmn: "DefaultModeNetwork",
        signals: list["NeuralSignal"],
        tick: int,
    ) -> None:
        self._tick = tick

        # La conscience requiert:
        # 1. Une porte thalamique ouverte (éveil)
        # 2. Un PFC actif (Global Workspace)
        # 3. Un faible niveau de fatigue

        thalamic_gate   = thalamus.attention_gate
        pfc_activation  = pfc.activation
        pfc_fatigue_factor = max(0.2, 1.0 - pfc.fatigue * 0.6)

        # Compétition des signaux dans le Global Workspace
        # Plus il y a de signaux forts et variés → plus la conscience est nette
        strong_signals = [s for s in signals if s.strength > 0.4]
        signal_diversity = len(set(s.signal_type for s in strong_signals))
        workspace_richness = min(1.0, signal_diversity * 0.15 + len(strong_signals) * 0.05)

        # Le DMN actif sans tâche = conscience intérieure (rêverie)
        dmn_contribution = dmn.activation * 0.3 if dmn.mind_wandering else 0.0

        # Calcul du niveau de conscience
        new_level = (
            thalamic_gate   * 0.25
            + pfc_activation * 0.30
            + pfc_fatigue_factor * 0.15
            + workspace_richness * 0.20
            + dmn_contribution * 0.10
        )
        self._level = self._level * 0.8 + new_level * 0.2

        # Méta-conscience: conscience de ses propres états
        # Emerge de l'introspection (PFC monitoring ses propres processus)
        if pfc.cognitive_load < 0.7 and pfc_activation > 0.4:
            internal_signals = [s for s in signals if s.signal_type == "internal"]
            if internal_signals:
                self._meta_awareness = min(1.0,
                    self._meta_awareness * 0.8
                    + len(internal_signals) * 0.1
                )
            else:
                self._meta_awareness *= 0.9
        else:
            self._meta_awareness *= 0.85

        # Contenu conscient (qu'est-ce qui est dans l'espace global?)
        if strong_signals:
            dominant = max(strong_signals, key=lambda s: s.strength)
            self._content = f"{dominant.source}→{dominant.signal_type}"
        elif dmn.mind_wandering:
            self._content = "internal_thought"
        else:
            self._content = "background"

        # Mise à jour du Global Workspace
        self._global_workspace = [
            {"source": s.source, "type": s.signal_type, "strength": round(s.strength, 3)}
            for s in strong_signals[:5]  # Limite de la capacité attentionnelle
        ]

        self._history.append({
            "tick":           tick,
            "level":          round(self._level, 3),
            "meta_awareness": round(self._meta_awareness, 3),
            "content":        self._content,
        })
        if len(self._history) > 100:
            self._history.pop(0)

    def current_state(self) -> dict:
        # Étiquette qualitative du niveau de conscience
        if self._level < 0.2:
            label = "unconscious"
        elif self._level < 0.4:
            label = "subconscious"
        elif self._level < 0.65:
            label = "conscious"
        elif self._level < 0.85:
            label = "focused"
        else:
            label = "heightened"

        return {
            "level":            round(self._level, 3),
            "label":            label,
            "meta_awareness":   round(self._meta_awareness, 3),
            "content":          self._content,
            "global_workspace": self._global_workspace,
        }
