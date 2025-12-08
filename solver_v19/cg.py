"""
cg.py — Calcul du Centre de Gravité global (CG)
----------------------------------------------

Ce module calcule le CG du système complet :

    CG_total = Tracteur + Machine(mode) + Loader(mode_user) + masses additionnelles

Pour chaque simulation, on retourne DEUX CG :

    - CG_transport
    - CG_work

Chaque CG comprend :
    - CG_local   : avant rotation (sol plat)
    - CG_rotated : après rotation (pente)
    - CG_ground  : projection 2D au sol
    - masse totale

Le chargeur utilise loader_CG(), la machine dépend du mode,
le tracteur dépend de ses propriétés.
"""

import numpy as np

from .geometry import rotation_matrix
from .loader import loader_CG
from .geometry import get_geometry

#---------------------------------------------------------------------------
# Fonctions génériques d'accumulation de CG
# ---------------------------------------------------------------------------

def accumulate_CG(MT, CG, m, cg):
    """
    Ajoute une masse m et son CG cg dans la somme globale.

    CG_total = (M1*C1 + M2*C2 + ...) / (M1 + M2 + ...)
    Ici, on fait seulement la somme pondérée ; la normalisation
    se fera à la fin.
    """
    if m > 0:
        MT += m
        CG += m * cg
    return MT, CG


# ---------------------------------------------------------------------------
# CG du tracteur
# ---------------------------------------------------------------------------

def tractor_CG(tractor: dict):
    """
    Calcule le CG "nu" du tracteur (sans chargeur).

    Le tracteur est défini par :
        mass
        mass_front_pct
        mass_rear_pct

    Hypothèse :
    - CG longitudinal = position moyenne = wheelbase * (pct_front)
    - CG vertical = hauteur nominale (cg_height_nominal)
    """

    import numpy as np

    m = float(tractor["mass"])

    pct_front = tractor.get("mass_front_pct", 50) / 100.0
    wheelbase = tractor["geometry"]["wheelbase"]


    # Position en X : plus la masse avant est importante, plus le CG avance
    X = (2 * pct_front - 1) * (wheelbase / 2)
    

    # Position en Y : peau de chagrin (axe longitudinal du tracteur)
    Y = 0.0

    # Position en Z : hauteur nominale
    Z = tractor.get("cg_height_nominal", 1.0)

    return m, np.array([X, Y, Z], dtype=float)


# ---------------------------------------------------------------------------
# CG de la machine (mode transport / mode work)
# ---------------------------------------------------------------------------

def machine_CG(machine: dict, tractor: dict, tires: dict,options: dict, mode: str):
    """
    Calcule le CG global de la machine en utilisant la règle officielle :

        CG_x = -L/2 - R - x_rel
        CG_y = y_rel
        CG_z = z_rel

    où :
        L = empattement du tracteur
        R = rayon du pneu arrière
        x_rel, y_rel, z_rel = offsets machine définis dans le JSON machine
    """

    m = float(machine["mass"])

    cg_rel = machine[mode]
    x_rel = float(cg_rel["x_rel"])
    y_rel = float(cg_rel["y_rel"])
    z_rel = float(cg_rel["z_rel"])

    # geometry du tracteur
    wheelbase = tractor["geometry"]["wheelbase"]

    # rayon pneu arrière
    rear_tire_name = options["rear_tire"]
    diam_mm = tires[rear_tire_name]["diameter_mm"]
    R = diam_mm / 2000.0

    # Formules V15 officielles
    x = -wheelbase / 2.0 - R - x_rel
    y = y_rel
    z = z_rel

    return m, np.array([x, y, z], dtype=float)


# ---------------------------------------------------------------------------
# Masses additionnelles (eau, masses roues, masses avant/arrière)
# ---------------------------------------------------------------------------

