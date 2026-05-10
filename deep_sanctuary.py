#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       DEEP SANCTUARY  v2.0                                  ║
║          Architecture Cognitive Humaine — Corps Numérique Intégré           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Le cerveau ne flotte pas dans le vide. Il est ANCRÉ dans un corps qui       ║
║  reçoit la réalité à travers ses récepteurs — et qui réagit en retour.      ║
║                                                                              ║
║  Tout stimulus est décrit en DIMENSIONS PHYSIQUES BRUTES (pas de labels).   ║
║  L'IA décrit CE QU'ELLE PERÇOIT — le corps et le cerveau en dérivent       ║
║  les effets appropriés, sans être guidés par des noms.                      ║
║                                                                              ║
║  USAGE:                                                                      ║
║    python3 deep_sanctuary.py --demo                                          ║
║    python3 deep_sanctuary.py --exp body     # Corps et réactions             ║
║    python3 deep_sanctuary.py --exp all      # Toutes les expériences         ║
║    python3 deep_sanctuary.py --ticks 40     # Simulation libre               ║
║                                                                              ║
║  API PYTHON (SensoryInput dimensionnel):                                     ║
║    from deep_sanctuary import DeepBrain, SensoryInput                        ║
║    brain = DeepBrain()                                                       ║
║    # Impact soudain fort (sans dire "gifle"):                                ║
║    r = brain.sense(SensoryInput(meca_force=0.85, meca_vitesse=0.95,         ║
║                                  meca_zone=0.2, location="visage"))          ║
║    print(r.emotion_matrix)  # top-3 émotions avec poids                     ║
║    print(r.body_state)      # état physiologique                             ║
║    print(r.impulse)         # élan spontané actuel                           ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  NOUVELLES DANS v2:                                                          ║
║  • SensoryInput: 35 dimensions physiques (mécanique, thermique, auditif,    ║
║    visuel, chimique/récepteur, sémantique, intéroceptif)                     ║
║  • BodySystem: corps numérique avec récepteurs, nociception, ANS, chimie    ║
║  • AutonomicNervousSystem: balance sympathique/parasympathique               ║
║    → 7 métriques corporelles (FC, respiration, tension, pupilles...)        ║
║  • NociceptiveProcessor: douleur A-delta (rapide) + C-fibre (lente),        ║
║    seuil adaptatif, sensibilisation, modulation opioïde                      ║
║  • ChemicalField: PK/PD — substances par profil récepteur, cinétique        ║
║  • ImpulseEngine: élans spontanés (curiosité, social, créatif, repos...)    ║
║  • IntrospectionEngine: le cerveau s'examine lui-même                       ║
║  • EmotionMatrix: top-3 émotions avec poids + humeur de fond                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations
import argparse, math, random, time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Optional


# ─────────────────────────────────────────────────────────────────────────────
# §1  SIGNAL NEURAL
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NeuralSignal:
    source:      str
    target:      str
    signal_type: str
    content:     dict[str, Any]
    strength:    float = 1.0
    valence:     float = 0.0
    arousal:     float = 0.5
    timestamp:   float = field(default_factory=time.time)

    def __post_init__(self):
        self.strength = max(0.0, min(1.0, self.strength))
        self.valence  = max(-1.0, min(1.0, self.valence))
        self.arousal  = max(0.0, min(1.0, self.arousal))

    def attenuate(self, f: float) -> "NeuralSignal":
        return NeuralSignal(self.source, self.target, self.signal_type,
            self.content.copy(), self.strength * f, self.valence, self.arousal * f, self.timestamp)


# ─────────────────────────────────────────────────────────────────────────────
# §2  NEUROTRANSMETTEURS
# ─────────────────────────────────────────────────────────────────────────────

BASELINE_NT = {"dopamine":0.50,"serotonin":0.60,"norepinephrine":0.35,
               "acetylcholine":0.50,"gaba":0.55,"glutamate":0.50,
               "cortisol":0.25,"oxytocin":0.40,"endorphins":0.45}
RECOVERY    = {"dopamine":0.05,"serotonin":0.02,"norepinephrine":0.08,
               "acetylcholine":0.06,"gaba":0.04,"glutamate":0.07,
               "cortisol":0.01,"oxytocin":0.03,"endorphins":0.03}

@dataclass
class NeurotransmitterSystem:
    dopamine:       float = 0.50
    serotonin:      float = 0.60
    norepinephrine: float = 0.35
    acetylcholine:  float = 0.50
    gaba:           float = 0.55
    glutamate:      float = 0.50
    cortisol:       float = 0.25
    oxytocin:       float = 0.40
    endorphins:     float = 0.45

    def _c(self, v):    return max(0.0, min(1.0, v))
    def modulate(self, d):
        for k,v in d.items():
            if hasattr(self,k): setattr(self,k,self._c(getattr(self,k)+v))
    def decay(self):
        for k,b in BASELINE_NT.items():
            r=RECOVERY[k]; c=getattr(self,k); setattr(self,k,self._c(c+(b-c)*r))

    @property
    def mood_valence(self):
        p=self.serotonin*.4+self.dopamine*.3+self.endorphins*.2+self.oxytocin*.1
        n=self.cortisol*.5+max(0,self.norepinephrine-.6)*.3+max(0,self.glutamate-.7)*.2
        return max(-1.0, min(1.0, self._c(p-n)*2-.7))
    @property
    def arousal_level(self):
        return self._c(self.norepinephrine*.4+self.dopamine*.3+self.glutamate*.2-self.gaba*.3)
    @property
    def stress_level(self):
        return self._c(self.cortisol*.5+self.norepinephrine*.3+max(0,self.glutamate-.5)*.2-self.gaba*.2-self.serotonin*.1)
    @property
    def motivation(self):
        return self._c(self.dopamine*.6+self.norepinephrine*.2+self.endorphins*.1-self.cortisol*.2)
    @property
    def social_openness(self):
        return self._c(self.oxytocin*.5+self.serotonin*.3+self.endorphins*.1-self.cortisol*.2)
    @property
    def memory_encoding_efficiency(self):
        return self._c(self.acetylcholine*.5+self.dopamine*.2+self.norepinephrine*.2-self.cortisol*.2)
    @property
    def pain_modulation(self):
        """Force de la modulation descendante de la douleur (opioïdes endogènes)."""
        return self._c(self.endorphins*.7+self.gaba*.2+self.serotonin*.1)
    def snapshot(self):
        return {k:round(getattr(self,k),3) for k in BASELINE_NT}


# ─────────────────────────────────────────────────────────────────────────────
# §3  RÉGION CÉRÉBRALE (classe de base)
# ─────────────────────────────────────────────────────────────────────────────

class BrainRegion(ABC):
    def __init__(self, name:str, capacity:int=10):
        self.name=name; self.activation=0.0; self.fatigue=0.0
        self._buf:deque=deque(maxlen=capacity); self._out:list=[]; self._tick=0
        self._fatigue_managed=False

    def receive(self, s:NeuralSignal): self._buf.append(s)

    def process(self, nt:NeurotransmitterSystem) -> list[NeuralSignal]:
        self._tick+=1; ins=list(self._buf); self._buf.clear(); self._out=[]
        if ins:
            avg=sum(s.strength for s in ins)/len(ins)
            self.activation=min(1.0,self.activation*.7+avg*.3)
            self._process_signals(ins,nt)
        else:
            self.activation*=.85
        if not self._fatigue_managed:
            if self.activation>.15: self.fatigue=min(1.0,self.fatigue+(self.activation-.15)*.05)
            elif not ins: self.fatigue=max(0.0,self.fatigue-.008)
        return list(self._out)

    @abstractmethod
    def _process_signals(self,signals,nt): ...
    def _emit(self,s): self._out.append(s)
    def _make(self,target,stype,content,strength=.5,valence=.0,arousal=.5):
        return NeuralSignal(self.name,target,stype,content,
            max(0.,min(1.,strength*(1.-self.fatigue*.5))),valence,arousal)
    def get_state(self):
        return {"region":self.name,"activation":round(self.activation,3),"fatigue":round(self.fatigue,3)}


# ─────────────────────────────────────────────────────────────────────────────
# §4  INPUT SENSORIEL DIMENSIONNEL
#     Décrit TOUT stimulus par ses dimensions physiques — pas de labels
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SensoryInput:
    """
    Description dimensionnelle d'un stimulus externe ou interne.
    L'IA fournit des valeurs numériques — le corps en dérive les effets.
    PAS DE NOMS (pas "gifle", pas "bière") — uniquement des dimensions.

    EXEMPLES:
      Impact soudain fort:
        SensoryInput(meca_force=0.85, meca_vitesse=0.95, meca_zone=0.2, location="visage")

      Caresse douce sur le bras:
        SensoryInput(meca_force=0.04, meca_vitesse=0.08, meca_zone=0.9,
                     thermal=0.62, meca_duration=0.7, location="bras")

      Son industriel/agressif (Nine Inch Nails-like):
        SensoryInput(audio_grave=0.8, audio_medium=0.5, audio_aigu=0.7,
                     audio_rugosite=0.9, audio_rythme=0.65, audio_dynamique=0.85)

      Substance GABAergique (alcool-like):
        SensoryInput(chem_gaba=+0.45, chem_nmda=-0.35, chem_da=+0.3,
                     chem_lipophile=0.7, chem_onset=0.25)

      Stimulant adénosine-bloquant (café-like):
        SensoryInput(chem_adenosine=-0.7, chem_ne=+0.3, chem_da=+0.2, chem_onset=0.6)

      Substance opioïde-like:
        SensoryInput(chem_opioid=+0.8, chem_gaba=+0.2, chem_lipophile=0.9,
                     chem_onset=0.5, meca_duration=1.0)

      Texte menaçant et émotionnellement chargé:
        SensoryInput(sem_valence=-0.7, sem_menace=0.75, sem_charge=0.85,
                     sem_arousal=0.65, sem_complexite=0.5)

      Texte intime et chaleureux:
        SensoryInput(sem_valence=0.7, sem_intimite=0.8, sem_social=0.7,
                     sem_charge=0.5, sem_arousal=0.35)
    """
    # ── Mécaniques (toucher, pression, impact, vibration) ──────────────────
    meca_force:    float = 0.0   # Force appliquée (0=aucune, 1=extrême)
    meca_vitesse:  float = 0.0   # Soudaineté (0=progressif, 1=brutal/soudain)
    meca_zone:     float = 0.5   # Surface de contact (0=ponctuel, 1=grande surface)
    meca_freq:     float = 0.0   # Vibration (0=statique, 1=haute vibration)
    meca_duration: float = 0.3   # Durée (0=instant, 1=prolongé)

    # ── Thermiques ──────────────────────────────────────────────────────────
    thermal:       float = 0.5   # Température (0=glace, 0.5=neutre, 1=brûlant)
    thermal_delta: float = 0.0   # Changement rapide (-1=refroidissement, +1=échauffement)

    # ── Auditives ───────────────────────────────────────────────────────────
    audio_grave:    float = 0.0  # Énergie basses fréquences
    audio_medium:   float = 0.0  # Énergie médiums
    audio_aigu:     float = 0.0  # Énergie hautes fréquences
    audio_rugosite: float = 0.0  # Distorsion/rugosité (0=pur/doux, 1=saturé/agressif)
    audio_rythme:   float = 0.0  # Régularité rythmique (0=aléatoire, 1=métronome)
    audio_dynamique:float = 0.0  # Plage dynamique (0=monotone, 1=très variable)
    audio_spatial:  float = 0.0  # Immersion spatiale (0=monophonie, 1=espace total)

    # ── Visuelles ───────────────────────────────────────────────────────────
    visual_lum:     float = 0.5  # Luminosité (0=noir, 1=éblouissant)
    visual_contraste:float= 0.0  # Contraste (0=plat, 1=très contrasté)
    visual_mouvement:float= 0.0  # Mouvement dans le champ (0=fixe, 1=chaotique)
    visual_chaleur: float = 0.5  # Teinte (0=bleu froid, 1=rouge chaud)
    visual_complexite:float= 0.0 # Complexité (0=minimaliste, 1=très dense)

    # ── Chimiques — PROFIL RÉCEPTEUR (sans nommer la substance) ─────────────
    # Valeurs: effet net sur le récepteur (-1 à +1)
    chem_gaba:      float = 0.0   # Modulation GABAergique (+ = plus inhibition)
    chem_nmda:      float = 0.0   # Modulation NMDA (+ = plus excitation)
    chem_da:        float = 0.0   # Effet dopaminergique
    chem_sero:      float = 0.0   # Effet sérotoninergique
    chem_ne:        float = 0.0   # Effet noradrénergique
    chem_opioid:    float = 0.0   # Activation système opioïde (0 à +1)
    chem_adenosine: float = 0.0   # Blocage adénosine (− = blocage → éveil)
    chem_lipophile: float = 0.0   # Liposolubilité / passage BHE (0-1)
    chem_onset:     float = 0.5   # Vitesse d'apparition (0=très lent, 1=immédiat)

    # ── Sémantiques / linguistiques ─────────────────────────────────────────
    sem_valence:    float = 0.0   # Valence du contenu (-1=négatif, +1=positif)
    sem_menace:     float = 0.0   # Contenu menaçant (0-1)
    sem_charge:     float = 0.0   # Charge émotionnelle globale (0-1)
    sem_arousal:    float = 0.0   # Contenu activant (0-1)
    sem_social:     float = 0.0   # Contenu social/relationnel (0-1)
    sem_complexite: float = 0.0   # Complexité cognitive requise (0-1)
    sem_intimite:   float = 0.0   # Degré d'intimité/proximité (0-1)

    # ── Intéroceptives (ce que le corps envoie déjà) ─────────────────────────
    intero_fc:      float = 0.0   # Variation fréquence cardiaque perçue
    intero_resp:    float = 0.0   # Variation respiration perçue
    intero_gut:     float = 0.0   # Sensation digestive
    intero_tension: float = 0.0   # Tension musculaire perçue

    # ── Méta ─────────────────────────────────────────────────────────────────
    location:    str   = "general"  # Zone: "visage","bras","torse","ventre","general"
    stimulus_id: str   = ""         # ID pour mémoire/conditionnement
    novelty:     float = 0.5        # Nouveauté (0=très connu, 1=totalement inconnu)
    onset:       float = 0.5        # Rapidité d'apparition du stimulus lui-même

    def has_mechanical(self) -> bool:
        return self.meca_force > 0.01 or self.meca_vitesse > 0.01

    def has_audio(self) -> bool:
        return (self.audio_grave+self.audio_medium+self.audio_aigu) > 0.05

    def has_chemical(self) -> bool:
        total = abs(self.chem_gaba)+abs(self.chem_nmda)+abs(self.chem_da)+abs(self.chem_sero)\
               +abs(self.chem_ne)+self.chem_opioid+abs(self.chem_adenosine)
        return total > 0.05

    def has_semantic(self) -> bool:
        return (self.sem_charge+abs(self.sem_valence)+self.sem_arousal) > 0.1

    def overall_intensity(self) -> float:
        meca  = self.meca_force * (1 + self.meca_vitesse)
        audio = max(self.audio_grave, self.audio_medium, self.audio_aigu) * (1 + self.audio_rugosite*.3)
        chem  = max(abs(self.chem_gaba), abs(self.chem_da), self.chem_opioid) * self.chem_lipophile
        sem   = self.sem_charge * (1 + abs(self.sem_valence)*.3)
        return min(1.0, max(meca*.5, audio*.6, chem*.7, sem*.5,
                            abs(self.thermal_delta)*.4))


