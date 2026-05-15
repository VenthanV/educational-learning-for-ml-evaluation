import json
import os

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_curve,
)

app = FastAPI(title="Cybersecurity ML Evaluator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # -> backend/app
BACKEND_DIR = os.path.dirname(CURRENT_DIR)  # -> backend
ROOT_DIR = os.path.dirname(BACKEND_DIR)  # -> Dein Hauptordner
DATA_DIR = os.path.join(ROOT_DIR, "data")  # -> Dein 'data' Ordner

scenarios_db = {}


def load_data():
    print(f"Lade Daten aus: {DATA_DIR}")

    config_path = os.path.join(DATA_DIR, "scenario_configs.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    for s_id, meta in config.items():
        csv_path = os.path.join(DATA_DIR, meta["file_path"])
        df = pd.read_csv(csv_path)

        y_true = df["y_true"].values
        y_prob = df["y_prob"].values

        fpr, tpr, _ = roc_curve(y_true, y_prob)
        prec_curve, rec_curve, _ = precision_recall_curve(y_true, y_prob)

        # In die Datenbank im Arbeitsspeicher laden
        scenarios_db[s_id] = {
            "title": meta["title"],
            "description": meta["description"],
            "y_true": y_true.tolist(),
            "y_prob": y_prob.tolist(),
            "roc_curve": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
            "pr_curve": {
                "precision": prec_curve.tolist(),
                "recall": rec_curve.tolist(),
            },
        }


load_data()


class EvaluationRequest(BaseModel):
    scenario_id: str
    threshold: float


# --- ENDPUNKTE ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend läuft und CSVs sind geladen!"}


@app.get("/api/scenarios")
def get_scenarios():
    """Wird vom Svelte-Frontend beim Start der Webseite aufgerufen"""
    return scenarios_db


@app.post("/api/evaluate")
def evaluate(req: EvaluationRequest):
    """Wird aufgerufen, wann immer du den Slider in Svelte bewegst"""
    if req.scenario_id not in scenarios_db:
        return {"error": "Szenario nicht gefunden"}

    data = scenarios_db[req.scenario_id]
    y_true = data["y_true"]
    y_prob = data["y_prob"]

    # Vorhersagen machen (Threshold anwenden)
    y_pred = [1 if p >= req.threshold else 0 for p in y_prob]

    # Metriken berechnen
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    return {
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
        },
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
    }
