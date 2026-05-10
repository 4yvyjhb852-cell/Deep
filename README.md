# Deep Sanctuary
Architecture cognitive humaine — simulation de l'émergence

> Un cerveau artificiel où les **émotions, états et comportements émergent**
> de l'interaction entre composantes — sans être programmés directement.

---

## Installation rapide

```bash
pip install -r requirements.txt
```

**Dépendances:** `numpy`, `rich` (affichage terminal), `dataclasses-json`

---

## Utilisation (API pour une IA ou un programme)

### Import et création

```python
from deep.api import DeepBrain

brain = DeepBrain()
```

---

## Méthode principale: `perceive(stimulus) → PerceptionResult`

Soumet un stimulus sensoriel. C'est l'input principal du système.

### Paramètres du stimulus (dict)

| Clé | Type | Plage | Défaut | Description |
|-----|------|-------|--------|-------------|
| `modality` | str | voir liste | `"unknown"` | Type de stimulus |
| `intensity` | float | 0.0–1.0 | 0.5 | Intensité brute |
| `valence` | float | **-1.0–+1.0** | 0.0 | Charge émotionnelle (-1=négatif, +1=positif) |
| `arousal` | float | 0.0–1.0 | 0.3 | Activation (0=endormant, 1=excitant) |
| `novelty` | float | 0.0–1.0 | 0.5 | Nouveauté (déclenche curiosité) |
| `threat` | float | 0.0–1.0 | 0.0 | Niveau de danger perçu |
| `reward` | float | 0.0–1.0 | 0.0 | Récompense immédiate |
| `pattern` | str | — | `""` | Identifiant visuel (pour habituation/reconnaissance) |
| `stimulus_id` | str | — | `""` | ID unique (pour conditionnement et mémoire) |

#### Valeurs valides pour `modality`
```
"visual"    "auditory"  "tactile"   "olfactory"  "taste"
"social"    "threat"    "reward"    "cognitive"  "music"
"pain"      "internal"  "unknown"
```

### Exemples de stimuli

```python
# Paysage beau et paisible
brain.perceive({"modality": "visual", "valence": 0.6, "arousal": 0.3,
                "intensity": 0.7, "novelty": 0.5, "pattern": "nature"})

# Danger soudain et inconnu
brain.perceive({"modality": "threat", "threat": 0.9, "valence": -0.8,
                "arousal": 0.95, "intensity": 0.9, "novelty": 1.0})

# Interaction sociale chaleureuse
brain.perceive({"modality": "social", "reward": 0.6, "valence": 0.5,
                "arousal": 0.4, "intensity": 0.6})

# Tâche cognitive difficile
brain.perceive({"modality": "cognitive", "novelty": 0.8, "intensity": 0.9,
                "arousal": 0.7, "valence": 0.1})

# Musique entraînante
brain.perceive({"modality": "music", "reward": 0.5, "valence": 0.6,
                "arousal": 0.6, "intensity": 0.7, "pattern": "jazz_upbeat"})

# Douleur modérée
brain.perceive({"modality": "pain", "threat": 0.4, "valence": -0.5,
                "arousal": 0.6, "intensity": 0.5})
```

---

## Sortie: `PerceptionResult`

Retourné par `perceive()` et `tick()`. Tous les champs sont accessibles directement.

### État émotionnel

| Attribut | Type | Plage | Description |
|----------|------|-------|-------------|
| `emotion` | str | — | Étiquette anglaise (ex: `"joy"`, `"fear"`, `"calm"`) |
| `emotion_fr` | str | — | Étiquette française (ex: `"joie / euphorie"`) |
| `valence` | float | -1.0–+1.0 | Valence émotionnelle intégrée |
| `arousal` | float | 0.0–1.0 | Niveau d'éveil |
| `emotion_intensity` | float | 0.0–1.0 | Intensité globale de l'émotion |
| `emotion_duration` | int | ≥1 | Nombre de ticks dans cet état |

#### Émotions possibles

