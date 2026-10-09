# Predictive Maintenance API

FastAPI microservice for two-stage predictive maintenance inference.

## Features
* `GET /` health check
* `POST /predict` – binary failure detection with failure type classification

## Request Schema
```json
{
  "type": "L|M|H",
  "air_temp": float,
  "process_temp": float,
  "rotational_speed": float,
  "torque": float,
  "tool_wear": float
}
```

## Response Schema
```json
{
  "Failure": boolean,
  "Failure Probability": float,
  "Failure Type": string
}
```

## Local Development
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Docker
```bash
docker build -t predictive-maintenance-api .
docker run -p 8000:8000 predictive-maintenance-api
```

## Model Artifacts
Models are loaded from `*.pkl` files. They are excluded from git. Place them in the container image or mount volume in production.

## Simulator
```bash
python simulator.py
```
Streams synthetic sensor data to `/predict` every 3 seconds.

## Environment Variables
* `API_URL` – target API for simulator
* `MODEL_PATH` – path to model artifacts

## Testing
Run `../notebooks/testing.ipynb` for inference sanity checks.