# ─────────────────────────────────────────────────────────────────────────────
# §5  CORPS NUMÉRIQUE
#     Le corps reçoit la réalité, la traduit en signaux, réagit aux états
# ─────────────────────────────────────────────────────────────────────────────

class NociceptiveProcessor:
    """
    Système de douleur à deux voies:
    - A-delta: douleur rapide, vive, localisée (premier signal d'alarme)
    - C-fibres: douleur lente, brûlante, diffuse (souffrance persistante)
    Avec seuil adaptatif, sensibilisation et modulation opioïde.
    """
    def __init__(self):
        self.threshold_adelta  = 0.45   # Seuil activation A-delta
        self.threshold_c       = 0.30   # Seuil activation C-fibre
        self.sensitization     = 0.0    # Sensibilisation centrale (0=normal, 1=max)
        self.fast_pain         = 0.0    # Douleur rapide courante
        self.slow_pain         = 0.0    # Douleur lente courante
        self.cumulative_pain   = 0.0    # Douleur cumulée (wind-up)

    def process(self, stim: SensoryInput, nt: NeurotransmitterSystem) -> list[NeuralSignal]:
        signals = []
        # Calcul de l'input nociceptif brut
        meca_pain  = max(0, (stim.meca_force - 0.3) * (1 + stim.meca_vitesse * 0.5))
        therm_pain = max(0, abs(stim.thermal - 0.5) - 0.3) * 2 + max(0, abs(stim.thermal_delta) - 0.4) * 1.5
        raw = max(meca_pain, therm_pain)

        # Modulation descendante opioïde
        opioid_gate = nt.pain_modulation
        effective   = max(0.0, raw * (1.0 - opioid_gate * 0.6) * (1.0 + self.sensitization * 0.5))

        # Voie A-delta (rapide, vive): déclenche si > seuil adaptatif
        if effective > self.threshold_adelta:
            self.fast_pain = min(1.0, effective * 1.2)
            signals.append(NeuralSignal("nociception","brainstem","sensory",
                {"pain_fast": round(self.fast_pain,3), "location": stim.location,
                 "type":"sharp", "threat": self.fast_pain},
                strength=self.fast_pain, valence=-self.fast_pain, arousal=min(1.,self.fast_pain*1.2)))
            signals.append(NeuralSignal("nociception","cingulate_cortex","interoceptive",
                {"pain_affect": round(self.fast_pain,3), "type":"sharp"},
                strength=self.fast_pain * 0.8, valence=-self.fast_pain * 0.9))
        else:
            self.fast_pain = max(0.0, self.fast_pain - 0.15)

        # Voie C-fibre (lente, brûlante): seuil plus bas, persiste plus longtemps
        if effective > self.threshold_c:
            self.slow_pain = min(1.0, self.slow_pain * 0.6 + effective * 0.4)
            signals.append(NeuralSignal("nociception","insula","interoceptive",
                {"pain_slow": round(self.slow_pain,3), "location": stim.location,
                 "type":"burning", "body_arousal": self.slow_pain},
                strength=self.slow_pain * 0.7, valence=-self.slow_pain * 0.8, arousal=self.slow_pain * 0.6))
            # Wind-up: douleur cumulée → sensibilisation centrale
            self.cumulative_pain = min(1.0, self.cumulative_pain * 0.9 + effective * 0.1)
            self.sensitization   = min(0.8, self.sensitization + self.cumulative_pain * 0.01)
            # Libération d'endorphines sous douleur intense
            if self.slow_pain > 0.6:
                nt.modulate({"endorphins": self.slow_pain * 0.04, "cortisol": self.slow_pain * 0.02})
        else:
            self.slow_pain     = max(0.0, self.slow_pain - 0.08)
            self.cumulative_pain = max(0.0, self.cumulative_pain - 0.02)
            self.sensitization = max(0.0, self.sensitization - 0.001)

        return signals

    @property
    def total_pain(self) -> float:
        return max(self.fast_pain, self.slow_pain * 0.8)


class AutonomicNervousSystem:
    """
    Balance sympathique/parasympathique et métriques corporelles.
    Cerveau → ANS → Corps → Insula → Conscience corporelle
    """
    def __init__(self):
        self.balance        = 0.35  # 0=parasympa total, 1=sympa total (repos≈0.35)
        # Métriques corporelles normalisées 0-1
        self.heart_rate     = 0.50  # FC (0.3=bradycardie, 0.5=repos, 0.9=max effort)
        self.breathing_rate = 0.35  # Fréquence respiratoire
        self.muscle_tone    = 0.25  # Tonus musculaire
        self.skin_conduct   = 0.10  # Conductance cutanée (sueur)
        self.pupil_dilation = 0.45  # Dilatation pupillaire
        self.digestive_act  = 0.65  # Activité digestive (parasympa)
        self.body_temp      = 0.50  # Température périphérique

    def update_from_brain(self, amygdala_fear: float, pfc_inhibition: float,
                          nt: NeurotransmitterSystem) -> None:
        """
        Le cerveau pilote l'ANS. Balance basée sur les ÉCARTS au niveau de base.
        Au repos (NTs baseline, fear=0) → balance reste à 0.35.
        """
        # Drives sympathiques (écarts positifs par rapport au baseline)
        fear_drive = amygdala_fear * 0.7
        ne_drive   = max(0.0, nt.norepinephrine - 0.35) * 0.8
        cort_drive = max(0.0, nt.cortisol       - 0.25) * 0.5
        # Drives parasympathiques (écarts calmants)
        pfc_para   = pfc_inhibition * 0.5
        gaba_para  = max(0.0, nt.gaba     - 0.55) * 0.4
        sero_para  = max(0.0, nt.serotonin- 0.60) * 0.3
        oxt_para   = max(0.0, nt.oxytocin - 0.40) * 0.3  # ocytocine → parasympa

        delta = fear_drive + ne_drive + cort_drive - pfc_para - gaba_para - sero_para - oxt_para
        target_balance = min(1.0, max(0.0, 0.35 + delta))
        self.balance = self.balance * 0.85 + target_balance * 0.15

        # Métriques dérivées de la balance
        b = self.balance
        self.heart_rate     = 0.30 + b * 0.55
        self.breathing_rate = 0.20 + b * 0.55
        self.muscle_tone    = 0.10 + b * 0.75
        self.skin_conduct   = b ** 2 * 0.9
        self.pupil_dilation = 0.30 + b * 0.45
        self.digestive_act  = max(0.0, 0.80 - b * 0.65)
        self.body_temp      = 0.50 + (b - 0.5) * 0.15  # légère hausse si sympa

    def generate_interoceptive_signal(self) -> Optional[NeuralSignal]:
        """Génère un signal intéroceptif vers l'insula si la balance est perturbée."""
        deviation = abs(self.balance - 0.35)
        if deviation < 0.05:
            return None
        return NeuralSignal("ans","insula","interoceptive",{
            "heart_rate": round(self.heart_rate, 3),
            "breathing":  round(self.breathing_rate, 3),
            "muscle_tone":round(self.muscle_tone, 3),
            "skin_conduct":round(self.skin_conduct, 3),
            "pupil":      round(self.pupil_dilation, 3),
            "ans_balance":round(self.balance, 3),
            "body_arousal":round(self.balance, 3),
            "valence":    round(-(self.balance - 0.35) * 1.5, 3),
        }, strength=min(1.0, deviation * 2), valence=-(self.balance - 0.35) * 1.5,
           arousal=self.balance)

    def snapshot(self) -> dict:
        return {k: round(getattr(self, k), 3) for k in
                ["balance","heart_rate","breathing_rate","muscle_tone",
                 "skin_conduct","pupil_dilation","digestive_act","body_temp"]}


class ChemicalField:
    """
    Pharmacocinétique simplifiée:
    La substance est décrite par son profil récepteur (SensoryInput.chem_*).
    Elle monte avec la vitesse d'onset, puis décroit avec le temps.
    Effet proportionnel au niveau plasmatique × liposolubilité.
    """
    def __init__(self):
        self._active: dict[str, dict] = {}  # id → {profil, level, half_life}

    def apply(self, stim: SensoryInput, nt: NeurotransmitterSystem) -> None:
        if not stim.has_chemical():
            return
        sid = stim.stimulus_id or f"chem_{abs(hash(str(stim.chem_gaba)+str(stim.chem_da)))}"
        if sid not in self._active:
            # half_life plus long pour les substances à onset lent (persistent)
            hl = max(8, int(25 * (1.0 - stim.chem_onset * 0.5)))
            self._active[sid] = {
                "profil": {
                    "gaba":      stim.chem_gaba,   "nmda":  stim.chem_nmda,
                    "da":        stim.chem_da,     "sero":  stim.chem_sero,
                    "ne":        stim.chem_ne,     "opioid":stim.chem_opioid,
                    "adenosine": stim.chem_adenosine,
                },
                "lipophile": stim.chem_lipophile,
                "level":     0.0,
                "half_life": hl,
            }
        # Absorption: accumule au rythme de l'onset
        boost = min(0.5, stim.chem_onset * 0.55)
        self._active[sid]["level"] = min(1.0, self._active[sid]["level"] + boost)

    def tick(self, nt: NeurotransmitterSystem) -> None:
        """Applique les effets actifs (PK/PD) et fait décroître les niveaux."""
        to_remove = []
        for sid, chem in self._active.items():
            biophase = chem["level"] * chem["lipophile"]
            if biophase < 0.01:
                to_remove.append(sid)
                continue
            p = chem["profil"]
            scale = biophase * 0.03  # effet modéré par tick
            # Effet noradrénergique net (ne propre + adénosine-block → éveil)
            ne_effect = p["ne"] * scale + max(0, -p["adenosine"]) * scale * 0.8
            nt.modulate({
                "gaba":           p["gaba"]    * scale,
                "glutamate":      p["nmda"]    * scale,
                "dopamine":       p["da"]      * scale,
                "serotonin":      p["sero"]    * scale,
                "norepinephrine": ne_effect,
                "endorphins":     p["opioid"]  * scale * 1.5,
            })
            # Décroissance PK: fraction exponentielle (ln2/half_life)
            k = 0.693 / max(1, chem["half_life"])
            chem["level"] = max(0.0, chem["level"] * (1.0 - k))
        for s in to_remove:
            del self._active[s]

    def active_count(self) -> int:
        return len(self._active)


