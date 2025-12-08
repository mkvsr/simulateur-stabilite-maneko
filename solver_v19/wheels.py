"""
wheels.py — Répartition des charges aux roues
---------------------------------------------

Calcule la charge sur les 4 roues :
    FL = Front Left
    FR = Front Right
    RL = Rear Left
    RR = Rear Right

Pour les modes :
    - transport
    - work

Formules ISO (issues du PFS) :

Répartition avant/arrière :
    R_AV = MT * g * (d_AR / L)
    R_AR = MT * g - R_AV

Répartition gauche/droite :
    R_FL = R_AV * (1/2 + YG / T_AV)
    R_FR = R_AV * (1/2 - YG / T_AV)
    R_RL = R_AR * (1/2 + YG / T_AR)
    R_RR = R_AR * (1/2 - YG / T_AR)

NOTE :
Toutes les charges finales sont retournées en kilogrammes.
"""

import numpy as np
from .geometry import get_geometry


g = 9.81  # gravité


# -----------------------------------------------------------
# CALCUL POUR UN MODE (transport ou work)
# -----------------------------------------------------------

def wheel_loads_one_mode(tractor, CG_block):
    """
    Calcule les charges sur les 4 roues pour UN mode.
    Entrée :
        tractor   : json tracteur (géométrie)
        CG_block  : données CG du mode ("transport" ou "work")
    Sortie :
        dict {"FL", "FR", "RL", "RR"} en kg
    """

    # ----- Extraction données CG -----
    MT  = CG_block["mass_total"]
    CGg = CG_block["CG_ground"]  # projection sol
    XG, YG = CGg

    # ----- Géométrie tracteur -----
    track_rear, wheelbase = get_geometry(tractor)
    track_front = tractor["geometry"]["track_front"]

    # ----- Répartition avant/arrière -----
    L = wheelbase
    # distances CG → essieux
    d_AV = (L/2) - XG
    d_AR = XG + (L/2)

    # réactions totales AV / AR
    R_AV = MT * g * (d_AR / L)
    R_AR = MT * g - R_AV

    # ----- Répartition gauche/droite -----
    # essieu avant
    R_FL = R_AV * (0.5 + YG / track_front)
    R_FR = R_AV * (0.5 - YG / track_front)

    # essieu arrière
    R_RL = R_AR * (0.5 + YG / track_rear)
    R_RR = R_AR * (0.5 - YG / track_rear)

    # ----- Conversion en kg -----
    FL = R_FL / g
    FR = R_FR / g
    RL = R_RL / g
    RR = R_RR / g

    return {
        "FL": FL,
        "FR": FR,
        "RL": RL,
        "RR": RR
    }


# -----------------------------------------------------------
# CALCUL GLOBAL : TRANSPORT + WORK
# -----------------------------------------------------------

def compute_wheel_loads(tractor, CG_data):
    """
    Calcule les charges aux roues pour les deux modes.

    Entrée :
        CG_data = { "transport": {...}, "work": {...} }

    Sortie :
        {
            "transport": {"FL", "FR", "RL", "RR"},
            "work":      {"FL", "FR", "RL", "RR"}
        }
    """

    return {
        "transport": wheel_loads_one_mode(tractor, CG_data["transport"]),
        "work":      wheel_loads_one_mode(tractor, CG_data["work"])
    }
