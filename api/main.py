"""
main.py — API FastAPI du simulateur de stabilité
-------------------------------------------------

Endpoints :
    GET  /                      → health check
    GET  /tractors              → liste des tracteurs disponibles
    GET  /machines              → liste des machines disponibles
    GET  /tires                 → liste des pneus disponibles
    GET  /tractors/{name}       → données complètes d'un tracteur
    POST /simulate              → lancer une simulation complète

Usage :
    uvicorn api.main:app --reload
"""

import os
import sys
import json
import glob
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# --- Résolution des chemins ---
# L'API est dans api/, le solver est à la racine
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from solver_v19.solver import solve
from .models import (
    SimulationRequest, SimulationResponse,
    CGModeResult, CGResult, WheelLoads,
    StaticResult, DynamicResult, CriterionResult
)

# -----------------------------------------------------------
# Application
# -----------------------------------------------------------

app = FastAPI(
    title="Simulateur de stabilité tracteur",
    description="API de calcul de stabilité pour tracteurs et équipements",
    version="20.0"
)

# CORS — autorise l'interface React à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # en prod, remplacer par l'URL exacte du front
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# Chargement des données JSON au démarrage
# -----------------------------------------------------------

DATA_DIR      = ROOT / "data"
TRACTORS_DIR  = ROOT / "tractors"
MACHINES_DIR  = ROOT / "machines"
LOADERS_DIR   = ROOT / "loaders"

def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_all(directory: Path) -> dict:
    """Charge tous les JSON d'un dossier. Clé = nom de fichier sans extension."""
    result = {}
    for f in sorted(directory.glob("*.json")):
        result[f.stem] = load_json(f)
    return result

# Chargement au démarrage
TIRES    = load_json(DATA_DIR / "tires.json")
TRACTORS = load_all(TRACTORS_DIR)
MACHINES = load_all(MACHINES_DIR)
LOADERS  = load_all(LOADERS_DIR)


# -----------------------------------------------------------
# Endpoints catalogue
# -----------------------------------------------------------

@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "version": "20.0"}


@app.get("/tractors", tags=["Catalogue"])
def get_tractors():
    """Retourne la liste des tracteurs disponibles avec leurs infos principales."""
    result = []
    for key, t in TRACTORS.items():
        result.append({
            "key":            key,
            "name":           t.get("name"),
            "brand":          t.get("brand"),
            "model":          t.get("model"),
            "mass":           t.get("mass"),
            "mass_front_pct": t.get("mass_front_pct"),
            "mass_rear_pct":  t.get("mass_rear_pct"),
            "ptac":           t.get("ptac"),
            "wheelbase":      t.get("geometry", {}).get("wheelbase"),
            "track_front":    t.get("geometry", {}).get("track_front"),
            "track_rear":     t.get("geometry", {}).get("track_rear"),
            "tire_defaults":  t.get("tire_defaults"),
            "dynamics":       t.get("dynamics"),
        })
    return result


@app.get("/tractors/{key}", tags=["Catalogue"])
def get_tractor(key: str):
    """Retourne les données complètes d'un tracteur."""
    if key not in TRACTORS:
        raise HTTPException(status_code=404, detail=f"Tracteur '{key}' introuvable")
    return TRACTORS[key]


@app.get("/machines", tags=["Catalogue"])
def get_machines():
    """Retourne la liste des machines disponibles."""
    result = []
    for key, m in MACHINES.items():
        result.append({
            "key":   key,
            "model": m.get("model"),
            "mass":  m.get("mass"),
        })
    return result


@app.get("/machines/{key}", tags=["Catalogue"])
def get_machine(key: str):
    """Retourne les données complètes d'une machine."""
    if key not in MACHINES:
        raise HTTPException(status_code=404, detail=f"Machine '{key}' introuvable")
    return MACHINES[key]


@app.get("/tires", tags=["Catalogue"])
def get_tires():
    """Retourne la liste des pneus disponibles."""
    return [
        {"reference": k, "diameter_mm": v.get("diameter_mm"), "volume_l": v.get("volume_l")}
        for k, v in TIRES.items()
    ]


# -----------------------------------------------------------
# Endpoint simulation
# -----------------------------------------------------------

@app.post("/simulate", response_model=SimulationResponse, tags=["Simulation"])
def simulate(request: SimulationRequest):
    """
    Lance une simulation complète.

    Corps de la requête : SimulationRequest
    Retourne           : SimulationResponse
    """

    # --- Validation des clés ---
    if request.tractor_name not in TRACTORS:
        raise HTTPException(status_code=404, detail=f"Tracteur '{request.tractor_name}' introuvable")

    if request.machine_name not in MACHINES:
        raise HTTPException(status_code=404, detail=f"Machine '{request.machine_name}' introuvable")

    tractor = TRACTORS[request.tractor_name]
    machine = MACHINES[request.machine_name]

    # --- Sélection du chargeur (automatique par masse tracteur) ---
    loader = None
    if request.options.loader_enabled:
        from solver_v19.loader import get_loader_category
        loader_key = get_loader_category(tractor["mass"])
        loader = LOADERS.get(loader_key)

    # --- Construction des options ---
    options = request.options.model_dump()

    # --- Construction de l'environnement ---
    env = request.environment.model_dump()

    # --- Appel du solver ---
    try:
        result = solve(tractor, machine, loader, TIRES, options, env)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur solver : {str(e)}")

    # --- Formatage de la réponse ---
    def fmt_cg(mode: str) -> CGModeResult:
        block = result["CG"][mode]
        cg = block["CG_local"]
        return CGModeResult(
            mass_total=round(block["mass_total"], 2),
            CG=CGResult(X=round(cg[0], 4), Y=round(cg[1], 4), Z=round(cg[2], 4))
        )

    def fmt_wheels(mode: str) -> WheelLoads:
        w = result["wheels"][mode]
        return WheelLoads(
            FL=round(w["FL"], 1),
            FR=round(w["FR"], 1),
            RL=round(w["RL"], 1),
            RR=round(w["RR"], 1),
        )

    def fmt_static(mode: str) -> StaticResult:
        s = result["static"][mode]
        return StaticResult(
            I_lat=round(s["I_lat"], 4),
            I_long=round(s["I_long"], 4),
            I_static=round(s["I_static"], 4),
            risk_direction=s["risk_direction"],
        )

    def fmt_dynamic(mode: str) -> DynamicResult:
        d = result["dynamic"][mode]
        return DynamicResult(
            I_lat_dyn=round(d["I_lat_dyn"], 4),
            I_long_dyn=round(d["I_long_dyn"], 4),
            I_dynamic=round(d["I_dynamic"], 4),
        )

    compatibility = [
        CriterionResult(
            name=c["name"],
            status=c["status"],
            value=round(c["value"], 4)
        )
        for c in result["compatibility"]
    ]

    return SimulationResponse(
        transport=fmt_cg("transport"),
        work=fmt_cg("work"),
        wheels_transport=fmt_wheels("transport"),
        wheels_work=fmt_wheels("work"),
        static_transport=fmt_static("transport"),
        static_work=fmt_static("work"),
        dynamic_transport=fmt_dynamic("transport"),
        dynamic_work=fmt_dynamic("work"),
        compatibility=compatibility,
    )
