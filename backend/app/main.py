from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Educational app for machine learning")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # für svelte später
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModelRequest(BaseModel):
    y_true: list[int]
    y_pred: list[int]


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend läuft einwandfrei!"}


@app.post("/api/metrics")
def calculate_metrics(data: ModelRequest):
    return {
        "accuracy": 0.95,
        "precision": 0.82,
        "recall": 0.99,
        "received_data_points": len(data.y_true),
    }
