"""
Expérience 1: Émergence des émotions

Question: Les émotions émergent-elles naturellement de l'interaction
des composantes, sans être programmées directement?

Protocole:
1. Présenter des stimuli de différentes valences
2. Observer comment l'état émotionnel global émerge
3. Vérifier que les transitions entre émotions sont progressives
   (les émotions ont une inertie — on ne passe pas de la joie à la peur en un tick)
4. Vérifier que la neurochimie influence l'émotion ressentie
"""
from __future__ import annotations
from deep.core.brain import Brain
from deep.experiments.base_experiment import Experiment


class EmotionEmergenceExperiment(Experiment):
    def __init__(self):
        super().__init__(
            name="emotion_emergence",
            description="Observer l'émergence des émotions à partir des composantes"
        )

    def run(self, brain: Brain) -> dict:
        print(f"\n{'='*60}")
        print(f"EXPÉRIENCE: {self.name}")
        print(f"{'='*60}")

        # Phase 1: Stimulus de récompense (joie?)
        print("\n[Phase 1] Stimulus de récompense positif")
        for i in range(5):
            state = brain.perceive({
                "modality":    "reward",
                "reward":      0.8,
                "novelty":     0.6,
                "intensity":   0.7,
                "valence":     0.7,
                "arousal":     0.6,
                "stimulus_id": "reward_A",
            })
            brain.inject_reward(0.8)
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: émotion={summary['emotion']:15s} "
                  f"valence={summary['valence']:+.2f} arousal={summary['arousal']:.2f}")
            self._record(state['tick'], {
                "phase": "reward", "emotion": summary['emotion'],
                "valence": summary['valence'], "arousal": summary['arousal']
            })

        # Phase 2: Stimulus de menace (peur?)
        print("\n[Phase 2] Stimulus de menace")
        for i in range(5):
            state = brain.perceive({
                "modality":    "threat",
                "threat":      0.85,
                "novelty":     0.9,
                "intensity":   0.9,
                "valence":    -0.8,
                "arousal":     0.9,
                "stimulus_id": "threat_X",
            })
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: émotion={summary['emotion']:15s} "
                  f"valence={summary['valence']:+.2f} arousal={summary['arousal']:.2f} "
                  f"stress={summary['stress']:.2f}")
            self._record(state['tick'], {
                "phase": "threat", "emotion": summary['emotion'],
                "valence": summary['valence'], "arousal": summary['arousal'],
                "stress": summary['stress']
            })

        # Phase 3: Silence / repos (retour au calme?)
        print("\n[Phase 3] Repos — observation du retour homéostatique")
        for i in range(8):
            state = brain.tick()
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: émotion={summary['emotion']:15s} "
                  f"valence={summary['valence']:+.2f} arousal={summary['arousal']:.2f} "
                  f"mind_wandering={summary['mind_wandering']}")
            self._record(state['tick'], {
                "phase": "rest", "emotion": summary['emotion'],
                "valence": summary['valence'], "arousal": summary['arousal'],
                "mind_wandering": summary['mind_wandering']
            })

        # Phase 4: Stimulus social positif (bien-être social?)
        print("\n[Phase 4] Stimulus social positif (ocytocine?)")
        for i in range(4):
            state = brain.perceive({
                "modality":    "social",
                "social":      True,
                "reward":      0.5,
                "novelty":     0.4,
                "intensity":   0.6,
                "valence":     0.5,
                "arousal":     0.4,
                "stimulus_id": "social_bond",
            })
            brain.nt.modulate({"oxytocin": 0.1})  # Contact social → ocytocine
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: émotion={summary['emotion']:15s} "
                  f"valence={summary['valence']:+.2f} "
                  f"social={brain.nt.social_openness:.2f}")
            self._record(state['tick'], {
                "phase": "social", "emotion": summary['emotion'],
                "valence": summary['valence'], "social": brain.nt.social_openness
            })

        return self.summary()
