"""
Moniteur d'état — Affichage en temps réel de l'état du cerveau.
Utilise la bibliothèque Rich pour un affichage formaté dans le terminal.
"""
from __future__ import annotations

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from deep.core.brain import Brain


def _bar(value: float, width: int = 20, fill: str = "█", empty: str = "░") -> str:
    """Barre de progression ASCII."""
    filled = int(value * width)
    return fill * filled + empty * (width - filled)


def _valence_bar(value: float, width: int = 20) -> str:
    """Barre de valence centrée (-1 à +1)."""
    center = width // 2
    pos = int((value + 1) / 2 * width)
    bar = list("─" * width)
    bar[center] = "┼"
    if pos != center:
        if pos > center:
            for i in range(center, min(pos, width)):
                bar[i] = "+"
        else:
            for i in range(max(pos, 0), center):
                bar[i] = "-"
    bar[max(0, min(pos, width-1))] = "●"
    return "".join(bar)


def print_brain_state(brain: Brain) -> None:
    """Affiche l'état courant du cerveau."""
    state = brain.get_state()
    summary = brain.get_summary()
    nt = brain.nt
    emo = state["emotional_state"]
    con = state["consciousness"]

    if HAS_RICH:
        _rich_display(brain, state, summary, nt, emo, con)
    else:
        _plain_display(brain, state, summary, nt, emo, con)


def _plain_display(brain, state, summary, nt, emo, con) -> None:
    """Affichage texte simple (sans Rich)."""
    print(f"\n{'━'*70}")
    print(f"  DEEP SANCTUARY — Tick #{state['tick']}")
    print(f"{'━'*70}")

    print(f"\n  ÉTAT ÉMOTIONNEL: [{emo['label_fr'].upper()}]  "
          f"(intensité: {emo['intensity']:.2f}, durée: {emo['duration']} ticks)")
    print(f"  Valence:  {_valence_bar(emo['valence'])} {emo['valence']:+.3f}")
    print(f"  Éveil:    {_bar(emo['arousal'])} {emo['arousal']:.3f}")

    print(f"\n  CONSCIENCE: [{con['label'].upper()}]  niveau={con['level']:.3f}")
    print(f"  Méta-conscience: {con['meta_awareness']:.3f}")
    print(f"  Contenu: {con['content']}")

    print(f"\n  NEUROTRANSMETTEURS:")
    print(f"  Dopamine:        {_bar(nt.dopamine, 15)} {nt.dopamine:.3f}  (motivation)")
    print(f"  Sérotonine:      {_bar(nt.serotonin, 15)} {nt.serotonin:.3f}  (humeur)")
    print(f"  Noradrénaline:   {_bar(nt.norepinephrine, 15)} {nt.norepinephrine:.3f}  (éveil)")
    print(f"  Acétylcholine:   {_bar(nt.acetylcholine, 15)} {nt.acetylcholine:.3f}  (mémoire)")
    print(f"  GABA:            {_bar(nt.gaba, 15)} {nt.gaba:.3f}  (inhibition)")
    print(f"  Cortisol:        {_bar(nt.cortisol, 15)} {nt.cortisol:.3f}  (stress)")
    print(f"  Ocytocine:       {_bar(nt.oxytocin, 15)} {nt.oxytocin:.3f}  (social)")

    print(f"\n  RÉGIONS ACTIVES:")
    for name, region_state in state["regions"].items():
        act = region_state["activation"]
        fat = region_state["fatigue"]
        if act > 0.1:
            print(f"  {name:30s} act={_bar(act, 10)} {act:.2f}  "
                  f"fatigue={fat:.2f}")

    print(f"\n  ACTION: {summary['action']}  "
          f"| Mind-wandering: {summary['mind_wandering']}")
    print(f"  PFC charge: {summary['pfc_load']:.3f}")
    print(f"{'━'*70}\n")


