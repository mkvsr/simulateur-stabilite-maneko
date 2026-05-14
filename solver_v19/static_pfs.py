"""
static_pfs.py — Stabilité statique (PFS)
---------------------------------------

Calcule pour chaque mode (transport, work) :

- Moments renversants latéral et longitudinal
- Moments stabilisants
- Indices de stabilité (latéral / longitudinal / min)
- Distances au polygone de sustentation
- Direction du risque statique
"""

import numpy as np
from .geometry import get_geometry


# -----------------------------------------------------------
# Distances pures (2D) entre CG au sol et bords du polygone
# -----------------------------------------------------------

def distances_pure(CG_ground, track_rear, wheelbase):
    """
    Distances entre la projection 2D du CG et les bords du polygone.

    Retourne :
        d_lat  : distance au bord lateral le plus proche (m)
        d_long : distance au bord longitudinal le plus proche (m)
    """
    x, y = CG_ground

    d_lat = (track_rear / 2.0) - abs(y)

    d_long_front = (wheelbase / 2.0) - x
    d_long_rear  = x + (wheelbase / 2.0)
    d_long = min(d_long_front, d_long_rear)

    return d_lat, d_long


# -----------------------------------------------------------
# Moments statiques renversants et stabilisants
# -----------------------------------------------------------

def static_moments(MT, ZG, slope_lat, slope_long, track_rear, wheelbase):
    """
    Moments selon le PFS :

    M_roll       = MT * g * ZG * sin(slope_lat)
    M_rest_roll  = MT * g * (track_rear / 2) * cos(slope_lat)

    M_pitch      = MT * g * ZG * sin(slope_long)
    M_rest_pitch = MT * g * (wheelbase   / 2) * cos(slope_long)
    """

    g = 9.81

    th_lat  = np.radians(slope_lat)
    th_long = np.radians(slope_long)

    M_roll      = MT * g * ZG * np.sin(th_lat)
    M_rest_roll = MT * g * (track_rear / 2.0) * np.cos(th_lat)

    M_pitch      = MT * g * ZG * np.sin(th_long)
    M_rest_pitch = MT * g * (wheelbase  / 2.0) * np.cos(th_long)

    return M_roll, M_rest_roll, M_pitch, M_rest_pitch


# -----------------------------------------------------------
# Indices de stabilité
# -----------------------------------------------------------

def static_indices(XG, YG, ZG, track_rear, wheelbase):
    """
    Formules des indices de stabilité :

    I_lat  = 1 - (|YG| / (track_rear/2)) * ZG
    I_long = 1 - (|XG| / (wheelbase/2))  * ZG

    I_static = min(I_lat, I_long)

    Logique :
    - |YG| / (TAR/2) : ratio de déplacement latéral (0=centre, 1=bord)
    - |XG| / (L/2)   : ratio de déplacement longitudinal (0=centre, 1=bord)
    - ZG : hauteur du CG global — plus le CG est haut, plus l'indice est pénalisé
    - Indice 1.0 = CG au centre (stabilité maximale)
    - Indice 0.0 = CG sur le bord du polygone
    - Indice < 0  = CG hors polygone = renversement
    """

    I_lat  = 1.0 - (abs(YG) / (track_rear / 2.0)) * ZG
    I_long = 1.0 - (abs(XG) / (wheelbase  / 2.0)) * ZG
    I_static = min(I_lat, I_long)

    return I_lat, I_long, I_static


# -----------------------------------------------------------
# Direction du risque
# -----------------------------------------------------------

def risk_direction(CG_ground):
    """Détermine la direction du risque dominant."""
    x, y = CG_ground

    if abs(y) > abs(x):
        return "lateral_left" if y > 0 else "lateral_right"
    else:
        return "front" if x > 0 else "rear"


# -----------------------------------------------------------
# FONCTION PRINCIPALE : STABILITÉ STATIQUE
# -----------------------------------------------------------

def compute_static_stability(tractor, CG_data, slope_lat, slope_long):
    """
    Entrée :
        CG_data = { "transport": {...}, "work": {...} }

    Sortie :
        { "transport": {...}, "work": {...} }
    """

    results = {}
    track_rear, wheelbase = get_geometry(tractor)

    for mode in ["transport", "work"]:

        block      = CG_data[mode]
        MT         = block["mass_total"]
        CG_rot     = block["CG_rotated"]
        CG_ground  = block["CG_ground"]

        XG_ground, YG_ground = CG_ground
        ZG = CG_rot[2]

        # 1) Distances pures au polygone
        d_lat, d_long = distances_pure(CG_ground, track_rear, wheelbase)

        # 2) Moments statiques
        M_roll, M_rest_roll, M_pitch, M_rest_pitch = static_moments(
            MT, ZG, slope_lat, slope_long, track_rear, wheelbase
        )

        # 3) Indices de stabilité
        I_lat, I_long, I_static = static_indices(
            XG_ground, YG_ground, ZG, track_rear, wheelbase
        )

        # 4) Direction du risque
        direction = risk_direction(CG_ground)

        results[mode] = {
            "I_lat":    I_lat,
            "I_long":   I_long,
            "I_static": I_static,

            "distances": {
                "lat_pure":  d_lat,
                "long_pure": d_long,
            },

            "moments": {
                "M_roll":       M_roll,
                "M_rest_roll":  M_rest_roll,
                "M_pitch":      M_pitch,
                "M_rest_pitch": M_rest_pitch
            },

            "risk_direction": direction
        }

    return results