class BodySystem:
    """
    Corps numérique — ancrage physique du cerveau.
    Transforme les SensoryInput en signaux neuraux afférents,
    et reçoit les commandes efférentes du cerveau (ANS).
    """
    def __init__(self):
        self.nociception = NociceptiveProcessor()
        self.ans         = AutonomicNervousSystem()
        self.chemistry   = ChemicalField()
        # État corporel riche
        self.state = {
            "pain_fast":    0.0, "pain_slow":   0.0,
            "heart_rate":   0.5, "breathing":   0.35,
            "muscle_tone":  0.25,"skin_conduct": 0.1,
            "pupil":        0.45,"digestive":    0.65,
            "temperature":  0.5, "energy":       0.7,
            "balance":      0.35,
        }

    def process(self, stim: SensoryInput, nt: NeurotransmitterSystem) -> list[NeuralSignal]:
        """Transforme un SensoryInput en signaux neuraux afférents."""
        signals = []

        # 1. Nociception (douleur si dépassement de seuil)
        signals.extend(self.nociception.process(stim, nt))

        # 2. Voie sensorielle principale → thalamus
        sensory_content = self._build_sensory_content(stim)
        intensity = stim.overall_intensity()

        if intensity > 0.02:
            valence = self._compute_afferent_valence(stim)
            arousal_sig = min(1.0, intensity * (1 + stim.onset * 0.3))
            signals.append(NeuralSignal("body","brainstem","sensory",
                sensory_content, strength=intensity, valence=valence, arousal=arousal_sig))
            signals.append(NeuralSignal("body","thalamus","sensory",
                sensory_content, strength=intensity * 0.9, valence=valence, arousal=arousal_sig))

        # 3. Contenu sémantique → direct PFC + amygdale
        if stim.has_semantic():
            sem_str = (stim.sem_charge * 0.5 + abs(stim.sem_valence) * 0.3 + stim.sem_arousal * 0.2)
            signals.append(NeuralSignal("body","amygdala","sensory",
                {"threat": stim.sem_menace, "reward": max(0, stim.sem_valence * 0.7),
                 "valence": stim.sem_valence, "intimacy": stim.sem_intimite,
                 "social": stim.sem_social, "stimulus_id": stim.stimulus_id},
                strength=sem_str * 0.9, valence=stim.sem_valence, arousal=stim.sem_arousal))
            signals.append(NeuralSignal("body","prefrontal_cortex","sensory",
                {"semantic_valence": stim.sem_valence, "semantic_complexity": stim.sem_complexite,
                 "semantic_charge": stim.sem_charge, "novelty": stim.novelty,
                 "stimulus_id": stim.stimulus_id},
                strength=sem_str * 0.6, valence=stim.sem_valence, arousal=stim.sem_arousal))

        # 4. Substances chimiques
        if stim.has_chemical():
            self.chemistry.apply(stim, nt)

        # 5. Signal intéroceptif (corps informe le cerveau de son état interne)
        if stim.intero_fc > 0.05 or stim.intero_tension > 0.05:
            signals.append(NeuralSignal("body","insula","interoceptive",{
                "heart_rate": 0.5 + stim.intero_fc,
                "muscle_tension": stim.intero_tension,
                "gut_feeling": 0.5 + stim.intero_gut,
                "body_arousal": max(stim.intero_fc, stim.intero_tension),
                "valence": -stim.intero_tension * 0.5,
            }, strength=max(stim.intero_fc, stim.intero_tension) * 0.8))

        return signals

    def update_from_brain(self, amygdala_fear: float, pfc_inhibition: float,
                          nt: NeurotransmitterSystem) -> Optional[NeuralSignal]:
        """Reçoit les commandes du cerveau → met à jour l'état corporel."""
        self.chemistry.tick(nt)
        self.ans.update_from_brain(amygdala_fear, pfc_inhibition, nt)

        # Mise à jour de l'état corporel depuis l'ANS
        ans = self.ans.snapshot()
        self.state.update({
            "pain_fast":   round(self.nociception.fast_pain, 3),
            "pain_slow":   round(self.nociception.slow_pain, 3),
            "heart_rate":  ans["heart_rate"],
            "breathing":   ans["breathing_rate"],
            "muscle_tone": ans["muscle_tone"],
            "skin_conduct":ans["skin_conduct"],
            "pupil":       ans["pupil_dilation"],
            "digestive":   ans["digestive_act"],
            "temperature": ans["body_temp"],
            "balance":     ans["balance"],
            "energy":      max(0.1, min(1.0, self.state["energy"]
                               - pfc_inhibition * 0.002 + nt.endorphins * 0.001)),
        })
        return self.ans.generate_interoceptive_signal()

    def _build_sensory_content(self, s: SensoryInput) -> dict:
        c = {"novelty": s.novelty, "stimulus_id": s.stimulus_id, "location": s.location}
        if s.has_mechanical():
            c.update({"meca_force": s.meca_force, "meca_vitesse": s.meca_vitesse,
                      "pattern": f"meca_{s.location}"})
            # Un impact fort sans zone large = potentielle menace
            if s.meca_force > 0.4 and s.meca_zone < 0.4:
                c["threat"] = s.meca_force * s.meca_vitesse
        if s.has_audio():
            energy = (s.audio_grave + s.audio_medium + s.audio_aigu) / 3
            c.update({"audio_energy": energy, "audio_rugosite": s.audio_rugosite,
                      "pattern": f"audio_{int(s.audio_rugosite*3)}"})
        if s.visual_contraste > 0.1 or s.visual_mouvement > 0.1:
            c.update({"visual_stim": (s.visual_contraste + s.visual_mouvement) / 2,
                      "pattern": "visual"})
        if abs(s.thermal_delta) > 0.3 or abs(s.thermal - 0.5) > 0.3:
            c.update({"thermal_val": s.thermal, "thermal_delta": s.thermal_delta})
        return c

    def _compute_afferent_valence(self, s: SensoryInput) -> float:
        """Valence afférente avant traitement cérébral."""
        neg = s.meca_force * s.meca_vitesse * 0.5  # impact soudain = négatif
        neg += max(0, abs(s.thermal - 0.5) - 0.3) * 0.6  # extrêmes thermiques
        neg += s.audio_rugosite * 0.2                     # son agressif
        pos = max(0, s.thermal - 0.5) * 0.3               # chaleur douce
        pos += (1 - s.meca_zone) * s.meca_force * 0.0    # zone large = moins douloureux
        pos += s.audio_spatial * s.audio_rythme * 0.1    # son spatial/rythmé
        return max(-1.0, min(1.0, pos - neg))


# ─────────────────────────────────────────────────────────────────────────────
# §6  LES 11 RÉGIONS CÉRÉBRALES (condensées, logique inchangée)
# ─────────────────────────────────────────────────────────────────────────────

class Brainstem(BrainRegion):
    def __init__(self):
        super().__init__("brainstem",20); self.arousal_drive=0.4; self._vt=0
    def _process_signals(self,signals,nt):
        self._vt+=1; threat=arousal=0.0
        for s in signals:
            if s.signal_type=="sensory":
                threat=max(threat,s.content.get("threat",0)*s.strength)
                arousal=max(arousal,s.strength*s.content.get("novelty",0.3))
        self.arousal_drive=min(1.0,max(0.1,self.arousal_drive*.8+arousal*.2+nt.norepinephrine*.1))
        self._emit(self._make("thalamus","arousal",
            {"arousal_drive":self.arousal_drive},
            strength=max(0.1,min(1.,self.arousal_drive+nt.norepinephrine*.3-nt.gaba*.2)),
            arousal=self.arousal_drive))
        if threat>0.4:
            self._emit(self._make("amygdala","sensory",
                {"threat":threat,"source":"brainstem_rapid"},
                strength=threat,valence=-threat,arousal=min(1.,threat*1.2)))
            nt.modulate({"norepinephrine":threat*.3,"cortisol":0.05})
        if math.sin(self._vt*.1)<-0.05: nt.modulate({"gaba":0.01,"norepinephrine":-0.01})


class Thalamus(BrainRegion):
    def __init__(self):
        super().__init__("thalamus",30); self.attention_gate=0.5
    def _process_signals(self,signals,nt):
        ai=exec_d=0.0; sens=[]
        for s in signals:
            if s.signal_type=="arousal": ai=max(ai,s.strength)
            elif s.signal_type=="sensory": sens.append(s)
            elif s.signal_type=="executive": exec_d=max(exec_d,s.content.get("attention_direction",0.5))
        td=exec_d if exec_d>0 else self.attention_gate
        self.attention_gate=min(1.,max(.1,ai*.3+td*.3+nt.acetylcholine*.2+nt.norepinephrine*.1-nt.gaba*.2))
        for s in sens:
            rs=s.strength*self.attention_gate
            if rs>0.05:
                self._emit(NeuralSignal("thalamus","sensory_cortex","sensory",s.content,rs,s.valence,s.arousal*self.attention_gate))
            if s.content.get("threat",0)>0.2 or s.valence<-0.3:
                self._emit(NeuralSignal("thalamus","amygdala","sensory",s.content,s.strength*.8,s.valence,s.arousal))
        self._emit(self._make("prefrontal_cortex","arousal",
            {"attention_gate":self.attention_gate,"arousal":ai},strength=self.attention_gate,arousal=ai))


class Amygdala(BrainRegion):
    def __init__(self):
        super().__init__("amygdala",20)
        self.fear_level=0.0; self.reward_signal=0.0
        self.emotional_valence=0.0; self.emotional_arousal=0.0
        self._cond:dict[str,float]={}
    def _process_signals(self,signals,nt):
        mt=mr=tv=ta=0.0; n=max(1,len(signals))
        for s in signals:
            t=s.content.get("threat",0.); r=s.content.get("reward",0.)
            sid=s.content.get("stimulus_id","")
            if sid in self._cond:
                c=self._cond[sid]; t=max(t,-c if c<0 else 0); r=max(r,c if c>0 else 0)
            mt=max(mt,t*s.strength); mr=max(mr,r*s.strength)
            tv+=s.valence*s.strength; ta+=s.arousal*s.strength
        av=tv/n; aa=ta/n
        dv=0.5 if abs(av)>0.5 else 0.65; da=0.5 if aa>0.6 else 0.65
        self.fear_level=self.fear_level*.6+mt*.4
        self.reward_signal=self.reward_signal*.6+mr*.4
        cv=av*.6+self.reward_signal*.25-self.fear_level*.15
        self.emotional_valence=self.emotional_valence*dv+cv*(1-dv)
        self.emotional_arousal=self.emotional_arousal*da+aa*(1-da)
        if self.fear_level>0.3: nt.modulate({"norepinephrine":self.fear_level*.1,"cortisol":self.fear_level*.05,"gaba":-self.fear_level*.03})
        if self.reward_signal>0.3: nt.modulate({"dopamine":self.reward_signal*.1,"endorphins":self.reward_signal*.05})
        intensity=max(abs(self.emotional_valence),self.fear_level,self.reward_signal)
        if intensity>0.1:
            self._emit(self._make("prefrontal_cortex","emotional",
                {"fear":round(self.fear_level,3),"reward":round(self.reward_signal,3),
                 "valence":round(self.emotional_valence,3),"arousal":round(self.emotional_arousal,3)},
                strength=intensity,valence=self.emotional_valence,arousal=self.emotional_arousal))
            self._emit(self._make("hippocampus","emotional",
                {"emotional_tag":round(intensity,3),"valence":round(self.emotional_valence,3)},
                strength=intensity*.8,valence=self.emotional_valence,arousal=self.emotional_arousal))
            if self.emotional_arousal>0.4:
                self._emit(self._make("insula","emotional",
                    {"body_arousal":self.emotional_arousal,"valence":self.emotional_valence},
                    strength=self.emotional_arousal*.7,arousal=self.emotional_arousal))
    def condition(self,sid,val):
        self._cond[sid]=self._cond.get(sid,0.0)*.7+val*.3
    def get_state(self):
        s=super().get_state(); s.update({"fear":round(self.fear_level,3),"reward":round(self.reward_signal,3),
            "valence":round(self.emotional_valence,3),"e_arousal":round(self.emotional_arousal,3)}); return s