def _rich_display(brain, state, summary, nt, emo, con) -> None:
    """Affichage enrichi avec Rich."""
    console = Console()

    # Tableau neurotransmetteurs
    nt_table = Table(title="Neurotransmetteurs", box=box.SIMPLE, show_header=True)
    nt_table.add_column("Molécule", style="cyan")
    nt_table.add_column("Niveau")
    nt_table.add_column("Rôle", style="dim")

    for name, role, value in [
        ("Dopamine",       "motivation/récompense",  nt.dopamine),
        ("Sérotonine",     "humeur/bien-être",        nt.serotonin),
        ("Noradrénaline",  "éveil/attention",         nt.norepinephrine),
        ("Acétylcholine",  "mémoire/attention fine",  nt.acetylcholine),
        ("GABA",           "inhibition/calme",        nt.gaba),
        ("Glutamate",      "excitation/apprentissage",nt.glutamate),
        ("Cortisol",       "stress",                  nt.cortisol),
        ("Ocytocine",      "lien social/confiance",   nt.oxytocin),
        ("Endorphines",    "plaisir/analgésie",       nt.endorphins),
    ]:
        color = "green" if value > 0.6 else ("red" if value < 0.3 else "yellow")
        bar = f"[{color}]{_bar(value, 12)}[/{color}] {value:.3f}"
        nt_table.add_row(name, bar, role)

    # Tableau régions
    reg_table = Table(title="Régions cérébrales", box=box.SIMPLE)
    reg_table.add_column("Région", style="cyan")
    reg_table.add_column("Activation")
    reg_table.add_column("Fatigue")

    for name, rs in state["regions"].items():
        act = rs["activation"]
        fat = rs["fatigue"]
        act_color = "green" if act > 0.5 else ("dim" if act < 0.1 else "yellow")
        fat_color = "red" if fat > 0.6 else "green"
        reg_table.add_row(
            name.replace("_", " "),
            f"[{act_color}]{_bar(act, 10)} {act:.2f}[/{act_color}]",
            f"[{fat_color}]{fat:.2f}[/{fat_color}]",
        )

    # Panel état émotionnel
    emotion_color = (
        "green" if emo["valence"] > 0.3
        else "red" if emo["valence"] < -0.3
        else "yellow"
    )
    emotion_panel = Panel(
        f"[bold {emotion_color}]{emo['label_fr'].upper()}[/bold {emotion_color}]\n\n"
        f"Valence:   {_valence_bar(emo['valence'], 24)} {emo['valence']:+.3f}\n"
        f"Éveil:     {_bar(emo['arousal'], 24)} {emo['arousal']:.3f}\n"
        f"Intensité: {_bar(emo['intensity'], 24)} {emo['intensity']:.3f}\n"
        f"Durée:     {emo['duration']} ticks\n\n"
        f"Stress:    {_bar(nt.stress_level, 24)} {nt.stress_level:.3f}\n"
        f"Motivation:{_bar(nt.motivation, 24)} {nt.motivation:.3f}",
        title=f"[bold]État Émotionnel — Tick #{state['tick']}[/bold]",
        border_style=emotion_color,
    )

    # Panel conscience
    con_color = "blue" if con["level"] > 0.5 else "dim"
    con_panel = Panel(
        f"[bold {con_color}]{con['label'].upper()}[/bold {con_color}]\n\n"
        f"Niveau:         {_bar(con['level'], 22)} {con['level']:.3f}\n"
        f"Méta-conscience:{_bar(con['meta_awareness'], 22)} {con['meta_awareness']:.3f}\n"
        f"Contenu:        {con['content']}\n\n"
        f"Action:         [bold]{summary['action']}[/bold]\n"
        f"Mind-wandering: {'[yellow]OUI[/yellow]' if summary['mind_wandering'] else 'non'}\n"
        f"Charge PFC:     {_bar(summary['pfc_load'], 22)} {summary['pfc_load']:.3f}",
        title="[bold]Conscience[/bold]",
        border_style=con_color,
    )

    console.print(Columns([emotion_panel, con_panel]))
    console.print(Columns([nt_table, reg_table]))
