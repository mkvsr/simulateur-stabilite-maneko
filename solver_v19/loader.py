"""
loader.py — Calcul du CG du chargeur frontal (bras + loader)
-----------------------------------------------------------

Méthode conforme à la documentation interne :
- Les bras ("arms") ont une masse fixe de 260 kg.
- Leur position dépend :
    X = k_arms * wheelbase
    Z = RAR + h_arms
- Le chargeur ("loader") a une masse variable (json).
  Ses positions LOW et HIGH sont définies par :

    X_low  = k_low  * wheelbase
    X_high = k_high * wheelbase

    Z_low  = RAR + kZ_low  * mass_loader
    Z_high = RAR + kZ_high * mass_loader

Toutes les valeurs proviennent du PDF "méthode de réalisation du simulateur".
"""

import numpy as np
from .geometry import get_geometry

def loader_CG(loader_json: dict, tractor: dict, tires: dict, options: dict):
    """
    Calcule le CG total du chargeur :
    = bras + chargeur (LOW ou HIGH)

    loader_json doit contenir :
      - mass_loader
      - mass_arms
      - rules.x.arms / low / high
      - rules.z.arms / k_low / k_high
    """

    if loader_json is None:
        return 0.0, np.zeros(3)

    # ---------------------------------------------------------
    # 1) Extraction du JSON loader
    # ---------------------------------------------------------
    mass_loader = float(loader_json.get("mass_loader", 0.0))
    mass_arms   = float(loader_json.get("mass_arms", 0.0))

    rules_x = loader_json["rules"]["x"]
    rules_z = loader_json["rules"]["z"]

    # ---------------------------------------------------------
    # 2) Rayon roue arrière
    # ---------------------------------------------------------
    rear_tire = options.get("rear_tire")
    tire_data = tires.get(rear_tire)
    rear_diam = tire_data["diameter_mm"] / 1000.0
    RAR = rear_diam / 2.0

    # ---------------------------------------------------------
    # 3) Géométrie du tracteur
    # ---------------------------------------------------------
    track_rear, wheelbase = get_geometry(tractor)

    # ---------------------------------------------------------
    # 4) CG des bras
    # ---------------------------------------------------------
    X_arms = rules_x["arms"] * wheelbase
    Z_arms = RAR + rules_z["arms"]
    CG_arms = np.array([X_arms, 0.0, Z_arms])

    # ---------------------------------------------------------
    # 5) CG du chargeur (LOW/HIGH)
    # ---------------------------------------------------------
    mode = options.get("loader_mode", "low")  # default = low

    if mode == "high":
        X_loader = rules_x["high"] * wheelbase
        Z_loader = RAR + rules_z["k_high"] * mass_loader
    else:
        X_loader = rules_x["low"] * wheelbase
        Z_loader = RAR + rules_z["k_low"] * mass_loader

    CG_loader = np.array([X_loader, 0.0, Z_loader])

    # ---------------------------------------------------------
    # 6) CG total (bras + chargeur)
    # ---------------------------------------------------------
    mass_total = mass_arms + mass_loader

    CG_total = (mass_arms * CG_arms + mass_loader * CG_loader) / mass_total

    return mass_total, CG_total

