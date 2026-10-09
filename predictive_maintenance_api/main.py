from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import joblib
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

def load_artifacts():
    try:
        binary_model = joblib.load(MODEL_DIR / "binary_failure_model.pkl")
        failure_type_model = joblib.load(MODEL_DIR / "failure_type_model.pkl")
        le_failure = joblib.load(MODEL_DIR / "failure_type_encoder.pkl")
        le_type = joblib.load(MODEL_DIR / "type_encoder.pkl")
        BEST_THRESHOLD = float(joblib.load(MODEL_DIR / "best_threshold.pkl"))
        return binary_model, failure_type_model, le_failure, le_type, BEST_THRESHOLD
    except FileNotFoundError as e:
        raise RuntimeError(f"Model artifacts missing in {MODEL_DIR}. Run scripts/train_models.py first.") from e

binary_model, failure_type_model, le_failure, le_type, BEST_THRESHOLD = load_artifacts()

app = FastAPI(title="Predictive Maintenance API")

# --- ENABLE CORS ---
# This allows your React UI to talk to this API without being blocked
import os
 origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input schema
class MachineInput(BaseModel):
    type: str
    air_temp: float
    process_temp: float
    rotational_speed: float
    torque: float
    tool_wear: float

@app.get("/")
def home():
    return {"message": "Predictive Maintenance API is running"}

@app.post("/predict")
def predict(data: MachineInput):
    # Validate type value
    if data.type not in ["L", "M", "H"]:
        raise ValueError("type must be one of L, M, H")
    try:
        type_encoded = le_type.transform([data.type])[0]
    except Exception:
        raise ValueError("Invalid machine type")

    sample = np.array([[type_encoded,
                        data.air_temp,
                        data.process_temp,
                        data.rotational_speed,
                        data.torque,
                        data.tool_wear]])

    # Stage 1: Binary Prediction (Failure or No Failure)
    prob = float(binary_model.predict_proba(sample)[:,1][0])

    if prob > BEST_THRESHOLD:
        # Stage 2: Multi-class Prediction (What kind of failure?)
        failure_type_encoded = failure_type_model.predict(sample)
        failure_type = le_failure.inverse_transform(failure_type_encoded)[0]

        return {
            "Failure": True,
            "Failure Probability": float(prob),
            "Failure Type": failure_type
        }
    else:
        return {
            "Failure": False,
            "Failure Probability": float(prob),
            "Failure Type": "No Failure"
        }