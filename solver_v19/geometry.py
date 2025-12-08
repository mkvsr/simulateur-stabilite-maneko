"""
geometry.py — Module de gestion géométrique du tracteur
-------------------------------------------------------

Contient :
- Conversion degrés → radians
- Matrice de rotation 3D (pente latérale + longitudinale)
- Extraction de la géométrie du tracteur
"""

import numpy as np
import math


# -----------------------------------------------------------
# Conversion d'angles
# -----------------------------------------------------------

def deg_to_rad(angle_deg: float) -> float:
    """ Convertit un angle en degrés vers radians """
    return angle_deg * math.pi / 180.0


# -----------------------------------------------------------
# Matrice de rotation 3D
# -----------------------------------------------------------
def rotation_matrix(slope_lat_deg: float, slope_long_deg: float) -> np.ndarray:
    """
    Convention correcte :
    - slope_lat  (dévers)  = rotation autour de X
    - slope_long (montée)  = rotation autour de Y
    """

    th_lat  = deg_to_rad(slope_lat_deg)
    th_long = deg_to_rad(slope_long_deg)

    # Roulis (dévers) → rotation autour de X
    R_lat = np.array([
        [1, 0,              0               ],
        [0, math.cos(th_lat), -math.sin(th_lat)],
        [0, math.sin(th_lat),  math.cos(th_lat)]
    ])

    # Tangage (montée/descente) → rotation autour de Y
    R_long = np.array([
        [ math.cos(th_long), 0, math.sin(th_long)],
        [ 0,                 1, 0                ],
        [-math.sin(th_long), 0, math.cos(th_long)]
    ])

    # ordre correct = R_longitude **puis** R_lat (conforme à ISO)
    return R_long @ R_lat


# -----------------------------------------------------------
# Extraction géométrie du tracteur
# -----------------------------------------------------------

def get_geometry(tractor: dict):
    """
    Retourne :
    - track_rear : voie arrière
    - wheelbase  : empattement

    Forme du JSON :
    "geometry": {
        "wheelbase": 2.65,
        "track_front": 2.00,
        "track_rear":  1.98
    }
    """
    g = tractor["geometry"]
    wheelbase  = float(g["wheelbase"])
    track_rear = float(g["track_rear"])

    return track_rear, wheelbase
