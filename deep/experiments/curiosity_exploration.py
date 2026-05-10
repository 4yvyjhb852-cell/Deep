"""
Expérience 3: Curiosité et exploration

Question: La curiosité émerge-t-elle spontanément face à la nouveauté?
La curiosité est-elle différente de l'anxiété (deux états de haute arousal
face à l'inconnu, mais de valence opposée)?

Protocole:
1. Stimuli nouveaux → curiosité (si sécurité) ou anxiété (si danger)
2. Stimuli répétés → habituation (la curiosité diminue)
3. Imprévisibilité → maintien de la curiosité
4. Observer si l'action "explore" émerge naturellement
"""
from __future__ import annotations
from deep.core.brain import Brain
from deep.experiments.base_experiment import Experiment


class CuriosityExplorationExperiment(Experiment):
    def __init__(self):
        super().__init__(
            name="curiosity_exploration",
            description="Emergence de la curiosité face à la nouveauté"
        )

    def run(self, brain: Brain) -> dict:
        print(f"\n{'='*60}")
        print(f"EXPÉRIENCE: {self.name}")
        print(f"{'='*60}")

        # Phase 1: Stimulus nouveau non-menaçant → curiosité?
        print("\n[Phase 1] Nouveauté sécurisée — curiosité?")
        for i in range(5):
            state = brain.perceive({
                "modality":  "visual",
                "novelty":   0.9,
                "threat":    0.0,
                "reward":    0.3,
                "intensity": 0.5,
                "valence":   0.2,
                "arousal":   0.5,
                "pattern":   f"novel_pattern_{i}",
                "stimulus_id": f"novel_{i}",
            })
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: action={str(summary['action']):10s} "
                  f"émotion={summary['emotion']:15s} "
                  f"pred_error={brain.pfc.prediction_error:.3f}")
            self._record(state['tick'], {"phase": "novel_safe", **summary,
                                          "pred_error": brain.pfc.prediction_error})

        # Phase 2: Habituation — même stimulus répété
        print("\n[Phase 2] Habituation — stimulus répété")
        for i in range(6):
            state = brain.perceive({
                "modality":  "visual",
                "novelty":   0.1,   # Plus novel
                "threat":    0.0,
                "intensity": 0.5,
                "valence":   0.1,
                "arousal":   0.3,
                "pattern":   "familiar_pattern",  # Même pattern
                "stimulus_id": "familiar",
            })
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: action={str(summary['action']):10s} "
                  f"émotion={summary['emotion']:15s} "
                  f"arousal={summary['arousal']:.3f}")
            self._record(state['tick'], {"phase": "habituation", **summary})

        # Phase 3: Surprise — attendait le familier, reçoit quelque chose d'inattendu
        print("\n[Phase 3] Surprise — rupture d'attente")
        for i in range(4):
            state = brain.perceive({
                "modality":  "visual",
                "novelty":   1.0,   # Très novel
                "threat":    0.0,
                "reward":    0.4,
                "intensity": 0.7,
                "valence":   0.3,
                "arousal":   0.7,
                "pattern":   "totally_unexpected",
                "stimulus_id": "surprise",
            })
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: action={str(summary['action']):10s} "
                  f"émotion={summary['emotion']:15s} "
                  f"pred_error={brain.pfc.prediction_error:.3f} "
                  f"consciousness={summary['consciousness_level']:.3f}")
            self._record(state['tick'], {"phase": "surprise", **summary,
                                          "pred_error": brain.pfc.prediction_error})

        # Phase 4: Même nouveauté MAIS avec menace → anxiété plutôt que curiosité?
        print("\n[Phase 4] Nouveauté menaçante — anxiété vs curiosité?")
        for i in range(4):
            state = brain.perceive({
                "modality":  "unknown",
                "novelty":   0.9,
                "threat":    0.6,   # Menaçant
                "intensity": 0.7,
                "valence":  -0.4,
                "arousal":   0.8,
                "pattern":   "threatening_novel",
                "stimulus_id": "threat_novel",
            })
            summary = brain.get_summary()
            print(f"  tick {state['tick']:3d}: action={str(summary['action']):10s} "
                  f"émotion={summary['emotion']:15s} "
                  f"valence={summary['valence']:+.3f}")
            self._record(state['tick'], {"phase": "threat_novelty", **summary})

        print("\n  >> Comparaison:")
        curious_phase  = [r for r in self.results if r.get("phase") == "novel_safe"]
        anxiety_phase  = [r for r in self.results if r.get("phase") == "threat_novelty"]
        if curious_phase and anxiety_phase:
            avg_curious_v = sum(r["valence"] for r in curious_phase) / len(curious_phase)
            avg_anxiety_v = sum(r["valence"] for r in anxiety_phase) / len(anxiety_phase)
            print(f"     Nouveauté sécurisée: valence moy={avg_curious_v:+.3f}")
            print(f"     Nouveauté menaçante: valence moy={avg_anxiety_v:+.3f}")
            print(f"     → Différenciation curiosité/anxiété: "
                  f"{'OUI ✓' if avg_curious_v > avg_anxiety_v else 'NON'}")

        return self.summary()
