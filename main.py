"""
Deep Sanctuary — Simulation cognitive
======================================

Point d'entrée principal. Lance toutes les expériences et affiche
l'état émergent du cerveau.

Usage:
    python main.py                  # Lance toutes les expériences
    python main.py --demo           # Démo interactive rapide
    python main.py --exp emotion    # Une seule expérience
    python main.py --ticks 20       # Simulation libre N ticks
"""
import sys
import argparse

from deep.core.brain import Brain
from deep.visualization.state_monitor import print_brain_state
from deep.experiments.emotion_emergence import EmotionEmergenceExperiment
from deep.experiments.stress_response import StressResponseExperiment
from deep.experiments.curiosity_exploration import CuriosityExplorationExperiment
from deep.experiments.memory_formation import MemoryFormationExperiment
from deep.experiments.fatigue_recovery import FatigueRecoveryExperiment


def run_demo(brain: Brain) -> None:
    """Démo rapide: quelques stimuli variés."""
    print("\n" + "="*70)
    print("  DEEP SANCTUARY — Démo cognitive")
    print("="*70)
    print("\nInitialisation du cerveau...")

    stimuli = [
        {"modality": "visual", "novelty": 0.8, "valence": 0.3,
         "arousal": 0.5, "intensity": 0.6, "pattern": "beautiful_scene"},
        {"modality": "threat", "threat": 0.7, "valence": -0.7,
         "arousal": 0.9, "intensity": 0.8, "novelty": 0.9},
        {"modality": "social", "reward": 0.5, "valence": 0.5,
         "arousal": 0.4, "intensity": 0.6, "novelty": 0.4},
        {"modality": "music", "reward": 0.6, "valence": 0.6,
         "arousal": 0.5, "intensity": 0.7, "novelty": 0.5},
    ]

    for i, stimulus in enumerate(stimuli):
        print(f"\nStimulus {i+1}: {stimulus['modality']}")
        brain.perceive(stimulus)
        print_brain_state(brain)

    # Quelques ticks de repos
    print("\nRepos (3 ticks)...")
    for _ in range(3):
        brain.tick()
    print_brain_state(brain)


def run_all_experiments(brain: Brain) -> None:
    """Lance toutes les expériences en séquence."""
    experiments = [
        EmotionEmergenceExperiment(),
        StressResponseExperiment(),
        CuriosityExplorationExperiment(),
        MemoryFormationExperiment(),
        FatigueRecoveryExperiment(),
    ]

    all_results = {}
    for exp in experiments:
        # Chaque expérience repart d'un cerveau frais
        fresh_brain = Brain()
        results = exp.run(fresh_brain)
        all_results[exp.name] = results
        print(f"\n  → Expérience '{exp.name}' terminée: {results['ticks']} ticks")

    print("\n" + "="*70)
    print("  RÉSUMÉ DES EXPÉRIENCES")
    print("="*70)
    for name, res in all_results.items():
        print(f"\n  [{name}]")
        if res["results"]:
            last = res["results"][-1]
            for k, v in last.items():
                if k not in ("tick",):
                    print(f"    {k}: {v}")


def run_free_simulation(brain: Brain, ticks: int = 20) -> None:
    """Simulation libre sans stimuli externes — observer le DMN et le repos."""
    print(f"\n{'='*70}")
    print(f"  Simulation libre — {ticks} ticks")
    print(f"{'='*70}")
    for i in range(ticks):
        # Stimuli aléatoires occasionnels
        if i % 5 == 2:
            import random
            brain.perceive({
                "modality": random.choice(["visual", "sound", "touch"]),
                "novelty":  random.uniform(0.1, 0.9),
                "valence":  random.uniform(-0.5, 0.8),
                "arousal":  random.uniform(0.2, 0.7),
                "intensity": random.uniform(0.3, 0.8),
                "pattern": f"random_{i}",
            })
        else:
            brain.tick()

        summary = brain.get_summary()
        wander = "[wandering]" if summary["mind_wandering"] else ""
        print(f"  tick {brain._tick:3d}: {summary['emotion']:15s} "
              f"valence={summary['valence']:+.3f} "
              f"action={str(summary['action']):10s} "
              f"conscience={summary['consciousness_level']:.3f} "
              f"{wander}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Deep Sanctuary — Simulation cognitive")
    parser.add_argument("--demo",  action="store_true", help="Démo rapide")
    parser.add_argument("--exp",   type=str, default=None,
                        choices=["emotion", "stress", "curiosity", "memory", "fatigue", "all"],
                        help="Expérience à lancer")
    parser.add_argument("--ticks", type=int, default=0,
                        help="Simulation libre N ticks")
    args = parser.parse_args()

    brain = Brain()

    if args.demo:
        run_demo(brain)
    elif args.ticks > 0:
        run_free_simulation(brain, args.ticks)
    elif args.exp == "emotion" or args.exp is None:
        EmotionEmergenceExperiment().run(brain)
    elif args.exp == "stress":
        StressResponseExperiment().run(brain)
    elif args.exp == "curiosity":
        CuriosityExplorationExperiment().run(brain)
    elif args.exp == "memory":
        MemoryFormationExperiment().run(brain)
    elif args.exp == "fatigue":
        FatigueRecoveryExperiment().run(brain)
    elif args.exp == "all":
        run_all_experiments(brain)

    print("\n✓ Simulation terminée.")


if __name__ == "__main__":
    main()
