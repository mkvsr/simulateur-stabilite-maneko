import numpy as np

def classify(value, limit, type="min"):
    """
    type = "min"  -> value must be >= limit
    type = "max"  -> value must be <= limit
    """

    if type == "min":
        if value < limit:
            return "⛔ Danger"
        elif value < limit * 1.1:
            return "⚠️ Avertissement"
        else:
            return "✅ OK"

    if type == "max":
        if value > limit:
            return "⛔ Danger"
        elif value > limit * 0.90:
            return "⚠️ Avertissement"
        else:
            return "✅ OK"


def check_compatibility(data):
    """
    data = {
        "wheels": {FL, FR, RL, RR},
        "I_lat": float,
        "I_long": float,
        "total_mass": float,
        "machine_mass": float,
        "tractor_mass": float
    }
    """

    FL = data["wheels"]["FL"]
    FR = data["wheels"]["FR"]
    RL = data["wheels"]["RL"]
    RR = data["wheels"]["RR"]
    total = data["total_mass"]
    I_lat = data["I_lat"]
    I_long = data["I_long"]

    results = []

    # -------------------------------------------------------------------
    # 1. Stabilité latérale (ISO 16231 + étude MDPI 2021)
    # -------------------------------------------------------------------
    limit_lat = 0.40
    status_lat = classify(I_lat, limit_lat, "min")
    results.append({
        "name": "Stabilité latérale ≥ 40%",
        "value": I_lat,
        "limit": limit_lat,
        "status": status_lat,
        #"source": "ISO 16231-2 / Appl. Sci. 2021 (Static Lateral Stability)"
    })

    # -------------------------------------------------------------------
    # 2. Stabilité longitudinale (ISO + recommandations sécurité)
    # -------------------------------------------------------------------
    limit_long = 0.50
    status_long = classify(I_long, limit_long, "min")
    results.append({
        "name": "Stabilité longitudinale ≥ 50%",
        "value": I_long,
        "limit": limit_long,
        "status": status_long,
        #"source": "ISO 16231 / Guides sécurité tracteur"
    })

    # -------------------------------------------------------------------
    # 3. Charge essieu avant ≥ 20% (constructeurs + OSHA + MSA)
    # -------------------------------------------------------------------
    front_load_ratio = (FL + FR) / total
    limit_front_ratio = 0.20

    status_front_ratio = classify(front_load_ratio, limit_front_ratio, "min")
    results.append({
        "name": "Charge en kg essieu avant ≥ 20 %",
        "value": front_load_ratio,
        "limit": limit_front_ratio,
        "status": status_front_ratio,
        #"source": "John Deere / CNH / Fendt / OSHA / MSA"
    })

    # -------------------------------------------------------------------
    # 4. Roue avant ou arrière délestée interdite
    # -------------------------------------------------------------------
    if FL <= 0 or FR <= 0:
        status = "⛔ Danger"
    else:
        status = "✅ OK"
    results.append({
        "name": "Aucune roue avant délestée",
        "value": min(FL, FR),
        "limit": 0,
        "status": status,
        #"source": "INRS / OSHA / MSA / JD"
    })
        
    if RL <= 0 or RR <= 0:
        status = "⛔ Danger"
    else:
        status = "✅ OK"
    results.append({
        "name": "Aucune roue arrière délestée",
        "value": min(RL, RR),
        "limit": 0,
        "status": status,
        #"source": "INRS / OSHA / MSA / JD"
    })

    # -------------------------------------------------------------------
    # 5. Charge roue avant ≤ 40 % total (NOUVEAU — DEMANDE UTILISATEUR)
    # -------------------------------------------------------------------
    limit_front_wheel_max = 0.40 * total

    status_FL = classify(FL, limit_front_wheel_max, "max")
    results.append({
        "name": "Charge roue avant gauche ≤ 40% charge total",
        "value": FL,
        "limit": limit_front_wheel_max,
        "status": status_FL,
        #"source": "Constructeurs / sécurité direction / surcharge essieu"
    })

    status_FR = classify(FR, limit_front_wheel_max, "max")
    results.append({
        "name": "Charge roue avant droite ≤ 40% charge total",
        "value": FR,
        "limit": limit_front_wheel_max,
        "status": status_FR,
        #"source": "Constructeurs / sécurité direction / surcharge essieu"
    })

    # -------------------------------------------------------------------
    # 6. Charge roue arrière ≤ 40 % total
    # -------------------------------------------------------------------
    limit_rear_wheel_max = 0.40 * total

    status_RL = classify(RL, limit_rear_wheel_max, "max")
    results.append({
        "name": "Charge roue arrière gauche ≤ 40% charge total",
        "value": RL,
        "limit": limit_rear_wheel_max,
        "status": status_RL,
        #"source": "ISO 16231 (projection CG) + études stabilité"
    })

    status_RR = classify(RR, limit_rear_wheel_max, "max")
    results.append({
        "name": "Charge roue arrière droite ≤ 40% charge total",
        "value": RR,
        "limit": limit_rear_wheel_max,
        "status": status_RR,
        #"source": "ISO 16231 (projection CG) + études stabilité"
    })

    # -------------------------------------------------------------------
    # 7. Rapport masse machine / tracteur ≤ 1.5
    # -------------------------------------------------------------------
    ratio = data["machine_mass"] / data["tractor_mass"]
    limit_ratio = 1.5
    status_ratio = classify(ratio, limit_ratio, "max")

    results.append({
        "name": "Masse machine ≤ 1.5 × masse tracteur",
        "value": ratio,
        "limit": limit_ratio,
        "status": status_ratio,
        #"source": "Constructeurs (Claas, MF, CNH)"
    })

    # -------------------------------------------------------------------
    # 8. PTAC — Poids Total Autorisé en Charge
    # -------------------------------------------------------------------
    ptac = data.get("ptac", None)
    if ptac is not None:
        status_ptac = classify(total, ptac, "max")
        results.append({
            "name": "Masse totale ≤ PTAC constructeur",
            "value": total,
            "limit": ptac,
            "status": status_ptac
        })

    return results



