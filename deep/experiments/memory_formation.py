"""
Expérience 4: Formation et récupération de la mémoire

Question: La mémoire émotionnelle est-elle différente de la mémoire froide?
Les souvenirs émotionnellement chargés sont-ils mieux retenus?

Protocole:
1. Présenter des stimuli neutres et émotionnels
2. Laisser le temps (ticks de repos = consolidation)
3. Tester la récupération
4. Comparer la force des traces mnésiques neutres vs émotionnelles
"""
from __future__ import annotations
from deep.core.brain import Brain
from deep.experiments.base_experiment import Experiment


class MemoryFormationExperiment(Experiment):
    def __init__(self):
        super().__init__(
            name="memory_formation",
            description="Mémoire émotionnelle vs mémoire neutre"
        )

    def run(self, brain: Brain) -> dict:
        print(f"\n{'='*60}")
        print(f"EXPÉRIENCE: {self.name}")
        print(f"{'='*60}")

        # Phase 1: Encodage de stimuli neutres
        print("\n[Phase 1] Encodage de stimuli neutres")
        for i in range(3):
            brain.perceive({
                "modality":  "neutral",
                "intensity": 0.4,
                "valence":   0.0,
                "arousal":   0.2,
                "pattern":   f"neutral_item_{i}",
                "stimulus_id": f"neutral_{i}",
                "novelty":   0.5,
            })
        traces_before_neutral = brain.hippocampus._episode_counter
        print(f"  Épisodes encodés: {brain.hippocampus._episode_counter}")
        neutral_traces = [t for t in brain.hippocampus._memory_traces]

        # Phase 2: Encodage de stimuli émotionnels
        print("\n[Phase 2] Encodage de stimuli émotionnels (forts)")
        for i in range(3):
            brain.perceive({
                "modality":  "emotional_event",
                "intensity": 0.9,
                "valence":   0.8 if i % 2 == 0 else -0.8,  # Alternance +/-
                "arousal":   0.85,
                "pattern":   f"emotional_item_{i}",
                "stimulus_id": f"emotional_{i}",
                "novelty":   0.8,
                "reward":    0.7 if i % 2 == 0 else 0.0,
                "threat":    0.0 if i % 2 == 0 else 0.7,
            })
        emotional_traces = [
            t for t in brain.hippocampus._memory_traces
            if t not in neutral_traces
        ]
        print(f"  Épisodes encodés: {brain.hippocampus._episode_counter}")
        for t in emotional_traces:
            print(f"    Trace #{t.episode_id}: force={t.strength:.3f} "
                  f"tag_émotionnel={t.emotional_tag:.3f} valence={t.valence:+.3f}")

        # Phase 3: Consolidation (ticks de repos)
        print("\n[Phase 3] Consolidation (repos)")
        for i in range(5):
            brain.tick()

        # Phase 4: Comparaison des forces de traces
        print("\n[Phase 4] Comparaison des forces après consolidation")
        all_traces = brain.hippocampus._memory_traces
        neutral  = [t for t in all_traces if t.emotional_tag < 0.2]
        emotional = [t for t in all_traces if t.emotional_tag >= 0.2]

        avg_neutral   = sum(t.strength for t in neutral) / max(1, len(neutral))
        avg_emotional = sum(t.strength for t in emotional) / max(1, len(emotional))

        print(f"  Traces neutres    ({len(neutral):2d}): force moyenne = {avg_neutral:.3f}")
        print(f"  Traces émotionnelles ({len(emotional):2d}): force moyenne = {avg_emotional:.3f}")
        print(f"  → Avantage émotionnel: {avg_emotional - avg_neutral:+.3f} "
              f"({'OUI ✓' if avg_emotional > avg_neutral else 'NON'})")

        self._record(brain._tick, {
            "neutral_count":       len(neutral),
            "emotional_count":     len(emotional),
            "avg_neutral_strength":   round(avg_neutral, 3),
            "avg_emotional_strength": round(avg_emotional, 3),
            "emotional_advantage":    round(avg_emotional - avg_neutral, 3),
        })

        return self.summary()
