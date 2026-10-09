# Predictive Maintenance System

Cloud-native distributed predictive maintenance platform using machine learning. Two-stage ML pipeline for real-time failure detection and failure-type classification with a FastAPI backend and React dashboard.

## Overview

This project implements a scalable predictive maintenance solution for industrial machines. Sensor telemetry is ingested, processed through a trained two-stage model, and visualized in real-time.

**Key features**
* Two-stage ML: binary failure detection → failure type classification
* FastAPI microservice with Docker support
* React + Tailwind dashboard with live probability streaming
* Sensor simulator for testing
* Kubernetes manifests for deployment

## Architecture

```
Sensors → React UI / Simulator → FastAPI /predict → RandomForest Binary → Threshold 0.35 → RandomForest Multi-class → Dashboard
```

## Tech Stack

* **Backend:** Python 3.10, FastAPI, Uvicorn, scikit-learn, joblib
* **Frontend:** React 19, TailwindCSS, Framer Motion, Recharts
* **ML:** RandomForestClassifier, LabelEncoder, SMOTE
* **Infra:** Docker, Docker Compose, Kubernetes
* **Data:** AI4I 2020 Predictive Maintenance dataset

## Project Structure

```
.
├── predictive_maintenance_api/   # FastAPI service
│   ├── main.py
│   ├── simulator.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── predictive-ui/                # React dashboard
│   ├── src/
│   ├── package.json
│   └── ...
├── notebooks/                    # Training & experimentation
│   ├── preprossing.py
│   ├── preprossing.ipynb
│   └── testing.ipynb
├── data/                         # Datasets, ignored in git
├── docs/                         # Project documentation
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
* Python 3.10+
* Node 18+
* Docker

### Quick start
```bash
# 1. Train models - generates predictive_maintenance_api/models/
make train
# or
python scripts/train_models.py

# 2. Run API
make api
# or
cd predictive_maintenance_api && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# 3. Run UI
make ui
# or
cd predictive-ui && cp .env.example .env && npm install && npm start
```

API docs: http://localhost:8000/docs
UI runs at http://localhost:3000. Set `REACT_APP_API_URL` in `predictive-ui/.env`.

### Docker Compose
```bash
docker-compose up --build
```

## API Usage

**POST /predict**
```json
{
  "type": "H",
  "air_temp": 300.0,
  "process_temp": 310.0,
  "rotational_speed": 1500,
  "torque": 40.0,
  "tool_wear": 50
}
```

Response:
```json
{
  "Failure": true,
  "Failure Probability": 0.72,
  "Failure Type": "Heat Dissipation Failure"
}
```

## Model Training

Training notebooks are in `notebooks/`. Models are serialized with joblib and loaded at runtime. See `predictive_maintenance_api/README.md` for details.

## Deployment

Kubernetes manifests:
* `predictive-ui/deployment.yaml`
* `predictive-ui/service.yaml`

## Security & Best Practices

* Secrets and private keys are excluded via `.gitignore`
* API URLs should be configured via environment variables
* Model artifacts are ignored; load from secure storage in production
* CORS is permissive in dev only

## License

Private project. Internal use only.

## Authors

Project developed for cloud-native distributed predictive maintenance research.
