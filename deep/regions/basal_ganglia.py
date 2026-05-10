"""
Noyaux Gris Centraux (Basal Ganglia)

Les noyaux gris sont le système de sélection de l'action et d'apprentissage
par renforcement du cerveau.

Rôles:
- Sélection de l'action (quel comportement exécuter parmi les candidats?)
- Apprentissage par renforcement (dopamine = signal de récompense temporelle)
- Formation des habitudes (comportements automatisés)
- Inhibition des actions non sélectionnées (voie indirecte)
- Motivation et drive (initiateur de l'action)

Modèle implémenté: Actor-Critic simplifié
- Acteur: choisit l'action basée sur l'état actuel
- Critique: évalue si l'action était bonne (TD-error = erreur de prédiction
  de récompense temporelle)

Connexions: PFC → BG (plans et intentions)
            BG → Thalamus → Cortex moteur (sélection d'action)
            Substantia nigra → BG (dopamine pour apprentissage)
"""
from __future__ import annotations
from deep.regions.base_region import BrainRegion
from deep.core.neural_signal import NeuralSignal
from deep.core.neurotransmitter import NeurotransmitterSystem


class BasalGanglia(BrainRegion):
    def __init__(self):
        super().__init__("basal_ganglia", capacity=15)
        self._action_values: dict[str, float] = {
            "approach": 0.5,
            "avoid":    0.5,
            "explore":  0.5,
            "engage":   0.5,
            "maintain": 0.5,
            "rest":     0.4,
        }
        self._last_action: str | None = None
        self._last_value: float = 0.0
        self.selected_action: str | None = None
        self.habit_strength: dict[str, float] = {}  # Habitudes apprises

    def _process_signals(
        self, signals: list[NeuralSignal], nt: NeurotransmitterSystem
    ) -> None:

        executive_signals = [s for s in signals if s.signal_type == "executive"]
        reward_signals    = [s for s in signals if s.signal_type == "reward"]

        # --- Mise à jour de l'apprentissage par renforcement ---
        for sig in reward_signals:
            if self._last_action:
                reward = sig.content.get("reward_received", 0.0)
                td_error = reward - self._last_value  # Erreur temporelle de différence
                lr = nt.dopamine * 0.1               # Le taux d'apprentissage dépend de la dopamine
                self._action_values[self._last_action] = min(1.0, max(0.0,
                    self._action_values[self._last_action] + lr * td_error
                ))
                # TD error positif → burst de dopamine (inattendu reward)
                if td_error > 0.2:
                    nt.modulate({"dopamine": td_error * 0.1})
                # TD error négatif → dip de dopamine (déception)
                elif td_error < -0.2:
                    nt.modulate({"dopamine": td_error * 0.05})

        if not executive_signals:
            # Pas d'input exécutif → maintien de l'action courante
            return

        last_executive = executive_signals[-1]
        suggested_action = last_executive.content.get("action", "maintain")
        confidence = last_executive.content.get("confidence", 0.5)

        # --- Sélection d'action (voie directe vs indirecte) ---
        # La valeur apprise + la confiance du PFC + l'influence des habitudes
        action_scores = {}
        for action, base_value in self._action_values.items():
            score = base_value * 0.5

            # Bonus si c'est l'action suggérée par le PFC
            if action == suggested_action:
                score += confidence * 0.4

            # Bonus habitude (comportement automatisé)
            habit = self.habit_strength.get(action, 0.0)
            score += habit * 0.3 * nt.dopamine

            # La dopamine basse → moins d'initiative (apathie)
            score *= max(0.2, nt.motivation)

            action_scores[action] = score

        # Sélection: Winner-Take-All (voie directe BG)
        selected = max(action_scores, key=action_scores.get)
        selected_score = action_scores[selected]

        self.selected_action = selected
        self._last_action = selected
        self._last_value = self._action_values.get(selected, 0.5)

        # Formation d'habitude: action répétée → habitude
        if self._last_action == selected:
            prev_habit = self.habit_strength.get(selected, 0.0)
            self.habit_strength[selected] = min(1.0, prev_habit + 0.01)
        else:
            # Réduction des autres habitudes (inhibition compétitive)
            for a in self.habit_strength:
                if a != selected:
                    self.habit_strength[a] = max(0.0, self.habit_strength[a] - 0.005)

        # Émission: action sélectionnée → cortex moteur (via thalamus)
        self._emit(self._make_signal(
            target="cerebellum",
            signal_type="motor",
            content={
                "action": selected,
                "score":  round(selected_score, 3),
                "habit":  round(self.habit_strength.get(selected, 0.0), 3),
            },
            strength=selected_score,
            valence=last_executive.valence,
        ))

        # Rétroaction vers le PFC (confirmation de l'action sélectionnée)
        self._emit(self._make_signal(
            target="prefrontal_cortex",
            signal_type="reward",
            content={
                "action_selected": selected,
                "action_score":    round(selected_score, 3),
            },
            strength=0.4,
        ))

    def get_state(self) -> dict:
        base = super().get_state()
        base.update({
            "selected_action": self.selected_action,
            "action_values":   {k: round(v, 3) for k, v in self._action_values.items()},
            "top_habit":       max(self.habit_strength, key=self.habit_strength.get)
                               if self.habit_strength else None,
        })
        return base