@dataclass
class MemoryTrace:
    episode_id:int; content:dict; emotional_tag:float; valence:float
    encoded_at:float=field(default_factory=time.time); strength:float=1.0
    consolidated:bool=False; retrieval_count:int=0
    def decay(self,rate=0.001):
        if not self.consolidated: self.strength=max(0.,self.strength-rate*(1-self.emotional_tag*.5))
    def reinforce(self,amt=0.1): self.strength=min(1.,self.strength+amt); self.retrieval_count+=1


class Hippocampus(BrainRegion):
    def __init__(self):
        super().__init__("hippocampus",20); self._ec=0; self._traces:list[MemoryTrace]=[]; self.cur_etag=0.0
    def _process_signals(self,signals,nt):
        cue=None; nc={}; et=self.cur_etag
        for s in signals:
            if s.signal_type=="emotional": et=max(et,s.content.get("emotional_tag",0)); self.cur_etag=et*.8
            elif s.signal_type=="sensory":
                nc.update(s.content)
                if abs(s.valence)>0.3 or s.arousal>0.6: et=max(et,(abs(s.valence)*.6+s.arousal*.4)*s.strength)
            elif s.signal_type=="executive" and s.content.get("retrieve"): cue=s.content["retrieve"]
        if nc:
            eff=nt.memory_encoding_efficiency*max(0.2,1.-nt.cortisol*.5)
            if eff>0.2:
                self._ec+=1
                self._traces.append(MemoryTrace(self._ec,nc.copy(),et,
                    sum(s.valence for s in signals)/max(1,len(signals)),strength=eff))
                self._emit(self._make("prefrontal_cortex","mnemonic",
                    {"episode_id":self._ec,"encoded":True,"strength":round(eff,3),"emotional_tag":round(et,3)},
                    strength=eff*.7))
        if cue:
            r=self._retrieve(cue)
            if r: self._emit(self._make("prefrontal_cortex","mnemonic",
                {"retrieved":True,"cue":cue,"memory":r.content,"emotional_tag":r.emotional_tag,"valence":r.valence},
                strength=r.strength,valence=r.valence))
        for t in self._traces: t.decay()
        self._traces=[t for t in self._traces if t.strength>0.01]
    def _retrieve(self,cue):
        if not self._traces: return None
        cands=[t for t in self._traces if isinstance(cue,str) and any(cue in str(v) for v in t.content.values())] or self._traces
        if not cands: return None
        best=max(cands,key=lambda t:t.strength*(1+t.emotional_tag)); best.reinforce(); return best
    def get_state(self):
        s=super().get_state(); s.update({"memory_traces":len(self._traces),"total_episodes":self._ec}); return s


class WorkingMemory:
    CAPACITY=7
    def __init__(self): self._s:deque=deque(maxlen=self.CAPACITY)
    def add(self,item,priority=0.5): self._s.append({"item":item,"priority":priority})
    def get_focus(self): return max(self._s,key=lambda s:s["priority"])["item"] if self._s else None
    def clear_low(self,t=0.2): self._s=deque([s for s in self._s if s["priority"]>t],maxlen=self.CAPACITY)
    @property
    def load(self): return len(self._s)/self.CAPACITY


class PrefrontalCortex(BrainRegion):
    def __init__(self):
        super().__init__("prefrontal_cortex",30); self._fatigue_managed=True
        self.wm=WorkingMemory(); self.emotional_state={"fear":0.,"reward":0.,"valence":0.}
        self.inhibition_signal=0.; self.cognitive_load=0.; self.prediction_error=0.
        self._expected:dict={}
    def _process_signals(self,signals,nt):
        sens=[s for s in signals if s.signal_type=="sensory"]
        emos=[s for s in signals if s.signal_type=="emotional"]
        mnems=[s for s in signals if s.signal_type=="mnemonic"]
        if emos: self.emotional_state=emos[-1].content
        for s in sens: self.wm.add(s.content,priority=s.strength*(1+abs(s.valence)*.5))
        for s in mnems:
            if s.content.get("retrieved"): self.wm.add(s.content,priority=0.8)
        self.cognitive_load=self.wm.load*.6+self.fatigue*.3+nt.cortisol*.1
        has_ext=any(s.signal_type in("sensory","emotional") for s in signals)
        if has_ext and self.cognitive_load>0.05: self.fatigue=min(1.,self.fatigue+self.cognitive_load*.15)
        elif not has_ext: self.fatigue=max(0.,self.fatigue-.03)
        if sens and self._expected:
            errs=[abs(float(self._expected.get(k,0))-float(sens[0].content.get(k,0)))
                  for k in set(self._expected)|set(sens[0].content)
                  if isinstance(self._expected.get(k,0),(int,float)) and isinstance(sens[0].content.get(k,0),(int,float))]
            self.prediction_error=min(1.,sum(errs)/max(1,len(errs))) if errs else self.prediction_error*.9
        else: self.prediction_error*=.9
        fear=self.emotional_state.get("fear",0.); self.inhibition_signal=fear*nt.serotonin
        self._emit(self._make("thalamus","executive",
            {"attention_direction":min(1.,max(.1,.5+self.prediction_error*.3-self.cognitive_load*.2))},
            strength=max(.2,1.-self.cognitive_load),arousal=nt.arousal_level))
        foc=self.wm.get_focus()
        if foc and self.prediction_error>0.4:
            self._emit(self._make("hippocampus","executive",
                {"retrieve":list(foc.keys())[0] if foc else None},strength=.6))
        if self.cognitive_load<0.9:
            dec=self._decide(nt)
            if dec: self._emit(self._make("basal_ganglia","executive",dec,
                strength=max(.3,nt.motivation),valence=self.emotional_state.get("valence",0.)))
        if abs(self.emotional_state.get("valence",0.))>0.3:
            self._emit(self._make("insula","interoceptive",{"monitored_state":self.emotional_state},strength=.5))
        self.wm.clear_low()
        if sens: self._expected=sens[-1].content.copy()
    def _decide(self,nt):
        foc=self.wm.get_focus()
        if not foc: return None
        fear=self.emotional_state.get("fear",0.); reward=self.emotional_state.get("reward",0.); valence=self.emotional_state.get("valence",0.)
        if fear>0.4 and nt.serotonin<0.5: action,conf="avoid",fear
        elif reward>0.25 and nt.dopamine>0.4: action,conf="approach",reward*nt.motivation
        elif self.prediction_error>0.35: action,conf="explore",self.prediction_error*.6
        elif valence>0.2: action,conf="engage",valence*.7
        else: action,conf="maintain",0.3
        return {"action":action,"confidence":round(conf,3),"cognitive_load":round(self.cognitive_load,3)}
    def get_state(self):
        s=super().get_state(); s.update({"cognitive_load":round(self.cognitive_load,3),
            "prediction_error":round(self.prediction_error,3),"emotional_state":self.emotional_state}); return s


class BasalGanglia(BrainRegion):
    def __init__(self):
        super().__init__("basal_ganglia",15)
        self._av={k:0.5 for k in ["approach","avoid","explore","engage","maintain","rest"]}
        self._last:Optional[str]=None; self._lval=0.5; self.selected_action:Optional[str]=None
        self.habit:dict[str,float]={}
    def _process_signals(self,signals,nt):
        execs=[s for s in signals if s.signal_type=="executive"]
        rwds =[s for s in signals if s.signal_type=="reward"]
        for s in rwds:
            if self._last:
                td=s.content.get("reward_received",0.)-self._lval; lr=nt.dopamine*.1
                self._av[self._last]=min(1.,max(0.,self._av[self._last]+lr*td))
                if td>0.2: nt.modulate({"dopamine":td*.1})
                elif td<-0.2: nt.modulate({"dopamine":td*.05})
        if not execs: return
        last=execs[-1]; sugg=last.content.get("action","maintain"); conf=last.content.get("confidence",.5)
        scores={a:(self._av[a]*.5+(conf*.4 if a==sugg else 0)+self.habit.get(a,0.)*.3*nt.dopamine)*max(.2,nt.motivation) for a in self._av}
        sel=max(scores,key=scores.get)
        self.selected_action=sel; self._last=sel; self._lval=self._av.get(sel,.5)
        self.habit[sel]=min(1.,self.habit.get(sel,0.)+.01)
        for a in self.habit:
            if a!=sel: self.habit[a]=max(0.,self.habit[a]-.005)
        self._emit(self._make("cerebellum","motor",
            {"action":sel,"score":round(scores[sel],3),"habit":round(self.habit.get(sel,0.),3)},
            strength=scores[sel],valence=last.valence))
    def get_state(self):
        s=super().get_state(); s.update({"selected_action":self.selected_action,
            "action_values":{k:round(v,3) for k,v in self._av.items()}}); return s


class Cerebellum(BrainRegion):
    def __init__(self):
        super().__init__("cerebellum",15); self._model:dict[str,float]={}
        self.timing=0.7; self.pred_err=0.0; self.proc_mem:dict[str,float]={}
    def _process_signals(self,signals,nt):
        for s in [s for s in signals if s.signal_type=="motor"]:
            a=s.content.get("action","maintain"); pred=self._model.get(a,.5)
            r=s.content.get("score",.5); proc=self.proc_mem.get(a,0.)
            self.proc_mem[a]=min(1.,proc+.005); t=self.timing*(1.-self.fatigue*.3)
            self._emit(self._make("output","motor",
                {"action":a,"refined_score":round(r*t,3),"predicted":round(pred,3),"procedural":round(proc,3)},
                strength=r*t,valence=s.valence))
            sfb=[s for s in signals if s.signal_type=="sensory"]
            if sfb:
                act=sfb[-1].strength; self.pred_err=abs(pred-act)
                self._model[a]=pred+.05*(act-pred)
                if self.pred_err>0.3:
                    self._emit(self._make("prefrontal_cortex","predictive",
                        {"action":a,"prediction_error":round(self.pred_err,3)},strength=self.pred_err))


class Insula(BrainRegion):
    def __init__(self):
        super().__init__("insula",15)
        self.body_state={"heart_rate":.5,"muscle_tension":.3,"gut_feeling":.5,"energy":.7,"pain":.0}
        self.felt_emotion:dict={}; self.empathy=0.0
    def _process_signals(self,signals,nt):
        for s in signals:
            if s.signal_type=="emotional":
                ar=s.content.get("body_arousal",s.arousal); vl=s.content.get("valence",s.valence)
                self.body_state["heart_rate"]=min(1.,self.body_state["heart_rate"]*.7+ar*.3)
                self.body_state["muscle_tension"]=min(1.,self.body_state["muscle_tension"]*.8+max(0,-vl)*ar*.3)
                self.body_state["gut_feeling"]=min(1.,max(0.,.5+vl*.3+(nt.serotonin-.5)*.2))
                self.felt_emotion={"valence":round(vl,3),"arousal":round(ar,3),
                    "body_tension":round(self.body_state["muscle_tension"],3),
                    "gut_feeling":round(self.body_state["gut_feeling"],3),
                    "subjective_intensity":round((abs(vl)+ar+self.body_state["heart_rate"])/3,3)}
            elif s.signal_type=="interoceptive":
                # Mise à jour depuis l'ANS ou le corps
                bd=s.content
                if "heart_rate" in bd: self.body_state["heart_rate"]=bd["heart_rate"]
                if "muscle_tension" in bd: self.body_state["muscle_tension"]=bd["muscle_tension"]
                if "gut_feeling" in bd: self.body_state["gut_feeling"]=bd["gut_feeling"]
                if "pain_slow" in bd: self.body_state["pain"]=bd.get("pain_slow",0.)
                fe=s.content.get("felt_emotion",{})
                if fe: self.felt_emotion.update(fe)
                ms=s.content.get("monitored_state",{})
                if ms: self.empathy=abs(ms.get("valence",0.))*.5
        self.body_state["energy"]=max(.1,min(1.,self.body_state["energy"]-self.fatigue*.01+nt.dopamine*.005))
        si=self.felt_emotion.get("subjective_intensity",0.)
        if si>0.15 or self.body_state["pain"]>0.1:
            self._emit(self._make("cingulate_cortex","interoceptive",
                {"felt_emotion":self.felt_emotion,"body_state":{k:round(v,3) for k,v in self.body_state.items()}},
                strength=max(si,self.body_state["pain"]),
                valence=self.felt_emotion.get("valence",0.),arousal=self.felt_emotion.get("arousal",.5)))
    def get_state(self):
        s=super().get_state(); s.update({"body_state":{k:round(v,3) for k,v in self.body_state.items()},"felt_emotion":self.felt_emotion}); return s


