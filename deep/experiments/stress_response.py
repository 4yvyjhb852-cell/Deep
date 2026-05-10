"""
Expérience 2: Réponse au stress et récupération

Question: Le système développe-t-il une réponse au stress qui:
1. Monte rapidement face au danger (survie)
2. Dégrade les fonctions cognitives sous stress prolongé (cortisol)
3. Récupère lentement à l'arrêt du stresseur
4. Crée une mémoire émotionnelle du stresseur (conditionnement)
"""
from __future__ import annotations
from deep.core.brain import Brain
from deep.experiments.base_experiment import Experiment


class StressResponseExperiment(Experiment):
    def __init__(self):
        super().__init__(
            name="stress_response",
            description="Réponse au stress aigu et chronique, récupération"
        )

    def run(self, brain: Brain) -> dict:
        print(f"\n{'='*60}")
        print(f"EXPÉRIENCE: {self.name}")
        print(f"{'='*60}")

        # Phase 1: Baseline (mesure de référence)
        print("\n[Phase 1] Baseline — état de repos")
        for i in range(3):
            state = brain.tick()
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: stress={summary['stress']:.3f} "
                  f"cortisol={brain.nt.cortisol:.3f} "
                  f"valence={summary['valence']:+.3f}")
            self._record(state['tick'], {"phase": "baseline", **summary})

        baseline_stress = brain.nt.cortisol

        # Phase 2: Stresseur aigu intense
        print("\n[Phase 2] Stresseur aigu (menace forte soudaine)")
        for i in range(3):
            state = brain.perceive({
                "modality":  "threat",
                "threat":    0.95,
                "novelty":   1.0,
                "intensity": 1.0,
                "valence":  -0.9,
                "arousal":   1.0,
                "stimulus_id": "acute_stressor",
            })
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: stress={summary['stress']:.3f} "
                  f"cortisol={brain.nt.cortisol:.3f} "
                  f"NE={brain.nt.norepinephrine:.3f} "
                  f"action={summary['action']}")
            self._record(state['tick'], {"phase": "acute_stress", **summary,
                                          "cortisol": brain.nt.cortisol,
                                          "norepinephrine": brain.nt.norepinephrine})

        peak_stress = brain.nt.cortisol

        # Phase 3: Stress chronique (stresseur répété à intensité modérée)
        print("\n[Phase 3] Stress chronique (exposition répétée)")
        wm_loads = []
        for i in range(8):
            state = brain.perceive({
                "modality":  "threat",
                "threat":    0.5,
                "intensity": 0.5,
                "valence":  -0.4,
                "arousal":   0.6,
                "stimulus_id": "chronic_stressor",
            })
            summary = brain.get_summary()
            wm_loads.append(summary['pfc_load'])
            print(f"  tick {state['tick']:3d}: cortisol={brain.nt.cortisol:.3f} "
                  f"mémoire_enc={brain.nt.memory_encoding_efficiency:.3f} "
                  f"pfc_load={summary['pfc_load']:.3f}")
            self._record(state['tick'], {"phase": "chronic_stress", **summary,
                                          "cortisol": brain.nt.cortisol,
                                          "memory_efficiency": brain.nt.memory_encoding_efficiency})

        print(f"\n  >> Dégradation PFC sous stress chronique: "
              f"charge moyenne={sum(wm_loads)/len(wm_loads):.3f}")

        # Phase 4: Récupération
        print("\n[Phase 4] Récupération post-stress")
        for i in range(10):
            state = brain.tick()
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: stress={summary['stress']:.3f} "
                  f"cortisol={brain.nt.cortisol:.3f} "
                  f"émotion={summary['emotion']}")
            self._record(state['tick'], {"phase": "recovery", **summary,
                                          "cortisol": brain.nt.cortisol})

        # Phase 5: Réexposition — conditionnement observé?
        print("\n[Phase 5] Réexposition — conditionnement mémoriel?")
        state = brain.perceive({
            "modality":  "cue",
            "stimulus_id": "acute_stressor",  # Même ID = rappel conditionné
            "threat":    0.2,  # Faible menace objective
            "intensity": 0.3,
            "valence":   0.0,
            "arousal":   0.2,
        })
        summary = brain.get_summary()
        print(f"  tick {state['tick']:3d}: réponse conditionnée?")
        print(f"    stress={summary['stress']:.3f} (attendu > baseline si conditionné)")
        print(f"    émotion={summary['emotion']}")
        conditioned = summary['stress'] > baseline_stress * 1.3
        print(f"    → CONDITIONNEMENT {'DÉTECTÉ' if conditioned else 'NON DÉTECTÉ'}")

        self._record(state['tick'], {"phase": "reexposure", **summary,
                                      "conditioned": conditioned})

        return self.summary()
