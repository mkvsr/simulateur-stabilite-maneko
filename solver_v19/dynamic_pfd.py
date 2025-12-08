"""
dynamic_pfd.py — Stabilité dynamique (PFD)
-----------------------------------------

Implémente la partie dynamique de la démonstration :

Forces :
    F_lat  = MT * v^2 / R
    F_long = MT * a_x

Moments dynamiques :
    M_dyn_lat  = F_lat  * ZG
    M_dyn_long = F_long * ZG

Indices dynamiques :
    I_lat_dyn  = 1 - (M_roll + M_dyn_lat)  / M_rest_roll
    I_long_dyn = 1 - (M_pitch + M_dyn_long) / M_rest_pitch

    I_dynamic  = min(I_lat_dyn, I_long_dyn)

Tout est calculé pour les modes "transport" et "work".
"""

import numpy as np


# -----------------------------------------------------------
# Forces dynamiques
# -----------------------------------------------------------

def dynamic_forces(MT, speed, turn_radius, accel_long):
    """
    Calcule les forces dynamiques latérales et longitudinales.

    speed       = vitesse (m/s)
    turn_radius = rayon de virage (m)
    accel_long  = accélération (+) ou freinage (-) (m/s²)
    """
    # Force latérale (si rayon non nul)
    if turn_radius > 0:
        F_lat = MT * (speed ** 2) / turn_radius
    else:
        F_lat = 0.0

    # Force longitudinale
    F_long = MT * accel_long

    return F_lat, F_long


# -----------------------------------------------------------
# Moments dynamiques
# -----------------------------------------------------------

def dynamic_moments(F_lat, F_long, ZG):
    """
    Moments dynamiques = force * hauteur du CG.

    M_dyn_lat  = F_lat  * ZG
    M_dyn_long = F_long * ZG
    """
    M_lat  = F_lat  * ZG
    M_long = F_long * ZG
    return M_lat, M_long


# -----------------------------------------------------------
# Indices dynamiques
# -----------------------------------------------------------

def dynamic_indices(M_roll, M_rest_roll, M_pitch, M_rest_pitch,
                    M_dyn_lat, M_dyn_long):
    """
    Indices dynamiques selon la démonstration :

    I_lat_dyn  = 1 - (M_roll + M_dyn_lat)  / M_rest_roll
    I_long_dyn = 1 - (M_pitch + M_dyn_long) / M_rest_pitch

    I_dynamic = min(...)
    """

    # Éviter division par 0
    if M_rest_roll == 0:
        I_lat = 0
    else:
        I_lat = 1.0 - (M_roll + M_dyn_lat) / M_rest_roll

    if M_rest_pitch == 0:
        I_long = 0
    else:
        I_long = 1.0 - (M_pitch + M_dyn_long) / M_rest_pitch

    I_dyn = min(I_lat, I_long)

    return I_lat, I_long, I_dyn


# -----------------------------------------------------------
# Direction du risque dynamique
# -----------------------------------------------------------

def dynamic_risk_direction(CG_ground, M_dyn_lat, M_dyn_long):
    """
    Détermine la direction du risque dynamique.
    Critère simple :
    - si |M_dyn_lat| > |M_dyn_long| → risque latéral
    - sinon → longitudinal
    """

    if abs(M_dyn_lat) > abs(M_dyn_long):
        return "lateral"
    else:
        return "longitudinal"


# -----------------------------------------------------------
# Fonction principale : dynamique transport / work
# -----------------------------------------------------------

def compute_dynamic_stability(tractor,
                              CG_data,
                              static_data,
                              speed,
                              turn_radius,
                              accel_long):
    """
    Entrée :
        CG_data["transport"], CG_data["work"]
        static_data["transport"], static_data["work"]

    Sortie :
        {
            "transport": {...},
            "work": {...}
        }
    """

    results = {}

    for mode in ["transport", "work"]:

        # ------------------------------
        # Extraction CG
        # ------------------------------
        block = CG_data[mode]
        MT = block["mass_total"]
        CG_rot = block["CG_rotated"]
        CG_ground = block["CG_ground"]

        ZG = CG_rot[2]

        # ------------------------------
        # Forces dynamiques
        # ------------------------------
        F_lat, F_long = dynamic_forces(MT, speed, turn_radius, accel_long)

        # Moments dynamiques
        M_dyn_lat, M_dyn_long = dynamic_moments(F_lat, F_long, ZG)

        # ------------------------------
        # Moments statiques (PFS)
        # ------------------------------
        static_block = static_data[mode]

        M_roll       = static_block["moments"]["M_roll"]
        M_rest_roll  = static_block["moments"]["M_rest_roll"]
        M_pitch      = static_block["moments"]["M_pitch"]
        M_rest_pitch = static_block["moments"]["M_rest_pitch"]

        # ------------------------------
        # Indices dynamiques
        # ------------------------------
        I_lat_dyn, I_long_dyn, I_dynamic = dynamic_indices(
            M_roll, M_rest_roll,
            M_pitch, M_rest_pitch,
            M_dyn_lat, M_dyn_long
        )

        # ------------------------------
        # Direction du risque
        # ------------------------------
        direction = dynamic_risk_direction(CG_ground, M_dyn_lat, M_dyn_long)

        # ------------------------------
        # Stockage
        # ------------------------------
        results[mode] = {
            "I_lat_dyn": I_lat_dyn,
            "I_long_dyn": I_long_dyn,
            "I_dynamic": I_dynamic,

            "moments_dyn": {
                "F_lat": F_lat,
                "F_long": F_long,
                "M_dyn_lat": M_dyn_lat,
                "M_dyn_long": M_dyn_long
            },

            "risk_direction": direction
        }

    return results
