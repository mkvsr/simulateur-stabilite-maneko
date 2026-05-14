"""
models.py — Structures de données entrée/sortie de l'API
---------------------------------------------------------

Définit les schémas Pydantic pour :
- SimulationRequest  : ce que l'interface envoie
- SimulationResponse : ce que l'API renvoie
"""

from pydantic import BaseModel, Field
from typing import Optional


# -----------------------------------------------------------
# ENTRÉE
# -----------------------------------------------------------

class OptionsInput(BaseModel):
    rear_tire: str                          = Field(..., description="Référence pneu arrière (ex: '520/85R38')")
    loader_enabled: bool                    = Field(False, description="Chargeur frontal activé")
    loader_mode: str                        = Field("low", description="Position chargeur : 'low' ou 'high'")
    water_ballast: bool                     = Field(False, description="Lestage à l'eau activé")
    wheel_weight_ARG: float                 = Field(0.0, description="Masse roue arrière gauche (kg)")
    wheel_weight_ARD: float                 = Field(0.0, description="Masse roue arrière droite (kg)")
    front_ballast_mass: float               = Field(0.0, description="Masse avant (kg)")
    front_ballast_offset: float             = Field(0.5, description="Offset masse avant / essieu AV (m)")
    rear_ballast_mass: float                = Field(0.0, description="Masse arrière (kg)")
    rear_ballast_offset: float              = Field(0.3, description="Offset masse arrière / essieu AR (m)")


class EnvironmentInput(BaseModel):
    slope_lat: float                        = Field(0.0, description="Pente latérale (degrés)")
    slope_long: float                       = Field(0.0, description="Pente longitudinale (degrés)")
    speed: float                            = Field(0.0, description="Vitesse (m/s)")
    turn_radius: float                      = Field(0.0, description="Rayon de virage (m)")
    accel_long: float                       = Field(0.0, description="Accélération longitudinale (m/s²)")


class SimulationRequest(BaseModel):
    tractor_name: str                       = Field(..., description="Nom du fichier tracteur (ex: 'Valtra_SERIE_N')")
    machine_name: str                       = Field(..., description="Nom du fichier machine (ex: 'magistra_m60')")
    options: OptionsInput
    environment: EnvironmentInput           = Field(default_factory=EnvironmentInput)


# -----------------------------------------------------------
# SORTIE
# -----------------------------------------------------------

class CGResult(BaseModel):
    X: float
    Y: float
    Z: float


class CGModeResult(BaseModel):
    mass_total: float
    CG: CGResult


class WheelLoads(BaseModel):
    FL: float
    FR: float
    RL: float
    RR: float


class StaticResult(BaseModel):
    I_lat: float
    I_long: float
    I_static: float
    risk_direction: str


class DynamicResult(BaseModel):
    I_lat_dyn: float
    I_long_dyn: float
    I_dynamic: float


class CriterionResult(BaseModel):
    name: str
    status: str
    value: float


class SimulationResponse(BaseModel):
    # CG global
    transport: CGModeResult
    work: CGModeResult

    # Charges aux roues
    wheels_transport: WheelLoads
    wheels_work: WheelLoads

    # Stabilité statique
    static_transport: StaticResult
    static_work: StaticResult

    # Stabilité dynamique
    dynamic_transport: DynamicResult
    dynamic_work: DynamicResult

    # Critères de sécurité
    compatibility: list[CriterionResult]