def extra_masses_CG(options: dict, tractor: dict, tires: dict):
    """
    Retourne :
        MT_extra : masse totale additionnelle
        CG_sum   : somme pondérée = Σ(m_i * pos_i)
    """

    MT_extra = 0.0
    CG_sum = np.zeros(3)

    # Géométrie tracteur
    track_rear, wheelbase = get_geometry(tractor)

    # Rayon roue arrière (Z)
    rear_tire_name = options["rear_tire"]
    rear_diam_m = tires[rear_tire_name]["diameter_mm"] / 1000.0
    R = rear_diam_m / 2.0

    # ------------------------------
    # MASSE ROUE ARG
    # ------------------------------
    m_ARG = options.get("wheel_weight_ARG", 0)
    if m_ARG is not None and m_ARG > 0:
        pos_ARG = np.array([
            -wheelbase / 2.0,      # X = arrière
            +track_rear / 2.0,     # Y = gauche
            R                      # Z = rayon roue
        ])
        MT_extra += m_ARG
        CG_sum += m_ARG * pos_ARG

    # ------------------------------
    # MASSE ROUE ARD
    # ------------------------------
    m_ARD = options.get("wheel_weight_ARD", 0)
    if m_ARD is not None and m_ARD > 0:
        pos_ARD = np.array([
            -wheelbase / 2.0,
            -track_rear / 2.0,
            R
        ])
        MT_extra += m_ARD
        CG_sum += m_ARD * pos_ARD


    # ------------------------------
    # LESTAGE À L'EAU (deux roues AR)
    # ------------------------------
    if options.get("water_ballast", False):

        rear_tire_name = options["rear_tire"]
        V = tires[rear_tire_name]["volume_l"]  # volume en litres

        # masse d’un pneu
        M_one = 0.754875 * V
        # masse totale pour 2 pneus
        M_total = 2 * M_one

        # position CG du liquide (un pneu gauche)
        pos_left = np.array([
            -wheelbase / 2.0,
            +track_rear / 2.0,
            R * 0.3
        ])

        # position CG du liquide (un pneu droit)
        pos_right = np.array([
            -wheelbase / 2.0,
            -track_rear / 2.0,
            R * 0.3
        ])

        # Ajout masse + CG pondéré
        MT_extra += M_one
        CG_sum += M_one * pos_left

        MT_extra += M_one
        CG_sum += M_one * pos_right

    # ------------------------------
    # MASSES ARRIÈRE PARAMÉTRABLES
    # ------------------------------
    rear_mass = options.get("rear_ballast_mass", 0)
    rear_offset = options.get("rear_ballast_offset", 0.0)

    if rear_mass > 0:
        pos_rear_ballast = np.array([
            -wheelbase / 2.0 - rear_offset,   # X = arrière - offset utilisateur
            0.0,                              # Y
            0.8                               # Z
        ])
        MT_extra += rear_mass
        CG_sum += rear_mass * pos_rear_ballast


    # ------------------------------
    # MASSES AVANT PARAMÉTRABLES (V18)
    # ------------------------------
    front_mass = options.get("front_ballast_mass", 0)
    front_offset = options.get("front_ballast_offset", 0.0)

    if front_mass > 0:
        pos_front_ballast = np.array([
            +wheelbase / 2.0 + front_offset,  # X = avant + offset utilisateur
            0.0,                              # Y
            0.8                               # Z
        ])
        MT_extra += front_mass
        CG_sum += front_mass * pos_front_ballast

    return MT_extra, CG_sum

# ---------------------------------------------------------------------------
# CG GLOBAL (transport + work)
# ---------------------------------------------------------------------------

def compute_global_CG(tractor, machine, loader, tires, options,
                      slope_lat, slope_long):
    """
    Calcule DEUX CG globaux :

        - mode transport
        - mode work

    Le chargeur utilise loader_CG(loader, tractor, tires, mode_user)
    -> où mode_user = options["loader_mode"] ("low" ou "high")

    La machine dépend du mode (transport / work).

    Retourne :
    {
        "transport": {...},
        "work": {...}
    }
    """

    # Chargeur : on calcule UNE SEULE FOIS le CG bras+loader
    loader_mass, loader_cg = loader_CG(
        loader,
        tractor,
        tires,
        options
    )

    # Machine : deux modes
    machine_modes = {
        "transport": machine_CG(machine, tractor, tires, options, mode="transport"),
        "work":      machine_CG(machine, tractor, tires, options, mode="work")
    }
    
    results = {}

    for mode in ["transport", "work"]:

        MT = 0.0
        CG = np.zeros(3)

        # ----------------------------------------------------------
        # 1) Tracteur
        # ----------------------------------------------------------
        m, cg = tractor_CG(tractor)
        MT, CG = accumulate_CG(MT, CG, m, cg)

        # ----------------------------------------------------------
        # 2) Machine (selon mode)
        # ----------------------------------------------------------
        m, cg = machine_modes[mode]
        MT, CG = accumulate_CG(MT, CG, m, cg)

        # ----------------------------------------------------------
        # 3) Loader (bras + chargeur low/high)
        # ----------------------------------------------------------
        if options.get("loader_enabled", True) and loader is not None:
            loader_mass, loader_cg = loader_CG(loader, tractor, tires, options)
        else:
            loader_mass, loader_cg = 0.0, np.zeros(3)

        MT, CG = accumulate_CG(MT, CG, loader_mass, loader_cg)

        # ----------------------------------------------------------
        # 4) Masses additionnelles
        # ----------------------------------------------------------
        m_extra, cg_sum = extra_masses_CG(options, tractor, tires)
        if m_extra > 0:
            CG_extra = cg_sum / m_extra
            MT, CG = accumulate_CG(MT, CG, m_extra, CG_extra)

        # ----------------------------------------------------------
        # 5) Normalisation du CG (local)
        # ----------------------------------------------------------
        CG_local = CG / MT

        # ----------------------------------------------------------
        # 6) Rotation selon la pente
        # ----------------------------------------------------------
        R = rotation_matrix(slope_lat, slope_long)
        CG_rot = R @ CG_local

        # ----------------------------------------------------------
        # 7) Projection au sol
        # ----------------------------------------------------------
        CG_ground = np.array([CG_rot[0], CG_rot[1]])

        # ----------------------------------------------------------
        # 8) Stockage
        # ----------------------------------------------------------
        results[mode] = {
            "mass_total": MT,
            "CG_local": CG_local,
            "CG_rotated": CG_rot,
            "CG_ground": CG_ground
        }

    return results
