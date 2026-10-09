#!/usr/bin/env python3
"""
Train two-stage predictive maintenance models.
Usage:
    python scripts/train_models.py
Saves models to predictive_maintenance_api/models/
Requires data/dataset.csv
"""
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "dataset.csv"
MODEL_DIR = ROOT / "predictive_maintenance_api" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("Loading data from", DATA_PATH)
df = pd.read_csv(DATA_PATH)

# Drop unwanted columns
df = df.drop(columns=['UDI', 'Product ID'], errors='ignore')

# Encode Type
le_type = LabelEncoder()
df['Type'] = le_type.fit_transform(df['Type'])

# Binary model
X = df.drop(columns=['Target', 'Failure Type'])
y = df['Target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

binary_model = RandomForestClassifier(
    n_estimators=300,
    class_weight={0:1, 1:5},
    random_state=42,
    n_jobs=-1
)
binary_model.fit(X_train, y_train)

y_prob = binary_model.predict_proba(X_test)[:,1]
best_threshold = 0.35
y_pred_custom = (y_prob > best_threshold).astype(int)

print("\nBinary model accuracy @ threshold", best_threshold)
print(accuracy_score(y_test, y_pred_custom))
print(classification_report(y_test, y_pred_custom))

# Failure type model
df_failures = df[df['Target'] == 1].copy()
df_failures = df_failures[df_failures['Failure Type'] != 'No Failure']
le_failure = LabelEncoder()
df_failures['Failure Type'] = le_failure.fit_transform(df_failures['Failure Type'])

X2 = df_failures.drop(columns=['Failure Type', 'Target'])
y2 = df_failures['Failure Type']

X2_train, X2_test, y2_train, y2_test = train_test_split(
    X2, y2, test_size=0.2, stratify=y2, random_state=42
)

failure_type_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)
failure_type_model.fit(X2_train, y2_train)

y2_pred = failure_type_model.predict(X2_test)
print("\nFailure type model accuracy")
print(accuracy_score(y2_test, y2_pred))
print(classification_report(y2_test, y2_pred))

# Save artifacts
joblib.dump(binary_model, MODEL_DIR / "binary_failure_model.pkl")
joblib.dump(failure_type_model, MODEL_DIR / "failure_type_model.pkl")
joblib.dump(le_failure, MODEL_DIR / "failure_type_encoder.pkl")
joblib.dump(le_type, MODEL_DIR / "type_encoder.pkl")
joblib.dump(best_threshold, MODEL_DIR / "best_threshold.pkl")

print("\nModels saved to", MODEL_DIR)
print("Done.")
