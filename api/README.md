# API — Simulateur de stabilité tracteur

## Lancer en local

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload
```

L'API est disponible sur `http://localhost:8000`  
La documentation interactive est sur `http://localhost:8000/docs`

## Endpoints

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/` | Health check |
| GET | `/tractors` | Liste des tracteurs |
| GET | `/tractors/{key}` | Données d'un tracteur |
| GET | `/machines` | Liste des machines |
| GET | `/machines/{key}` | Données d'une machine |
| GET | `/tires` | Liste des pneus |
| POST | `/simulate` | Lancer une simulation |

## Exemple de requête simulation

```json
POST /simulate
{
  "tractor_name": "Valtra_SERIE_N",
  "machine_name": "magistra_m60",
  "options": {
    "rear_tire": "520/85R38",
    "loader_enabled": false,
    "loader_mode": "low",
    "water_ballast": false,
    "wheel_weight_ARG": 0,
    "wheel_weight_ARD": 0,
    "front_ballast_mass": 0,
    "front_ballast_offset": 0.5,
    "rear_ballast_mass": 0,
    "rear_ballast_offset": 0.3
  },
  "environment": {
    "slope_lat": 0,
    "slope_long": 0,
    "speed": 0,
    "turn_radius": 0,
    "accel_long": 0
  }
}
```

## Déploiement sur Render

1. Connecte ton dépôt GitHub à Render
2. Crée un nouveau **Web Service**
3. Paramètres :
   - **Build command** : `pip install -r api/requirements.txt`
   - **Start command** : `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. Déploie — c'est tout
