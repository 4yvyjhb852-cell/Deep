# Deep
Deep Sanctuary — Architecture Cognitive Humaine

## Vision

Ce projet implémente une architecture cognitive complète inspirée du cerveau humain.
L'objectif est d'observer si des phénomènes comme les **émotions**, la **fatigue**,
la **curiosité**, la **mémoire émotionnelle** et la **conscience** peuvent **émerger**
naturellement de l'interaction entre composantes — sans être programmés directement.

## Architecture

```
deep/
├── core/
│   ├── brain.py              # Orchestrateur central (Global Workspace Theory)
│   ├── neural_signal.py      # Unité de communication entre régions
│   ├── neurotransmitter.py   # Système neurochimique partagé (dopamine, sérotonine...)
│   └── synapse.py            # Connexions plastiques (règle de Hebb)
├── regions/
│   ├── brainstem.py          # Tronc: éveil, survie, SRAA
│   ├── thalamus.py           # Routeur sensoriel, porte attentionnelle
│   ├── amygdala.py           # Évaluation émotionnelle, peur, récompense
│   ├── hippocampus.py        # Mémoire épisodique, encodage, récupération
│   ├── prefrontal_cortex.py  # Exécutif: planification, décision, mémoire de travail
│   ├── basal_ganglia.py      # Sélection d'action, apprentissage par renforcement
│   ├── cerebellum.py         # Timing, prédiction motrice, mémoire procédurale
│   ├── insula.py             # Intéroception, ressenti corporel, empathie
│   ├── cingulate_cortex.py   # Détection de conflit, monitoring d'erreur
│   ├── sensory_cortex.py     # Traitement perceptuel
│   └── default_mode_network.py  # Rêverie, narration de soi, créativité
├── states/
│   ├── emotional_state.py    # Tracker d'état émotionnel émergent
│   └── consciousness.py      # Moniteur de conscience (Global Workspace)
└── experiments/
    ├── emotion_emergence.py   # Émergence des émotions
    ├── stress_response.py     # Réponse au stress et récupération
    ├── curiosity_exploration.py  # Curiosité vs anxiété
    ├── memory_formation.py    # Mémoire émotionnelle vs neutre
    └── fatigue_recovery.py    # Fatigue cognitive et récupération
```

## Bases Théoriques

- **Global Workspace Theory** (Baars, Dehaene) — La conscience comme espace de diffusion global
- **Predictive Processing** (Friston) — Le cerveau comme machine prédictive
- **Somatic Marker Hypothesis** (Damasio) — Les émotions guident la décision
- **Hebbian Learning** — "Neurons that fire together, wire together"
- **Dimensional Emotion Model** (Russell) — Valence × Arousal

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
# Démo rapide
python3 main.py --demo

# Expérience émergence des émotions
python3 main.py --exp emotion

# Réponse au stress
python3 main.py --exp stress

# Curiosité et exploration
python3 main.py --exp curiosity

# Mémoire émotionnelle
python3 main.py --exp memory

# Fatigue cognitive
python3 main.py --exp fatigue

# Toutes les expériences
python3 main.py --exp all

# Simulation libre N ticks
python3 main.py --ticks 30
```

## Phénomènes Observés (Émergents)

| Phénomène | Source | Observé |
|-----------|--------|---------|
| Émotions (joie, peur, mélancolie...) | Amygdale × Insula × Neurotransmetteurs | ✓ |
| Inertie émotionnelle | Lissage temporel multi-sources | ✓ |
| Stress aigu vs chronique | Accumulation cortisol | ✓ |
| Dégradation mémoire sous stress | Cortisol → encodage | ✓ |
| Fatigue cognitive et récupération | Charge PFC × repos | ✓ |
| Mind-wandering (rêverie) | DMN actif au repos | ✓ |
| Curiosité vs anxiété | Novelty × Valence | ✓ |
| Avantage mémoriel émotionnel | Tag amygdalien × Hippocampe | ✓ |
| Conscience variable | Thalamus × PFC × Global Workspace | ✓ |
| Apprentissage par renforcement | TD-error × Dopamine × BG | ✓ |

## Neurotransmetteurs Modélisés

| Molécule | Rôle | Effets Émergents |
|----------|------|-----------------|
| Dopamine | Récompense, motivation | Drive à agir, apprentissage |
| Sérotonine | Humeur, bien-être | Tolérance stress, humeur positive |
| Noradrénaline | Éveil, attention | Fight-or-flight, hypervigilance |
| Acétylcholine | Mémoire, attention fine | Encodage mémoriel |
| GABA | Inhibition | Calme, réduction anxiété |
| Glutamate | Excitation | Activation, apprentissage |
| Cortisol | Stress (axe HPA) | Dégradation PFC, mémoire |
| Ocytocine | Lien social | Confiance, ouverture sociale |
| Endorphines | Plaisir, analgésie | Bien-être, résilience |