| Étiquette | Condition | Zone valence/arousal |
|-----------|-----------|---------------------|
| `joy` / joie | Valence +, arousal haut | v > 0.5, a > 0.65 |
| `excitement` / excitation | Valence +, arousal moyen-haut | v > 0.25, a > 0.55 |
| `contentment` / contentement | Valence +, arousal bas | v > 0.35, a < 0.35 |
| `calm` / calme | Valence légèrement +, arousal très bas | v > 0.1, a < 0.25 |
| `serene` / serein | Zone centrale positive | v > 0, a < 0.5 |
| `neutral` / neutre | Zone centrale | -0.3 < v < 0.3, 0.15 < a < 0.55 |
| `alert` / alerte | Légèrement positif, arousal moyen | — |
| `anxiety` / anxiété | Valence -, arousal moyen | v < -0.15, a > 0.45 |
| `fear` / peur | Valence très -, arousal très haut | v < -0.45, a > 0.6 |
| `anger` / colère | Valence -, arousal haut | v < -0.25, a > 0.5 |
| `sadness` / tristesse | Valence très -, arousal bas | v < -0.35, a < 0.45 |
| `boredom` / ennui | Légèrement négatif, arousal très bas | v < -0.05, a < 0.35 |
| `melancholy` / mélancolie | Négatif modéré, arousal moyen-bas | — |
| `tired` / fatigué | Très bas arousal | a < 0.2 |

### Conscience

| Attribut | Type | Plage | Description |
|----------|------|-------|-------------|
| `consciousness` | float | 0.0–1.0 | Niveau de conscience (Global Workspace) |
| `consciousness_label` | str | — | `"unconscious"` / `"subconscious"` / `"conscious"` / `"focused"` / `"heightened"` |
| `meta_awareness` | float | 0.0–1.0 | Méta-conscience, introspection |
| `mind_wandering` | bool | — | `True` si le DMN est actif (rêverie, pensée spontanée) |

### Décision

| Attribut | Type | Description |
|----------|------|-------------|
| `action` | str or None | Action sélectionnée par les noyaux gris |
| `action_confidence` | float | Confiance dans l'action (0–1) |

#### Actions possibles
| Action | Déclenchement |
|--------|---------------|
| `"approach"` | Récompense détectée, dopamine élevée |
| `"avoid"` | Peur/menace élevée, sérotonine basse |
| `"explore"` | Nouveauté + erreur de prédiction |
| `"engage"` | Valence positive modérée |
| `"maintain"` | État stable, pas de signal fort |
| `"rest"` | Faible drive général |

### Charge cognitive et fatigue

| Attribut | Type | Description |
|----------|------|-------------|
| `cognitive_load` | float 0–1 | Charge du cortex préfrontal (>0.9 = surcharge) |
| `pfc_fatigue` | float 0–1 | Fatigue accumulée du PFC |

### Neurochimie émergente

| Attribut | Type | Description |
|----------|------|-------------|
| `stress` | float 0–1 | Niveau de stress émergent (cortisol + NE) |
| `motivation` | float 0–1 | Motivation (dopamine + NE) |
| `mood` | float -1–+1 | Humeur neurochimique de fond |

### Mémoire

| Attribut | Type | Description |
|----------|------|-------------|
| `memory_count` | int | Nombre de traces mnésiques actives |
| `last_encoded` | bool | Un souvenir vient-il d'être encodé? |

### Tick

| Attribut | Type | Description |
|----------|------|-------------|
| `tick` | int | Cycle de traitement interne (≥1) |

---

## Autres méthodes

### `tick() → PerceptionResult`
Avance d'un cycle sans stimulus. Permet la décroissance, la rêverie (DMN), la consolidation.
```python
result = brain.tick()
```

### `reward(value: float)`
Donne un feedback d'apprentissage après une action.
```python
brain.perceive(stimulus)
# ... l'action est exécutée dans l'environnement ...
brain.reward(+0.8)   # Succès
brain.reward(-0.5)   # Échec
```

### `inject(neurotransmitters: dict)`
Modifie directement les niveaux neurochimiques (delta, pas valeur absolue).
```python
brain.inject({"serotonin": -0.3})           # Simule dépression
brain.inject({"dopamine": 0.4})             # Stimulant
brain.inject({"cortisol": 0.5})             # Stress intense
brain.inject({"gaba": 0.3, "cortisol":-0.2})  # Anxiolytique
brain.inject({"oxytocin": 0.2})             # Lien affectif
```

### `get_neurochemistry() → NeurochemistryState`
```python
nc = brain.get_neurochemistry()
print(nc.dopamine, nc.serotonin, nc.cortisol)
```

### `get_region_activations() → dict[str, float]`
```python
acts = brain.get_region_activations()
# {"brainstem": 0.12, "amygdala": 0.45, "prefrontal_cortex": 0.23, ...}
```

### `get_memory_traces() → list[dict]`
```python
memories = brain.get_memory_traces()
# [{"episode_id": 1, "strength": 0.82, "emotional_tag": 0.71, "valence": -0.6}, ...]
```

