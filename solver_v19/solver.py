"""
solver.py — Orchestration complète du solver V12
------------------------------------------------

Pipeline de calcul :

    CG_data = compute_global_CG(...)
    static  = compute_static_stability(...)
    dynamic = compute_dynamic_stability(...)
    wheels  = compute_wheel_loads(...)

Retourne une structure finale compacte et complète.

Tout est séparé dans des modules propres :
    cg.py
    static_pfs.py
    dynamic_pfd.py
    wheels.py
"""
import json
import numpy as np

from .cg import compute_global_CG
from .static_pfs import compute_static_stability
from .dynamic_pfd import compute_dynamic_stability
from .wheels import compute_wheel_loads
from solver_v19.compatibility import check_compatibility

# ---------------------------------------------------------------------
# Sélection automatique du chargeur selon la masse du tracteur
# ---------------------------------------------------------------------

def select_loader_name(tractor_mass):
    if tractor_mass < 4300:
        return "FL3817"
    elif tractor_mass < 5300:
        return "FL4121"
    elif tractor_mass < 7000:
        return "FL4220"
    elif tractor_mass < 9000:
        return "FL4621"
    elif tractor_mass < 11000:
        return "FL4722"
    else:
        return "FL5033"


# -----------------------------------------------------------
# SOLVER PRINCIPAL
# -----------------------------------------------------------

def solve(tractor, machine, loader, tires, options, env):
    """
    Entrées :
        tractor : JSON tracteur
        machine : JSON machine arrière
        loader  : JSON chargeur frontal
        tires   : dictionnaire pneus (global)
        options : masses etc. + loader_mode ("low"/"high")
        env     : paramètres environnementaux :
                    - slope_lat
                    - slope_long
                    - speed           (m/s)
                    - turn_radius     (m)
                    - accel_long      (m/s²)

    Sortie : dictionnaire complet :
        {
            "CG": {transport, work},
            "static": {...},
            "dynamic": {...},
            "wheels": {...}
        }
    """

    # ------------------------------------------
    # CHARGEUR AUTOMATIQUE (obligatoire si activé)
    # ------------------------------------------


    # Si le chargeur est désactivé → aucun chargeur
    if not options.get("loader_enabled", False):
        loader = None
        print("Chargeur désactivé.")

    else:
        # loader vient de l’interface
        loader = options.get("loader", None)

        # Si l’interface a choisi "Auto"
        if loader is None:
            tractor_mass = tractor.get("mass", 0)
            loader_name = select_loader_name(tractor_mass)
            print(f"Chargeur AUTO sélectionné : {loader_name}")

            loader_path = f"loaders/{loader_name}.json"
            try:
                with open(loader_path, "r") as f:
                    loader = json.load(f)
            except FileNotFoundError:
                print(f"⚠ ERREUR : fichier '{loader_path}' introuvable !")
                loader = None
     
    # -----------------------------
    # 1) CG global (transport + work)
    # -----------------------------
    CG_data = compute_global_CG(
        tractor,
        machine,
        loader,
        tires,
        options,
        slope_lat=env.get("slope_lat", 0),
        slope_long=env.get("slope_long", 0)
    )

    # -----------------------------
    # 2) Stabilité statique (PFS)
    # -----------------------------
    static = compute_static_stability(
        tractor,
        CG_data,
        slope_lat=env.get("slope_lat", 0),
        slope_long=env.get("slope_long", 0)
    )

    # -----------------------------
    # 3) Stabilité dynamique (PFD)
    # -----------------------------
    dynamic = compute_dynamic_stability(
        tractor,
        CG_data,
        static,
        speed=env.get("speed", 0),
        turn_radius=env.get("turn_radius", 0),
        accel_long=env.get("accel_long", 0)
    )

    # -----------------------------
    # 4) Charges aux roues
    # -----------------------------
    wheels = compute_wheel_loads(
        tractor,
        CG_data
    )

    # -----------------------------
    # 5) Regroupement final
    # -----------------------------
    result = {
        "CG": CG_data,
        "static": static,
        "dynamic": dynamic,
        "wheels": wheels
    }

    # ============================================================
    # 6) Analyse des critères de sécurité (V19)
    # ============================================================
    try:
        from solver_v19.compatibility import check_compatibility

        compat = check_compatibility({
            "wheels": wheels["work"],
            "I_lat": static["work"]["I_lat"],
            "I_long": static["work"]["I_long"],
            "total_mass": CG_data["work"]["mass_total"],
            "machine_mass": machine.get("mass", 0),
            "tractor_mass": tractor.get("mass", 0),
            "ptac": tractor.get("ptac", None)
        })

        result["compatibility"] = compat

    except Exception as e:
        print("\n[ERREUR COMPATIBILITE] :", e)
        result["compatibility"] = []

    return result

