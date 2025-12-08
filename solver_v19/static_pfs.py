"""
static_pfs.py — Stabilité statique (PFS)
---------------------------------------

Calcule pour chaque mode (transport, work) :

- Moments renversants latéral et longitudinal
- Moments stabilisants
- Indices de stabilité ISO (latéral / longitudinal / min)
- Distances au polygone de sustentation
- Direction du risque statique

Les formules sont celles démontrées dans ta documentation.
"""

import numpy as np
from .geometry import get_geometry


# -----------------------------------------------------------
# Distances pures (2D) entre CG au sol et bords du rectangle
# -----------------------------------------------------------

def distances_pure(CG_ground, track_rear, wheelbase):
    """
    Calcule les distances minimales entre la projection 2D du CG et :

    - la ligne latérale gauche/droite (± track_rear/2)
    - la ligne avant/arrière (basées sur 0 et wheelbase)

    Retourne :
        d_lat  : distance latérale (m)
        d_long : distance longitudinale (m)
    """
    x, y = CG_ground

    # Distance à la limite latérale (droite/gauche)
    d_lat = (track_rear / 2.0) - abs(y)

    # Distance à l'avant et à l'arrière
    d_long_front = (wheelbase / 2.0) - x
    d_long_rear  = x + (wheelbase / 2.0)

    d_long = min(d_long_front, d_long_rear)

    return d_lat, d_long


# -----------------------------------------------------------
# Distances "effectives" pondérées par Z0/ZG
# -----------------------------------------------------------

def distances_effective(d_lat, d_long, Z0, ZG):
    """
    Applique le facteur ISO :
        d_eff = d * (Z0 / ZG)
    """
    ratio = Z0 / ZG
    return d_lat * ratio, d_long * ratio


# -----------------------------------------------------------
# Moments statiques renversants et stabilisants
# -----------------------------------------------------------

def static_moments(MT, ZG, slope_lat, slope_long, track_rear, wheelbase):
    """
    Moments selon la démonstration :

    M_roll       = MT * g * ZG * sin(slope_lat)
    M_rest_roll  = MT * g * (track_rear / 2) * cos(slope_lat)

    M_pitch      = MT * g * ZG * sin(slope_long)
    M_rest_pitch = MT * g * (wheelbase   / 2) * cos(slope_long)
    """

    g = 9.81

    th_lat  = np.radians(slope_lat)
    th_long = np.radians(slope_long)

    # Moments latéraux
    M_roll      = MT * g * ZG * np.sin(th_lat)
    M_rest_roll = MT * g * (track_rear / 2.0) * np.cos(th_lat)

    # Moments longitudinaux
    M_pitch      = MT * g * ZG * np.sin(th_long)
    M_rest_pitch = MT * g * (wheelbase  / 2.0) * np.cos(th_long)

    return M_roll, M_rest_roll, M_pitch, M_rest_pitch


# -----------------------------------------------------------
# Indices de stabilité ISO
# -----------------------------------------------------------

def static_indices(XG, YG, ZG, Z0, track_rear, wheelbase):
    """
    Formules démontrées :

    I_lat  = 1 - (|YG| / (track_rear/2)) * (Z0/ZG)
    I_long = 1 - (|XG - wheelbase/2| / (wheelbase/2)) * (Z0/ZG)

    I_static = min(I_lat, I_long)
    """

    ratio = Z0 / ZG

    # Indice latéral
    I_lat = 1.0 - (abs(YG) / (track_rear / 2.0)) * ratio

    # Position relative du CG en X par rapport au centre
    X_rel = abs(XG)

    I_long = 1.0 - (X_rel / (wheelbase / 2.0)) * ratio

    # Indice final
    I_static = min(I_lat, I_long)

    return I_lat, I_long, I_static


# -----------------------------------------------------------
# Direction du risque (simple mais utile)
# -----------------------------------------------------------

def risk_direction(CG_ground):
    """Analyse simple de la direction du risque."""
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
        CG_data = {
            "transport": {...},
            "work":      {...}
        }

    Sortie :
        {
          "transport": {...résultats...},
          "work":      {...résultats...}
        }
    """

    results = {}

    # Récup géométrie
    track_rear, wheelbase = get_geometry(tractor)

    # Hauteur nominale ISO de référence
    Z0 = tractor.get("cg_height_nominal", 1.0)

    for mode in ["transport", "work"]:

        block = CG_data[mode]

        MT = block["mass_total"]
        CG_rot = block["CG_rotated"]
        CG_ground = block["CG_ground"]

        XG_ground, YG_ground = CG_ground
        ZG = CG_rot[2]

        # ------------------------------------------------------
        # 1) Distances (pures + effectives)
        # ------------------------------------------------------
        d_lat, d_long = distances_pure(CG_ground, track_rear, wheelbase)
        d_lat_eff, d_long_eff = distances_effective(d_lat, d_long, Z0, ZG)

        # ------------------------------------------------------
        # 2) Moments statiques
        # ------------------------------------------------------
        M_roll, M_rest_roll, M_pitch, M_rest_pitch = static_moments(
            MT, ZG, slope_lat, slope_long, track_rear, wheelbase
        )

        # ------------------------------------------------------
        # 3) Indices statiques ISO
        # ------------------------------------------------------
        I_lat, I_long, I_static = static_indices(
            XG_ground, YG_ground, ZG, Z0, track_rear, wheelbase
        )

        # ------------------------------------------------------
        # 4) Direction du risque
        # ------------------------------------------------------
        direction = risk_direction(CG_ground)

        # ------------------------------------------------------
        # 5) Stockage des résultats
        # ------------------------------------------------------
        results[mode] = {
            "I_lat": I_lat,
            "I_long": I_long,
            "I_static": I_static,

            "distances": {
                "lat_pure": d_lat,
                "long_pure": d_long,
                "lat_eff": d_lat_eff,
                "long_eff": d_long_eff
            },

            "moments": {
                "M_roll": M_roll,
                "M_rest_roll": M_rest_roll,
                "M_pitch": M_pitch,
                "M_rest_pitch": M_rest_pitch
            },

            "risk_direction": direction
        }

    return results