### `get_emotional_history() → list[dict]`
```python
history = brain.get_emotional_history()
# [{"valence": 0.3, "arousal": 0.4, "label": "serene", "intensity": 0.35}, ...]
```

---

## Exemple complet (scénario narratif)

```python
from deep.api import DeepBrain

brain = DeepBrain()

# Matin calme
for _ in range(3):
    r = brain.tick()
    print(r)   # neutre / serein

# Surprise positive
r = brain.perceive({
    "modality": "reward", "reward": 0.7, "valence": 0.6,
    "arousal": 0.6, "novelty": 0.7, "intensity": 0.8
})
brain.reward(0.7)
print(r.emotion)        # → "excitement" ou "enthusiasm"
print(r.action)         # → "approach"

# Menace soudaine
r = brain.perceive({
    "modality": "threat", "threat": 0.85, "valence": -0.8,
    "arousal": 0.9, "intensity": 0.9
})
print(r.emotion)        # → "fear" ou "anxiety"
print(r.stress)         # → élevé
print(r.action)         # → "avoid"
nc = brain.get_neurochemistry()
print(nc.norepinephrine)  # → élevé (fight-or-flight)

# Retour au calme progressif
for _ in range(5):
    r = brain.tick()
    print(f"tick {r.tick}: {r.emotion} (valence={r.valence:+.2f})")
# Montre la décroissance progressive: fear → anxiety → neutral → calm

# Interaction sociale apaisante
brain.inject({"oxytocin": 0.15})
r = brain.perceive({
    "modality": "social", "valence": 0.4, "arousal": 0.35,
    "reward": 0.4, "intensity": 0.6
})
print(r.emotion)              # → "contentment" ou "calm"
print(brain.get_neurochemistry().oxytocin)  # → élevé
```

---

## Lancer les expériences prédéfinies

```bash
python3 main.py --exp emotion     # Émergence des émotions
python3 main.py --exp stress      # Réponse au stress
python3 main.py --exp curiosity   # Curiosité vs anxiété
python3 main.py --exp memory      # Mémoire émotionnelle
python3 main.py --exp fatigue     # Fatigue cognitive
python3 main.py --exp all         # Tout
python3 main.py --demo            # Démo rapide
python3 main.py --ticks 30        # Simulation libre
```

---

## Architecture interne

```
INPUT (stimulus dict)
        │
        ▼
   [Brainstem]──────────────────────► Éveil, SRAA, menace rapide
        │
        ▼
   [Thalamus]──────────────────────► Routage sensoriel, porte attentionnelle
        │              │
        ▼              ▼
[Sensory Cortex]  [Amygdala]──────► Évaluation émotionnelle rapide
        │              │
        ▼              ▼
[Hippocampus] ◄── [Amygdala]──────► Marquage émotionnel mémoriel
        │
        ▼
[Prefrontal Cortex]────────────────► Décision, mémoire de travail, prédiction
        │
        ▼
[Basal Ganglia]────────────────────► Sélection d'action (Actor-Critic)
        │
        ▼
[Cerebellum]───────────────────────► Raffinement, timing, mémoire procédurale
        │
        ▼
OUTPUT (action: approach/avoid/explore/engage/maintain/rest)

PARALLÈLE:
[Insula] ─────────────────────────► Ressenti corporel → [Cingulate] → alarme
[Default Mode Network] ───────────► Rêverie, narration de soi (au repos)
[Neurotransmitter System] ────────► Bain chimique global modulant tout
```

---

## Phénomènes émergents documentés

| Phénomène | Comment l'observer |
|-----------|-------------------|
| **Émotions nommées** | Lire `result.emotion` après plusieurs ticks |
| **Inertie émotionnelle** | Les émotions changent progressivement, pas instantanément |
| **Stress et récupération** | `--exp stress` ou injecter du cortisol et observer |
| **Mind-wandering** | `result.mind_wandering` après ticks de repos |
| **Fatigue** | `result.pfc_fatigue` monte sous charge, descend au repos |
| **Curiosité vs anxiété** | Même `novelty=1.0` avec `threat=0` vs `threat=0.8` |
| **Mémoire émotionnelle** | `get_memory_traces()` — emotional_tag élevé = mieux retenu |
| **Conditionnement** | Même `stimulus_id` répété → réponse apprise |
| **Habituation** | Même `pattern` répété → arousal décroît |
