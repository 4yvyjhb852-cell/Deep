"""
Expérience 5: Fatigue cognitive et récupération

Question: La fatigue cognitive émerge-t-elle avec l'usage intensif?
Les performances se dégradent-elles sous charge prolongée?
Le repos restaure-t-il les capacités?
"""
from __future__ import annotations
from deep.core.brain import Brain
from deep.experiments.base_experiment import Experiment


class FatigueRecoveryExperiment(Experiment):
    def __init__(self):
        super().__init__(
            name="fatigue_recovery",
            description="Émergence de la fatigue cognitive et récupération"
        )

    def run(self, brain: Brain) -> dict:
        print(f"\n{'='*60}")
        print(f"EXPÉRIENCE: {self.name}")
        print(f"{'='*60}")

        # Phase 1: Charge cognitive intensive
        print("\n[Phase 1] Charge cognitive intensive prolongée")
        for i in range(12):
            state = brain.perceive({
                "modality":  "cognitive",
                "intensity": 0.9,
                "novelty":   0.7,
                "valence":   0.1,
                "arousal":   0.7,
                "pattern":   f"complex_task_{i % 3}",
                "stimulus_id": f"task_{i}",
            })
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: "
                  f"PFC_fatigue={brain.pfc.fatigue:.3f} "
                  f"PFC_load={summary['pfc_load']:.3f} "
                  f"action={str(summary['action']):10s} "
                  f"émotion={summary['emotion']}")
            self._record(state['tick'], {
                "phase": "intensive",
                "pfc_fatigue":  round(brain.pfc.fatigue, 3),
                "pfc_load":     summary['pfc_load'],
                "action":       summary['action'],
                "emotion":      summary['emotion'],
            })

        peak_fatigue = brain.pfc.fatigue
        print(f"\n  >> Fatigue PFC au pic: {peak_fatigue:.3f}")

        # Phase 2: Repos complet
        print("\n[Phase 2] Repos — récupération")
        for i in range(8):
            state = brain.tick()
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: "
                  f"PFC_fatigue={brain.pfc.fatigue:.3f} "
                  f"mind_wandering={summary['mind_wandering']} "
                  f"émotion={summary['emotion']}")
            self._record(state['tick'], {
                "phase": "rest",
                "pfc_fatigue":    round(brain.pfc.fatigue, 3),
                "mind_wandering": summary['mind_wandering'],
                "emotion":        summary['emotion'],
            })

        recovered_fatigue = brain.pfc.fatigue
        print(f"\n  >> Récupération: {peak_fatigue:.3f} → {recovered_fatigue:.3f} "
              f"({'OUI ✓' if recovered_fatigue < peak_fatigue * 0.7 else 'PARTIELLE'})")

        # Phase 3: Retour à la tâche — performance restaurée?
        print("\n[Phase 3] Retour à la tâche après repos")
        for i in range(4):
            state = brain.perceive({
                "modality":  "cognitive",
                "intensity": 0.9,
                "novelty":   0.7,
                "valence":   0.1,
                "arousal":   0.7,
                "pattern":   f"complex_task_{i % 3}",
                "stimulus_id": f"task_post_{i}",
            })
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: "
                  f"PFC_fatigue={brain.pfc.fatigue:.3f} "
                  f"action={str(summary['action']):10s}")
            self._record(state['tick'], {
                "phase": "post_rest",
                "pfc_fatigue": round(brain.pfc.fatigue, 3),
                "action": summary['action'],
            })

        self._record(brain._tick, {
            "peak_fatigue":      round(peak_fatigue, 3),
            "recovered_fatigue": round(recovered_fatigue, 3),
            "recovery_ratio":    round(1 - recovered_fatigue / max(0.01, peak_fatigue), 3),
        })

        return self.summary()