class CingulateCortex(BrainRegion):
    def __init__(self):
        super().__init__("cingulate_cortex",15); self.conflict=0.; self.error=0.; self.distress=0.
    def _process_signals(self,signals,nt):
        intero=[s for s in signals if s.signal_type=="interoceptive"]
        pred  =[s for s in signals if s.signal_type=="predictive"]
        vals=[s.valence for s in signals if s.valence!=0]
        if len(vals)>=2:
            mx,mn=max(vals),min(vals)
            self.conflict=min(1.,(mx-mn)/2) if mx>0.3 and mn<-0.3 else self.conflict*.8
        else: self.conflict*=.8
        for s in pred: self.error=max(self.error*.7,s.content.get("prediction_error",0.))
        for s in intero:
            fe=s.content.get("felt_emotion",{}); neg=max(0,-fe.get("valence",0.))
            si=fe.get("subjective_intensity",0.); pain=s.content.get("body_state",{}).get("pain",0.)
            self.distress=min(1.,self.distress*.7+(neg*.3+self.conflict*.2+si*.2+pain*.3))
        if self.distress>0.4: nt.modulate({"cortisol":self.distress*.02})
        if self.error>0.5: nt.modulate({"norepinephrine":self.error*.05})
        alarm=max(self.conflict,self.error,self.distress)
        if alarm>0.2:
            self._emit(self._make("prefrontal_cortex","executive",
                {"conflict":round(self.conflict,3),"error":round(self.error,3),
                 "distress":round(self.distress,3),"alarm":round(alarm,3)},
                strength=alarm,valence=-self.distress,arousal=min(1.,alarm*1.2)))
    def get_state(self):
        s=super().get_state(); s.update({"conflict":round(self.conflict,3),"distress":round(self.distress,3)}); return s


class SensoryCortex(BrainRegion):
    def __init__(self):
        super().__init__("sensory_cortex",20); self._rec:dict[str,float]={}
    def _process_signals(self,signals,nt):
        for s in [x for x in signals if x.signal_type=="sensory"]:
            pat=s.content.get("pattern","")
            if pat: self._rec[pat]=min(1.,self._rec.get(pat,0.)+.05); rec=self._rec[pat]>0.2
            else: rec=False; rec_str=0.
            ps=s.strength*(nt.acetylcholine*.3+.7)
            self._emit(NeuralSignal("sensory_cortex","hippocampus","sensory",
                {**s.content,"recognized":rec},ps*.7,s.valence,s.arousal))
            self._emit(NeuralSignal("sensory_cortex","prefrontal_cortex","sensory",
                {**s.content,"recognized":rec,"novelty":s.content.get("novelty",.3)},ps*.6,s.valence,s.arousal))
            if abs(s.valence)>0.3 or s.content.get("threat",0)>0.2:
                self._emit(NeuralSignal("sensory_cortex","amygdala","sensory",s.content,ps*.5,s.valence,s.arousal))


class DefaultModeNetwork(BrainRegion):
    def __init__(self):
        super().__init__("default_mode_network",10)
        self.self_model={"identity_coherence":.7,"narrative_strength":.5,"rumination_tendency":.3}
        self.mind_wandering=False; self.creative_assoc:list=[]
        self.current_thought_type:str=""; self.thought_valence:float=0.
    def _process_signals(self,signals,nt):
        ext=sum(s.strength for s in signals if s.signal_type in("sensory","executive"))
        da=max(0.,.7-ext*.8)*max(.2,1.-nt.norepinephrine*.5)
        self.activation=self.activation*.6+da*.4
        if self.activation<0.2: self.mind_wandering=False; return
        self.mind_wandering=True
        if nt.stress_level>0.6 and nt.serotonin<0.4:
            tt="rumination"; tv=-0.5
            self.self_model["rumination_tendency"]=min(1.,self.self_model["rumination_tendency"]+.02)
            nt.modulate({"serotonin":-.01,"cortisol":.01})
        elif nt.mood_valence>0.3 and nt.dopamine>0.5:
            tt="creative_daydream"; tv=0.4; self._gen_creative(); nt.modulate({"dopamine":.005})
        elif nt.serotonin>0.6:
            tt="self_narrative"; tv=0.2
            self.self_model["narrative_strength"]=min(1.,self.self_model["narrative_strength"]+.01)
        else:
            tt="mind_wandering"; tv=0.0
        self.current_thought_type=tt; self.thought_valence=tv
        if self.activation>0.4:
            self._emit(self._make("prefrontal_cortex","internal",
                {"thought_type":tt,"dmn_activation":round(self.activation,3),
                 "self_model":self.self_model.copy(),"mind_wandering":self.mind_wandering},
                strength=self.activation*.5,valence=tv,arousal=self.activation*.3))
    def _gen_creative(self):
        cs=["mémoire","émotion","futur","soi","autre","motif","structure","flux","émergence","lien"]
        if len(cs)>=2:
            a=random.choice(cs); b=random.choice([c for c in cs if c!=a])
            self.creative_assoc.append((a,b,round(random.uniform(.3,1.),2)))
            if len(self.creative_assoc)>20: self.creative_assoc.pop(0)
    def get_state(self):
        s=super().get_state(); s.update({"mind_wandering":self.mind_wandering,
            "thought_type":self.current_thought_type,"self_model":{k:round(v,3) for k,v in self.self_model.items()}}); return s


# ─────────────────────────────────────────────────────────────────────────────
# §7  ÉLANS SPONTANÉS & INTROSPECTION
# ─────────────────────────────────────────────────────────────────────────────

class ImpulseEngine:
    """
    Génère des élans internes sans stimulus extérieur.
    Le cerveau n'est jamais passif — il anticipe, désire, s'ennuie, crée.
    Types: curiosité, social, créatif, repos, mémoire, mélancolie, dérive
    """
    TYPES = {
        "curiosity":     (+0.35, "explorer, comprendre"),
        "social":        (+0.30, "connecter, partager"),
        "creative":      (+0.45, "créer, exprimer"),
        "rest":          (+0.10, "s'arrêter, récupérer"),
        "memory_replay": ( 0.00, "remémorer"),
        "melancholy":    (-0.25, "ressentir la perte"),
        "anticipation":  (+0.20, "anticiper, se préparer"),
        "drift":         ( 0.00, "dériver librement"),
    }

    def __init__(self):
        self.current_impulse:Optional[str]=None; self.impulse_strength=0.
        self._drives={"rest":0.,"social":.3,"curiosity":.4,"creative":.2,"anticipation":.1}
        self._last_impulse_tick=0

    def tick(self, nt:NeurotransmitterSystem, pfc:PrefrontalCortex,
             hippocampus:Hippocampus, tick:int) -> Optional[NeuralSignal]:
        # Mise à jour des drives homéostatiques
        self._drives["rest"]      = min(1., pfc.fatigue*.8 + max(0,nt.cortisol-.4)*.3)
        self._drives["social"]    = min(1., self._drives["social"]*.99 + max(0,.5-nt.oxytocin)*.02)
        self._drives["curiosity"] = min(1., max(0,nt.dopamine-.3)*.4 + pfc.prediction_error*.3)
        self._drives["creative"]  = min(1., max(0,nt.dopamine-.4)*.3 + max(0,nt.serotonin-.5)*.2)
        self._drives["anticipation"]=min(1., pfc.prediction_error*.5)

        # Bruit de fond stochastique (simplifie 1/f)
        noise=(random.random()**1.8)*(nt.arousal_level*.4+.15)

        strongest=max(self._drives,key=self._drives.get)
        drive_val=self._drives[strongest]
        threshold=0.5-nt.arousal_level*.1

        if (noise>0.75 or drive_val>threshold) and (tick-self._last_impulse_tick)>3:
            if drive_val>0.6:
                itype=strongest
            elif noise>0.82 and hippocampus._traces:
                itype="memory_replay"
            elif nt.serotonin<0.35 and nt.arousal_level<0.4:
                itype="melancholy"
            elif noise>0.78:
                itype="drift"
            else:
                itype=strongest

            self.current_impulse=itype
            self.impulse_strength=min(1.,drive_val*.7+noise*.3)
            self._last_impulse_tick=tick
            val=self.TYPES.get(itype,(0.,""))[0]
            return NeuralSignal("impulse_engine","default_mode_network","internal",
                {"impulse_type":itype,"drives":{k:round(v,3) for k,v in self._drives.items()},
                 "impulse_meaning":self.TYPES.get(itype,("",""))[1]},
                strength=self.impulse_strength,valence=val,arousal=self.impulse_strength*.5)

        # Décroissance naturelle
        self.current_impulse=None; self.impulse_strength=0.
        return None

    def get_state(self) -> dict:
        return {"impulse":self.current_impulse,"strength":round(self.impulse_strength,3),
                "drives":{k:round(v,3) for k,v in self._drives.items()}}


class IntrospectionEngine:
    """
    Le cerveau s'examine lui-même: que ressens-je? pourquoi?
    Génère un rapport de méta-conscience et des questions ouvertes.
    Active toutes les N ticks, surtout au repos (PFC peu chargé).
    """
    def __init__(self):
        self.last_tick=0; self.interval=10
        self.self_report:dict={}; self.meta_questions:list=[]
        self.self_coherence=0.7   # sentiment de cohérence interne

    def tick(self, amygdala:Amygdala, insula:Insula, pfc:PrefrontalCortex,
             hippocampus:Hippocampus, nt:NeurotransmitterSystem, tick:int) -> Optional[dict]:
        # S'active surtout quand le PFC est peu chargé
        adj_interval = max(5, self.interval - int(pfc.fatigue * 5))
        if tick - self.last_tick < adj_interval:
            return None
        self.last_tick = tick

        # Ce que je ressens physiquement
        bst = insula.body_state
        phys = {"tension": round(bst.get("muscle_tension", 0), 3),
                "gut_sense": round(bst.get("gut_feeling", 0.5), 3),
                "energy": round(bst.get("energy", 0.5), 3),
                "pain": round(bst.get("pain", 0.0), 3),
                "heart_rate": round(bst.get("heart_rate", 0.5), 3)}

        # Ce que je ressens émotionnellement
        emo = {"valence":  round(amygdala.emotional_valence, 3),
               "fear":     round(amygdala.fear_level, 3),
               "desire":   round(amygdala.reward_signal, 3),
               "mood":     round(nt.mood_valence, 3)}

        # Ce qui est en mémoire de travail
        foc = pfc.wm.get_focus()
        wm_summary = list(foc.keys())[:3] if foc else []

        # Souvenir émotionnellement saillant
        sal_mem = None
        if hippocampus._traces:
            best = max(hippocampus._traces, key=lambda t: t.emotional_tag*t.strength)
            if best.emotional_tag > 0.3:
                sal_mem = {"episode_id": best.episode_id, "emotional_tag": round(best.emotional_tag,3),
                           "valence": round(best.valence, 3)}

        # Cohérence interne (peur+désir simultanés = incoherence)
        incoherence = abs(amygdala.fear_level - amygdala.reward_signal) * min(amygdala.fear_level, amygdala.reward_signal) * 2
        self.self_coherence = max(0.2, min(1.0, self.self_coherence - incoherence*.1 + .02))

        self.self_report = {
            "physical_sense": phys,
            "emotional_sense": emo,
            "working_memory": wm_summary,
            "salient_memory": sal_mem,
            "stress": round(nt.stress_level, 3),
            "motivation": round(nt.motivation, 3),
            "coherence": round(self.self_coherence, 3),
        }

        # Méta-questions émergentes (l'esprit se demande)
        self.meta_questions = []
        if nt.stress_level > 0.5:
            self.meta_questions.append("qu'est-ce qui génère cette tension?")
        if amygdala.fear_level > 0.3 and not foc:
            self.meta_questions.append("pourquoi cette inquiétude sans objet précis?")
        if nt.mood_valence < -0.3 and nt.arousal_level < 0.4:
            self.meta_questions.append("qu'est-ce qui manque?")
        if sal_mem:
            self.meta_questions.append("ce souvenir est-il lié à l'instant?")
        if nt.dopamine > 0.65 and not amygdala.reward_signal > 0.3:
            self.meta_questions.append("vers quoi ce désir se dirige-t-il?")

        return self.self_report

    def get_state(self) -> dict:
        return {"self_report": self.self_report, "meta_questions": self.meta_questions,
                "self_coherence": round(self.self_coherence, 3)}


# ─────────────────────────────────────────────────────────────────────────────
# §8  MATRICE ÉMOTIONNELLE — TOP 3 + HUMEUR DE FOND
# ─────────────────────────────────────────────────────────────────────────────

