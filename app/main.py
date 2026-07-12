from fastapi import FastAPI

from app.models import BirthData
from app.astrology.chart_engine import VedicChartEngine


app = FastAPI(
    title="Jyotish AI Backend",
    description=(
        "Deterministic Vedic astrology calculation "
        "engine with AI interpretation."
    ),
    version="0.1.0",
)


engine = VedicChartEngine()


@app.get("/")
def root():
    return {
        "name": "Jyotish AI Backend",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/api/v1/chart")
def calculate_chart(
    birth: BirthData,
):
    return engine.calculate_chart(birth)