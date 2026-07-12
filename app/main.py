from fastapi import FastAPI, HTTPException

from app.models import BirthData
from app.astrology.chart_engine import (
    VedicChartEngine,
)


app = FastAPI(
    title="Jyotish AI Backend",
    description=(
        "Deterministic Vedic astrology calculation "
        "engine with separate divisional chart APIs."
    ),
    version="0.2.0",
)


engine = VedicChartEngine()


# =============================================================
# ROOT
# =============================================================


@app.get("/")
def root():

    return {
        "name": (
            "Jyotish AI Backend"
        ),

        "status": (
            "running"
        ),

        "version": (
            "0.2.0"
        ),
    }


# =============================================================
# HEALTH
# =============================================================


@app.get("/health")
def health():

    return {
        "status": (
            "healthy"
        ),
    }


# =============================================================
# SUPPORTED CHARTS
# =============================================================


@app.get(
    "/api/v1/charts"
)
def supported_charts():

    return {
        "charts": (
            engine.get_supported_charts()
        )
    }


# =============================================================
# D1 - RASHI
# =============================================================


@app.post(
    "/api/v1/chart/d1"
)
def calculate_d1(
    birth: BirthData,
):

    return engine.calculate_d1(
        birth
    )


# =============================================================
# D2 - HORA
# =============================================================


@app.post(
    "/api/v1/chart/d2"
)
def calculate_d2(
    birth: BirthData,
):

    return engine.calculate_d2(
        birth
    )


# =============================================================
# D3 - DREKKANA
# =============================================================


@app.post(
    "/api/v1/chart/d3"
)
def calculate_d3(
    birth: BirthData,
):

    return engine.calculate_d3(
        birth
    )


# =============================================================
# D4 - CHATURTHAMSHA
# =============================================================


@app.post(
    "/api/v1/chart/d4"
)
def calculate_d4(
    birth: BirthData,
):

    return engine.calculate_d4(
        birth
    )


# =============================================================
# D7 - SAPTAMSHA
# =============================================================


@app.post(
    "/api/v1/chart/d7"
)
def calculate_d7(
    birth: BirthData,
):

    return engine.calculate_d7(
        birth
    )


# =============================================================
# D9 - NAVAMSHA
# =============================================================


@app.post(
    "/api/v1/chart/d9"
)
def calculate_d9(
    birth: BirthData,
):

    return engine.calculate_d9(
        birth
    )


# =============================================================
# D10 - DASHAMSHA
# =============================================================


@app.post(
    "/api/v1/chart/d10"
)
def calculate_d10(
    birth: BirthData,
):

    return engine.calculate_d10(
        birth
    )


# =============================================================
# D12 - DWADASHAMSHA
# =============================================================


@app.post(
    "/api/v1/chart/d12"
)
def calculate_d12(
    birth: BirthData,
):

    return engine.calculate_d12(
        birth
    )


# =============================================================
# ALL CURRENTLY SUPPORTED CHARTS
# =============================================================


@app.post(
    "/api/v1/chart/all"
)
def calculate_all_charts(
    birth: BirthData,
):

    return (
        engine.calculate_all_charts(
            birth
        )
    )


# =============================================================
# GENERIC SINGLE-CHART ENDPOINT
# =============================================================


@app.post(
    "/api/v1/chart/{division}"
)
def calculate_chart_by_division(
    division: int,
    birth: BirthData,
):
    """
    Generic endpoint.

    Examples:

        POST /api/v1/chart/9
        POST /api/v1/chart/10

    Useful internally and for future Vargas.
    """

    try:

        return (
            engine.calculate_varga_chart(
                birth=birth,
                division=division,
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(
                error
            ),
        )


# =============================================================
# LEGACY ENDPOINT
# =============================================================


@app.post(
    "/api/v1/chart"
)
def calculate_chart_legacy(
    birth: BirthData,
):
    """
    Legacy endpoint.

    Kept temporarily so existing frontend/tests do not break.
    """

    return (
        engine.calculate_chart(
            birth
        )
    )