EMOTION_MAP = [
    ( 0.5, 1.0, 0.65,1.0,  "joy",          "joie / euphorie"),
    ( 0.25,0.7, 0.55,0.9,  "excitement",   "excitation"),
    ( 0.15,0.55,0.45,0.75, "interest",     "intérêt / curiosité"),
    ( 0.3, 0.8, 0.35,0.7,  "enthusiasm",   "enthousiasme"),
    ( 0.3, 0.7, 0.25,0.55, "pleasure",     "plaisir"),
    ( 0.2, 0.6, 0.15,0.45, "satisfaction", "satisfaction"),
    ( 0.35,1.0, 0.0, 0.35, "contentment",  "contentement"),
    ( 0.1, 0.45,0.0, 0.25, "calm",         "calme"),
    ( 0.45,1.0, 0.15,0.5,  "happiness",    "bonheur"),
    (-1.0,-0.45,0.6, 1.0,  "fear",         "peur"),
    (-0.7,-0.25,0.5, 0.9,  "anger",        "colère"),
    (-0.5,-0.15,0.45,0.8,  "anxiety",      "anxiété"),
    (-0.8,-0.35,0.7, 1.0,  "panic",        "panique"),
    (-0.6,-0.2, 0.35,0.65, "unease",       "malaise"),
    (-1.0,-0.35,0.0, 0.45, "sadness",      "tristesse"),
    (-0.5,-0.05,0.05,0.35, "boredom",      "ennui"),
    (-0.6,-0.15,0.0, 0.2,  "depression",   "abattement"),
    (-0.4,-0.1, 0.15,0.45, "melancholy",   "mélancolie"),
    (-0.3, 0.3, 0.15,0.55, "neutral",      "neutre"),
    (-0.15,0.35,0.35,0.65, "alert",        "alerte"),
    (-0.2, 0.2, 0.55,0.85, "aroused",      "éveillé"),
    (-0.3, 0.15,0.0, 0.2,  "tired",        "fatigué"),
    ( 0.0, 0.4, 0.0, 0.5,  "serene",       "serein"),
    (-0.2, 0.3, 0.2, 0.5,  "pensive",      "songeur"),
]

def get_emotion_matrix(valence:float, arousal:float, n:int=3) -> list[dict]:
    """
    Retourne les N émotions dominantes avec leur poids (softmax sur proximité inverse).
    Modèle le fait que plusieurs émotions coexistent simultanément.
    """
    scored = []
    for mn_v,mx_v,mn_a,mx_a,lbl,lbl_fr in EMOTION_MAP:
        cv=(mn_v+mx_v)/2; ca=(mn_a+mx_a)/2
        # Distance euclidienne centrée
        dist=((valence-cv)**2+(arousal-ca)**2)**.5
        # Bonus si dans la zone
        in_zone=1.2 if (mn_v<=valence<=mx_v and mn_a<=arousal<=mx_a) else 1.0
        score=in_zone/(dist+0.001)
        scored.append((score,lbl,lbl_fr))
    scored.sort(key=lambda x:-x[0])
    top=scored[:n+2]  # prendre un peu plus pour softmax
    total=sum(s for s,_,_ in top)
    return [{"label":lbl,"label_fr":lbl_fr,"weight":round(s/total,3)} for s,lbl,lbl_fr in top[:n]]


class EmotionalStateTracker:
    def __init__(self):
        self._v=0.; self._a=0.3; self._intensity=0.; self._duration=1; self._last=""
        self._history:list=[]
        # Humeur de fond (timescale lente — jours en vrai, ~50 ticks ici)
        self._background_valence=0.05
        self._background_arousal=0.35

    def update(self, amygdala:Amygdala, insula:Insula, nt:NeurotransmitterSystem) -> None:
        iv=amygdala.emotional_valence*.4+insula.felt_emotion.get("valence",0.)*.3+nt.mood_valence*.3
        ia=amygdala.emotional_arousal*.4+insula.felt_emotion.get("arousal",.3)*.3+nt.arousal_level*.3
        smooth=max(.4,.7-min(1.,abs(iv)+ia)*.3)
        self._v=self._v*smooth+iv*(1-smooth)
        self._a=self._a*smooth+ia*(1-smooth)
        # Humeur de fond (décroissance très lente vers neutre)
        self._background_valence=self._background_valence*.995+nt.mood_valence*.005
        self._background_arousal=self._background_arousal*.995+nt.arousal_level*.005
        self._intensity=(abs(self._v)+self._a)/2
        matrix=get_emotion_matrix(self._v,self._a)
        top_label=matrix[0]["label"] if matrix else "neutral"
        self._duration=self._duration+1 if top_label==self._last else 1
        self._last=top_label
        self._history.append({"valence":round(self._v,3),"arousal":round(self._a,3),
            "label":top_label,"intensity":round(self._intensity,3)})
        if len(self._history)>100: self._history.pop(0)

    def current_state(self) -> dict:
        matrix=get_emotion_matrix(self._v,self._a,3)
        top=matrix[0] if matrix else {"label":"neutral","label_fr":"neutre","weight":1.0}
        return {"label":top["label"],"label_fr":top["label_fr"],
                "valence":round(self._v,3),"arousal":round(self._a,3),
                "intensity":round(self._intensity,3),"duration":self._duration,
                "emotion_matrix":matrix,
                "background":{"valence":round(self._background_valence,3),
                               "arousal":round(self._background_arousal,3)}}

    def get_history(self): return list(self._history)


# ─────────────────────────────────────────────────────────────────────────────
# §9  CONSCIENCE
# ─────────────────────────────────────────────────────────────────────────────

class ConsciousnessMonitor:
    def __init__(self):
        self._level=0.5; self._meta=0.; self._content="background"; self._ws:list=[]
    def update(self,pfc,thalamus,dmn,signals,tick):
        strong=[s for s in signals if s.strength>0.4]
        diversity=len(set(s.signal_type for s in strong))
        richness=min(1.,diversity*.15+len(strong)*.05)
        dmn_c=dmn.activation*.3 if dmn.mind_wandering else 0.
        new=thalamus.attention_gate*.25+pfc.activation*.30+max(.2,1.-pfc.fatigue*.6)*.15+richness*.20+dmn_c*.10
        self._level=self._level*.8+new*.2
        if pfc.cognitive_load<.7 and pfc.activation>.3:
            ints=[s for s in signals if s.signal_type=="internal"]
            self._meta=min(1.,self._meta*.8+len(ints)*.1) if ints else self._meta*.9
        else: self._meta*=.85
        self._content=(f"{max(strong,key=lambda s:s.strength).source}" if strong
                       else ("internal" if dmn.mind_wandering else "background"))
        self._ws=[{"source":s.source,"type":s.signal_type,"strength":round(s.strength,3)} for s in strong[:5]]
    def current_state(self):
        lbl=("unconscious" if self._level<.2 else "subconscious" if self._level<.4
             else "conscious" if self._level<.65 else "focused" if self._level<.85 else "heightened")
        return {"level":round(self._level,3),"label":lbl,"meta_awareness":round(self._meta,3),
                "content":self._content,"global_workspace":self._ws}


# ─────────────────────────────────────────────────────────────────────────────
# §10  CERVEAU COMPLET — ORCHESTRATEUR
# ─────────────────────────────────────────────────────────────────────────────

class Brain:
    """
    Cerveau complet avec corps numérique intégré.
    Boucle complète: Monde → Corps → Cerveau → Corps → Conscience
    """
    def __init__(self):
        self.nt    = NeurotransmitterSystem()
        # Corps
        self.body  = BodySystem()
        # Régions
        self.brainstem=Brainstem(); self.thalamus=Thalamus()
        self.amygdala=Amygdala();   self.hippocampus=Hippocampus()
        self.pfc=PrefrontalCortex(); self.basal_ganglia=BasalGanglia()
        self.cerebellum=Cerebellum(); self.insula=Insula()
        self.cingulate=CingulateCortex(); self.sensory_cortex=SensoryCortex()
        self.dmn=DefaultModeNetwork()
        self._regions={
            "brainstem":self.brainstem,"thalamus":self.thalamus,
            "amygdala":self.amygdala,"hippocampus":self.hippocampus,
            "prefrontal_cortex":self.pfc,"basal_ganglia":self.basal_ganglia,
            "cerebellum":self.cerebellum,"insula":self.insula,
            "cingulate_cortex":self.cingulate,"sensory_cortex":self.sensory_cortex,
            "default_mode_network":self.dmn,
        }
        # Systèmes émergents
        self.impulse_engine    = ImpulseEngine()
        self.introspection     = IntrospectionEngine()
        self.emotional_tracker = EmotionalStateTracker()
        self.consciousness     = ConsciousnessMonitor()
        self._tick=0; self.last_action:Optional[str]=None

    def sense(self, stim: SensoryInput) -> dict:
        """Input principal: SensoryInput dimensionnel → passe par le corps."""
        body_signals = self.body.process(stim, self.nt)
        for sig in body_signals:
            t=sig.target
            if t in self._regions: self._regions[t].receive(sig)
        return self.tick()

    def perceive(self, stimulus:dict) -> dict:
        """Input legacy: dict simple → converti en SensoryInput minimal."""
        si=SensoryInput(
            meca_force=stimulus.get("threat",0.)*0.5,
            meca_vitesse=stimulus.get("threat",0.)*0.7,
            sem_valence=stimulus.get("valence",0.),
            sem_charge=stimulus.get("intensity",0.5),
            sem_arousal=stimulus.get("arousal",0.3),
            sem_menace=stimulus.get("threat",0.),
            chem_da=stimulus.get("reward",0.)*0.3,
            novelty=stimulus.get("novelty",0.5),
            stimulus_id=stimulus.get("stimulus_id",""),
        )
        if stimulus.get("modality")=="threat": si.meca_force=max(si.meca_force,stimulus.get("intensity",.5)*.4)
        if stimulus.get("modality")=="social": si.sem_social=0.7; nt_mod={"oxytocin":0.05}; self.nt.modulate(nt_mod)
        return self.sense(si)

    def tick(self) -> dict:
        self._tick+=1
        all_emitted:list[NeuralSignal]=[]
        for r in self._regions.values():
            all_emitted.extend(r.process(self.nt))

        for sig in all_emitted:
            t=sig.target
            if t in self._regions:   self._regions[t].receive(sig)
            elif t=="output":
                if sig.content.get("action"): self.last_action=sig.content["action"]
            elif t=="broadcast":
                for r in self._regions.values(): r.receive(sig)

        # DMN reçoit un signal de repos systématiquement
        self.dmn.receive(NeuralSignal("brain","default_mode_network","internal",{"tick":self._tick},.1))

        # Élans spontanés
        imp=self.impulse_engine.tick(self.nt,self.pfc,self.hippocampus,self._tick)
        if imp:
            all_emitted.append(imp); self.dmn.receive(imp)

        # Introspection
        self.introspection.tick(self.amygdala,self.insula,self.pfc,self.hippocampus,self.nt,self._tick)

        # Homéostasie chimique
        self.nt.decay()

        # Décroissance passive de la douleur (même sans nouveau stimulus)
        self.body.nociception.fast_pain = max(0.0, self.body.nociception.fast_pain - 0.08)
        self.body.nociception.slow_pain = max(0.0, self.body.nociception.slow_pain - 0.04)

        # Boucle efférente cerveau → corps → insula
        ans_sig=self.body.update_from_brain(self.amygdala.fear_level,self.pfc.inhibition_signal,self.nt)
        if ans_sig: self.insula.receive(ans_sig)

        # États émergents
        self.emotional_tracker.update(self.amygdala,self.insula,self.nt)
        self.consciousness.update(self.pfc,self.thalamus,self.dmn,all_emitted,self._tick)

        return self.get_state()

    def inject_reward(self, v:float) -> None:
        self.basal_ganglia.receive(NeuralSignal("env","basal_ganglia","reward",
            {"reward_received":v},abs(v),v))
        if v>0: self.nt.modulate({"dopamine":v*.1,"serotonin":v*.03})
        else: self.nt.modulate({"cortisol":abs(v)*.05})

    def get_state(self) -> dict:
        return {
            "tick":self._tick,
            "regions":{n:r.get_state() for n,r in self._regions.items()},
            "neurotransmitters":self.nt.snapshot(),
            "emotional_state":self.emotional_tracker.current_state(),
            "consciousness":self.consciousness.current_state(),
            "body_state":self.body.state.copy(),
            "impulse":self.impulse_engine.get_state(),
            "introspection":self.introspection.get_state(),
            "last_action":self.last_action,
        }

    def get_summary(self) -> dict:
        emo=self.emotional_tracker.current_state(); con=self.consciousness.current_state()
        imp=self.impulse_engine
        return {
            "tick":self._tick,
            "emotion":emo["label"],"emotion_fr":emo["label_fr"],
            "emotion_matrix":emo["emotion_matrix"],
            "valence":round(self.nt.mood_valence,3),"arousal":round(self.nt.arousal_level,3),
            "stress":round(self.nt.stress_level,3),"motivation":round(self.nt.motivation,3),
            "action":self.last_action,"consciousness_level":round(con["level"],3),
            "mind_wandering":self.dmn.mind_wandering,
            "pfc_load":round(self.pfc.cognitive_load,3),
            "impulse":imp.current_impulse,"impulse_strength":round(imp.impulse_strength,3),
            "pain":round(self.body.nociception.total_pain,3),
            "heart_rate":round(self.body.ans.heart_rate,3),
            "background_mood":emo["background"],
        }


# ─────────────────────────────────────────────────────────────────────────────
# §11  API PUBLIQUE
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PerceptionResult:
    """
    Résultat complet d'un cycle de traitement.

    ÉMOTIONNEL:
      emotion        str          dominant: "joy","fear","calm","anxiety","melancholy"...
      emotion_fr     str          français: "joie / euphorie"...
      emotion_matrix list[dict]   top-3 avec poids ex: [{"label":"fear","weight":0.54}, ...]
      valence        float -1→+1  valence intégrée
      arousal        float 0→1    niveau d'éveil
      background     dict         humeur de fond (timescale lente)

    CONSCIENCE:
      consciousness  float 0→1    niveau de conscience
      meta_awareness float 0→1    méta-conscience / introspection
      mind_wandering bool         DMN actif (rêverie)

    DÉCISION:
      action         str|None     "approach","avoid","explore","engage","maintain","rest"

    CORPS:
      body_state     dict         métriques physiologiques complètes
      pain           float 0→1    niveau de douleur total
      heart_rate     float        fréquence cardiaque normalisée

    SPONTANÉ:
      impulse        str|None     élan actuel: "curiosity","social","creative","rest"...
      introspection  dict         rapport de méta-conscience (si disponible)

    NEUROCHIMIE:
      stress         float 0→1    niveau de stress émergent
      motivation     float 0→1    motivation
      mood           float -1→+1  humeur neurochimique
    """
    emotion:str; emotion_fr:str; emotion_matrix:list
    valence:float; arousal:float; emotion_intensity:float; emotion_duration:int
    background:dict; consciousness:float; consciousness_label:str
    meta_awareness:float; mind_wandering:bool
    action:Optional[str]; action_confidence:float
    body_state:dict; pain:float; heart_rate:float; ans_balance:float
    impulse:Optional[str]; impulse_strength:float; impulse_meaning:str
    introspection:dict; meta_questions:list
    cognitive_load:float; pfc_fatigue:float
    stress:float; motivation:float; mood:float
    memory_count:int; last_encoded:bool; tick:int
    _full_state:dict=field(default_factory=dict,repr=False)

    def to_dict(self) -> dict:
        return {
            "tick":self.tick,"emotion":self.emotion,"emotion_fr":self.emotion_fr,
            "emotion_matrix":self.emotion_matrix,"valence":self.valence,"arousal":self.arousal,
            "emotion_intensity":self.emotion_intensity,"background":self.background,
            "consciousness":self.consciousness,"consciousness_label":self.consciousness_label,
            "meta_awareness":self.meta_awareness,"mind_wandering":self.mind_wandering,
            "action":self.action,"action_confidence":self.action_confidence,
            "body_state":self.body_state,"pain":self.pain,"heart_rate":self.heart_rate,
            "impulse":self.impulse,"impulse_meaning":self.impulse_meaning,
            "introspection":self.introspection,"meta_questions":self.meta_questions,
            "cognitive_load":self.cognitive_load,"stress":self.stress,
            "motivation":self.motivation,"mood":self.mood,
            "memory_count":self.memory_count,
        }

    def __str__(self):
        top3=" + ".join(f"{e['label']}({e['weight']:.0%})" for e in self.emotion_matrix)
        imp=f"[élan:{self.impulse}]" if self.impulse else ""
        pain=f" DOULEUR={self.pain:.2f}" if self.pain>0.1 else ""
        return (f"[t={self.tick}] {top3} | v={self.valence:+.2f} a={self.arousal:.2f} "
                f"| action={self.action} | ♡={self.heart_rate:.2f}{pain} {imp}")


class DeepBrain:
    """
    Interface complète pour Deep Sanctuary v2.

    USAGE MINIMAL:
        brain = DeepBrain()
        # SensoryInput dimensionnel (sans labels)
        r = brain.sense(SensoryInput(meca_force=0.8, meca_vitesse=0.9,
                                      meca_zone=0.2, location="visage"))
        print(r.emotion_matrix)  # top-3 émotions
        print(r.body_state)      # état physiologique
        print(r.impulse)         # élan spontané
        print(r.pain)            # douleur

        # Ou format dict simple (legacy)
        r = brain.perceive({"modality":"threat","threat":0.8,"valence":-0.7})
    """
    def __init__(self):
        self._brain=Brain(); self._prev_mc=0

    def sense(self, stim:SensoryInput) -> PerceptionResult:
        """Input dimensionnel via SensoryInput."""
        return self._to_result(self._brain.sense(stim))

    def perceive(self, stimulus:dict) -> PerceptionResult:
        """Input legacy dict."""
        return self._to_result(self._brain.perceive(stimulus))

    def tick(self) -> PerceptionResult:
        return self._to_result(self._brain.tick())

    def reward(self, v:float) -> None:
        self._brain.inject_reward(max(-1.,min(1.,v)))

    def inject(self, nts:dict[str,float]) -> None:
        self._brain.nt.modulate(nts)

    def get_neurochemistry(self) -> dict:
        return self._brain.nt.snapshot()

    def get_body_state(self) -> dict:
        return dict(self._brain.body.state)

    def get_memory_traces(self) -> list:
        return [{"episode_id":t.episode_id,"strength":round(t.strength,3),
                 "emotional_tag":round(t.emotional_tag,3),"valence":round(t.valence,3)}
                for t in self._brain.hippocampus._traces]

    def get_emotional_history(self) -> list:
        return self._brain.emotional_tracker.get_history()

    @property
    def tick_count(self) -> int:
        return self._brain._tick

    def _to_result(self, state:dict) -> PerceptionResult:
        emo=state["emotional_state"]; con=state["consciousness"]; nt=self._brain.nt
        bg=state["regions"].get("basal_ganglia",{}); pfc=state["regions"]["prefrontal_cortex"]
        imp=state["impulse"]; intro=state["introspection"]
        action=bg.get("selected_action") or state.get("last_action")
        cur=len(self._brain.hippocampus._traces); enc=cur>self._prev_mc; self._prev_mc=cur
        bs=dict(state["body_state"]); bs.update({
            "pain_fast":round(self._brain.body.nociception.fast_pain,3),
            "pain_slow":round(self._brain.body.nociception.slow_pain,3),
        })
        imp_type=imp.get("impulse"); imp_meaning=""
        if imp_type: imp_meaning=ImpulseEngine.TYPES.get(imp_type,("",""))[1]
        return PerceptionResult(
            tick=state["tick"],emotion=emo["label"],emotion_fr=emo["label_fr"],
            emotion_matrix=emo["emotion_matrix"],valence=emo["valence"],arousal=emo["arousal"],
            emotion_intensity=emo["intensity"],emotion_duration=emo["duration"],
            background=emo["background"],consciousness=con["level"],consciousness_label=con["label"],
            meta_awareness=con["meta_awareness"],mind_wandering=self._brain.dmn.mind_wandering,
            action=action,action_confidence=round(self._brain.basal_ganglia._av.get(action or "maintain",.5),3),
            body_state=bs,pain=round(self._brain.body.nociception.total_pain,3),
            heart_rate=round(self._brain.body.ans.heart_rate,3),
            ans_balance=round(self._brain.body.ans.balance,3),
            impulse=imp_type,impulse_strength=round(imp.get("strength",0.),3),
            impulse_meaning=imp_meaning,
            introspection=intro.get("self_report",{}),meta_questions=intro.get("meta_questions",[]),
            cognitive_load=pfc.get("cognitive_load",0.),pfc_fatigue=pfc.get("fatigue",0.),
            stress=round(nt.stress_level,3),motivation=round(nt.motivation,3),
            mood=round(nt.mood_valence,3),memory_count=cur,last_encoded=enc,
            _full_state=state,
        )


# ─────────────────────────────────────────────────────────────────────────────
# §12  VISUALISATION
# ─────────────────────────────────────────────────────────────────────────────

def _bar(v,w=18): filled=int(max(0.,min(1.,v))*w); return "█"*filled+"░"*(w-filled)
def _vbar(v,w=20):
    c=w//2; pos=int((v+1)/2*w); bar=list("─"*w); bar[c]="┼"
    if pos>c:
        for i in range(c,min(pos,w)): bar[i]="+"
    elif pos<c:
        for i in range(max(pos,0),c): bar[i]="-"
    bar[max(0,min(pos,w-1))]="●"
    return "".join(bar)

def print_state(brain:Brain) -> None:
    st=brain.get_state(); sm=brain.get_summary(); nt=brain.nt
    emo=st["emotional_state"]; con=st["consciousness"]
    bs=st["body_state"]; imp=st["impulse"]; intro=st["introspection"]
    print(f"\n{'━'*76}")
    print(f"  DEEP SANCTUARY v2  tick #{st['tick']:>4d}")
    print(f"{'━'*76}")

    # Matrice émotionnelle top-3
    print(f"\n  ◈ MATRICE ÉMOTIONNELLE:")
    for i,e in enumerate(emo["emotion_matrix"]):
        bar=_bar(e["weight"],12); mark=" ◀ dominant" if i==0 else ""
        print(f"    {i+1}. {e['label_fr']:<22s} {bar} {e['weight']:.0%}{mark}")

    print(f"\n     Valence:  {_vbar(emo['valence'],22)} {emo['valence']:+.3f}")
    print(f"     Éveil:    {_bar(emo['arousal'],22)} {emo['arousal']:.3f}")
    bg=emo["background"]
    print(f"     Fond:     v={bg['valence']:+.3f}  a={bg['arousal']:.3f}  (humeur de fond)")

    # Corps
    print(f"\n  ◈ CORPS:")
    print(f"     Cœur:     {_bar(bs.get('heart_rate',.5),22)} {bs.get('heart_rate',.5):.3f}")
    print(f"     Respir.:  {_bar(bs.get('breathing',.35),22)} {bs.get('breathing',.35):.3f}")
    print(f"     Tension:  {_bar(bs.get('muscle_tone',.25),22)} {bs.get('muscle_tone',.25):.3f}")
    print(f"     Sueur:    {_bar(bs.get('skin_conduct',.1),22)} {bs.get('skin_conduct',.1):.3f}")
    if brain.body.nociception.total_pain > 0.05:
        print(f"     DOULEUR:  {_bar(brain.body.nociception.total_pain,22)}"
              f" rapide={brain.body.nociception.fast_pain:.2f} lente={brain.body.nociception.slow_pain:.2f}")
    if brain.body.chemistry.active_count()>0:
        print(f"     Chimique: {brain.body.chemistry.active_count()} substance(s) active(s)")

    # Neurotransmetteurs
    print(f"\n  ◈ NEUROTRANSMETTEURS:")
    for nm,rl,key in [("Dopamine","motivation","dopamine"),("Sérotonine","humeur","serotonin"),
                       ("Noradrénaline","éveil","norepinephrine"),("Acétylcholine","mémoire","acetylcholine"),
                       ("GABA","inhibition","gaba"),("Cortisol","stress","cortisol"),
                       ("Ocytocine","social","oxytocin"),("Endorphines","plaisir","endorphins")]:
        val=getattr(nt,key); alert=" ⚠" if (key=="cortisol" and val>0.6) else ""
        print(f"     {nm:<14s} {_bar(val,14)} {val:.3f}  ({rl}){alert}")

    # Conscience et élans
    print(f"\n  ◈ CONSCIENCE: [{con['label'].upper()}]  {con['level']:.3f}")
    print(f"     méta-conscience={con['meta_awareness']:.3f}")
    if brain.dmn.mind_wandering:
        print(f"     ✦ mind-wandering: {brain.dmn.current_thought_type}")
    if imp.get("impulse"):
        itype=imp["impulse"]; meaning=ImpulseEngine.TYPES.get(itype,("",""))[1]
        print(f"     ✦ ÉLAN SPONTANÉ: [{itype}]  ({meaning})  force={imp.get('strength',0.):.2f}")
    if intro.get("meta_questions"):
        print(f"     ✦ INTROSPECTION: {intro['meta_questions'][0]}")

    # Régions actives
    print(f"\n  ◈ RÉGIONS:")
    for n,rs in st["regions"].items():
        a=rs["activation"]; f=rs["fatigue"]
        if a>0.1: print(f"     {n:<28s} {_bar(a,10)} {a:.2f}  fat={f:.2f}")

    print(f"\n  ACTION: {sm['action']}  |  stress={sm['stress']:.3f}  |  motivation={sm['motivation']:.3f}")
    print(f"{'━'*76}\n")


# ─────────────────────────────────────────────────────────────────────────────
# §13  EXPÉRIENCES
# ─────────────────────────────────────────────────────────────────────────────

def exp_emotion(brain:Brain) -> None:
    print(f"\n{'='*64}\nEXPÉRIENCE: Émergence des émotions\n{'='*64}")
    print("\n[Phase 1] Récompense positive")
    for i in range(5):
        brain.sense(SensoryInput(chem_da=0.4,chem_sero=0.2,chem_opioid=0.3,
            chem_lipophile=0.6,sem_valence=0.6,sem_charge=0.5,novelty=0.5,
            stimulus_id="reward_A"))
        brain.inject_reward(0.7); sm=brain.get_summary()
        top3=" / ".join(f"{e['label']}({e['weight']:.0%})" for e in sm["emotion_matrix"])
        print(f"  tick {sm['tick']:3d}: {top3}")
    print("\n[Phase 2] Impact soudain fort")
    for i in range(3):
        brain.sense(SensoryInput(meca_force=0.85,meca_vitesse=0.95,meca_zone=0.2,location="torse"))
        sm=brain.get_summary()
        top3=" / ".join(f"{e['label']}({e['weight']:.0%})" for e in sm["emotion_matrix"])
        print(f"  tick {sm['tick']:3d}: {top3}  DOULEUR={sm['pain']:.2f}  FC={sm['heart_rate']:.2f}")
    print("\n[Phase 3] Repos — retour et élans")
    for i in range(8):
        brain.tick(); sm=brain.get_summary()
        imp=f" [élan:{sm['impulse']}]" if sm['impulse'] else ""
        print(f"  tick {sm['tick']:3d}: {sm['emotion']:15s} v={sm['valence']:+.2f} wandering={sm['mind_wandering']}{imp}")
    print("\n[Phase 4] Son immersif (texture sonore complexe)")
    for i in range(4):
        brain.sense(SensoryInput(audio_grave=0.7,audio_medium=0.5,audio_aigu=0.6,
            audio_rugosite=0.8,audio_rythme=0.65,audio_dynamique=0.85,audio_spatial=0.8))
        sm=brain.get_summary()
        top3=" / ".join(f"{e['label']}({e['weight']:.0%})" for e in sm["emotion_matrix"])
        print(f"  tick {sm['tick']:3d}: {top3}  FC={sm['heart_rate']:.2f}")


def exp_body(brain:Brain) -> None:
    print(f"\n{'='*64}\nEXPÉRIENCE: Corps numérique — réactions physiologiques\n{'='*64}")
    def show(sm,label=""):
        print(f"  tick {sm['tick']:3d} {label:<20s}: "
              f"FC={sm['heart_rate']:.3f}  "
              f"douleur={sm['pain']:.3f}  "
              f"ANS={brain.body.ans.balance:.2f}  "
              f"émotion={sm['emotion']}")

    print("\n[Phase 1] Baseline — repos")
    for _ in range(3): show(brain.get_summary()," "); brain.tick()

    print("\n[Phase 2] Contact mécanique soudain et fort")
    for _ in range(3):
        brain.sense(SensoryInput(meca_force=0.9,meca_vitesse=0.98,meca_zone=0.15,location="visage"))
        show(brain.get_summary(),"impact fort")

    print("\n[Phase 3] Contact doux et prolongé")
    for _ in range(4):
        brain.sense(SensoryInput(meca_force=0.04,meca_vitesse=0.06,meca_zone=0.85,
                                  thermal=0.62,meca_duration=0.9,location="bras"))
        brain.nt.modulate({"oxytocin":0.05})
        show(brain.get_summary(),"contact doux")

    print("\n[Phase 4] Substance chimique GABAergique-like (effet progressive)")
    for i in range(6):
        if i<2:
            brain.sense(SensoryInput(chem_gaba=0.5,chem_nmda=-0.4,chem_da=0.25,
                                      chem_lipophile=0.75,chem_onset=0.25,
                                      stimulus_id="substance_G"))
        else:
            brain.tick()
        sm=brain.get_summary()
        print(f"  tick {sm['tick']:3d} substance_G t+{i}  : "
              f"GABA={brain.nt.gaba:.3f}  DA={brain.nt.dopamine:.3f}  "
              f"arousal={sm['arousal']:.3f}  émotion={sm['emotion']}")

    print("\n[Phase 5] Stimulant adénosine-bloquant (café-like)")
    brain.sense(SensoryInput(chem_adenosine=-0.7,chem_ne=0.35,chem_da=0.2,
                              chem_lipophile=0.65,chem_onset=0.55,stimulus_id="substance_A"))
    for i in range(4):
        brain.tick(); sm=brain.get_summary()
        print(f"  tick {sm['tick']:3d} stimulant t+{i}   : "
              f"NE={brain.nt.norepinephrine:.3f}  éveil={sm['arousal']:.3f}  action={sm['action']}")

    print("\n[Phase 6] Contenu sémantique menaçant puis intime")
    brain.sense(SensoryInput(sem_valence=-0.75,sem_menace=0.8,sem_charge=0.85,
                              sem_arousal=0.7,sem_complexite=0.5))
    sm=brain.get_summary()
    print(f"  menace sémantique: {sm['emotion']}  stress={sm['stress']:.3f}")
    brain.sense(SensoryInput(sem_valence=0.7,sem_intimite=0.85,sem_social=0.75,
                              sem_charge=0.6,sem_arousal=0.35))
    brain.nt.modulate({"oxytocin":0.1})
    sm=brain.get_summary()
    print(f"  intimité sémantique: {sm['emotion']}  social={brain.nt.social_openness:.3f}")


def exp_impulse(brain:Brain) -> None:
    print(f"\n{'='*64}\nEXPÉRIENCE: Élans spontanés et introspection\n{'='*64}")
    print("\n[Phase 1] Repos pur — observer les élans spontanés")
    for i in range(20):
        brain.tick(); sm=brain.get_summary()
        if sm["impulse"] or sm["mind_wandering"]:
            imp=f"ÉLAN:{sm['impulse']}({sm['impulse_strength']:.2f})" if sm["impulse"] else ""
            wand=f"[{brain.dmn.current_thought_type}]" if sm["mind_wandering"] else ""
            print(f"  tick {sm['tick']:3d}: {sm['emotion']:15s} v={sm['valence']:+.2f}  {imp} {wand}")

    print("\n[Phase 2] Forcer fatigue — observer le drive de repos")
    for i in range(10):
        brain.sense(SensoryInput(sem_charge=0.9,sem_arousal=0.8,sem_complexite=0.9))
    for i in range(8):
        brain.tick(); sm=brain.get_summary()
        print(f"  tick {sm['tick']:3d}: fatigue_PFC={brain.pfc.fatigue:.3f}  "
              f"élan={sm['impulse']}  repos_drive={brain.impulse_engine._drives['rest']:.3f}")

    print("\n[Phase 3] Introspection — rapport de conscience de soi")
    brain.tick()
    intro=brain.introspection
    if intro.self_report:
        print("  Rapport introspectif:")
        for k,v in intro.self_report.items():
            print(f"    {k}: {v}")
        if intro.meta_questions:
            print("  Questions émergentes:")
            for q in intro.meta_questions:
                print(f"    → '{q}'")
    else:
        print("  (introspection pas encore déclenchée)")


def exp_stress(brain:Brain) -> None:
    print(f"\n{'='*64}\nEXPÉRIENCE: Stress et récupération\n{'='*64}")
    print("\n[Phase 1] Baseline"); [brain.tick() for _ in range(3)]
    sm=brain.get_summary(); print(f"  Baseline: stress={sm['stress']:.3f}  FC={sm['heart_rate']:.3f}")
    print("\n[Phase 2] Menace intense + impact")
    for i in range(4):
        brain.sense(SensoryInput(meca_force=0.8,meca_vitesse=0.9,sem_menace=0.9,
            sem_valence=-0.85,sem_arousal=0.95,sem_charge=0.9))
        sm=brain.get_summary()
        print(f"  tick {sm['tick']:3d}: stress={sm['stress']:.3f}  NE={brain.nt.norepinephrine:.3f}"
              f"  cortisol={brain.nt.cortisol:.3f}  FC={sm['heart_rate']:.3f}  action={sm['action']}")
    print("\n[Phase 3] Récupération")
    for i in range(10):
        brain.tick(); sm=brain.get_summary()
        print(f"  tick {sm['tick']:3d}: stress={sm['stress']:.3f}  FC={sm['heart_rate']:.3f}"
              f"  émotion={sm['emotion']}  élan={sm['impulse'] or '-'}")


def run_demo(brain:Brain) -> None:
    print("\n"+"="*76+"\n  DEEP SANCTUARY v2 — Démo corps + cerveau\n"+"="*76)
    scenarios=[
        ("Paysage lumineux et calme",
         SensoryInput(visual_lum=0.8,visual_chaleur=0.6,visual_contraste=0.3,
                      sem_valence=0.4,sem_arousal=0.2,novelty=0.6)),
        ("Impact inattendu — force modérée",
         SensoryInput(meca_force=0.7,meca_vitesse=0.88,meca_zone=0.25,location="bras")),
        ("Son immersif, rythmé, rugueux",
         SensoryInput(audio_grave=0.8,audio_medium=0.6,audio_aigu=0.65,audio_rugosite=0.85,
                      audio_rythme=0.7,audio_dynamique=0.9,audio_spatial=0.75)),
        ("Contact doux et chaleureux",
         SensoryInput(meca_force=0.03,meca_vitesse=0.05,meca_zone=0.9,thermal=0.65,
                      meca_duration=0.8,sem_intimite=0.7,location="épaule")),
    ]
    for name,stim in scenarios:
        print(f"\n→ {name}")
        brain.sense(stim); print_state(brain)
    print("\nRepos (5 ticks)...")
    for _ in range(5): brain.tick()
    print_state(brain)


def run_free(brain:Brain, ticks:int) -> None:
    print(f"\n{'='*76}\n  Simulation libre — {ticks} ticks\n{'='*76}")
    stimuli=[
        SensoryInput(audio_grave=0.6,audio_medium=0.5,audio_rugosite=0.3,audio_rythme=0.7),
        SensoryInput(visual_lum=0.7,visual_chaleur=0.6,novelty=0.6,sem_valence=0.3),
        SensoryInput(sem_charge=0.7,sem_valence=-0.3,sem_menace=0.4,sem_arousal=0.6),
        SensoryInput(meca_force=0.05,meca_zone=0.8,thermal=0.6,sem_intimite=0.5),
    ]
    for i in range(ticks):
        if i%6==3: brain.sense(random.choice(stimuli))
        else: brain.tick()
        sm=brain.get_summary()
        top=sm["emotion_matrix"][0]; w2=sm["emotion_matrix"][1] if len(sm["emotion_matrix"])>1 else {"label":"","weight":0}
        imp=f"[{sm['impulse']}]" if sm["impulse"] else ""
        print(f"  t={brain._tick:3d}: {top['label']:12s}({top['weight']:.0%}) + {w2['label']:10s}({w2['weight']:.0%})"
              f"  v={sm['valence']:+.2f}  FC={sm['heart_rate']:.2f}  {imp}")


# ─────────────────────────────────────────────────────────────────────────────
# §14  POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser=argparse.ArgumentParser(description="Deep Sanctuary v2 — Corps + Cerveau")
    parser.add_argument("--demo",  action="store_true")
    parser.add_argument("--exp",   type=str,default="emotion",
        choices=["emotion","body","impulse","stress","all"])
    parser.add_argument("--ticks", type=int,default=0)
    args=parser.parse_args()

    brain=Brain()
    print("\n  ✦ Deep Sanctuary v2 initialisé — corps + cerveau prêts")

    if args.demo: run_demo(brain)
    elif args.ticks>0: run_free(brain,args.ticks)
    elif args.exp=="all":
        for fn in [exp_emotion,exp_body,exp_impulse,exp_stress]:
            fn(Brain())
    elif args.exp=="emotion":  exp_emotion(brain)
    elif args.exp=="body":     exp_body(brain)
    elif args.exp=="impulse":  exp_impulse(brain)
    elif args.exp=="stress":   exp_stress(brain)

    print("\n  ✦ Simulation terminée.\n")


if __name__=="__main__":
    main()
