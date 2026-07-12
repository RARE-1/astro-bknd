from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status

from app.models import BirthData
from app.astrology.chart_engine import VedicChartEngine


app = FastAPI(
    title="Jyotish AI Backend",
    description=(
        "Deterministic Vedic astrology calculation "
        "engine with reusable chart sessions and "
        "separate divisional chart APIs."
    ),
    version="0.3.0",
)


engine = VedicChartEngine()


# =============================================================
# TEMPORARY IN-MEMORY CHART SESSION STORE
# =============================================================
#
# For development:
#
# {
#     UUID: BirthData
# }
#
# IMPORTANT:
# This data is lost whenever the server restarts.
#
# Later we can replace this with:
# - Redis
# - PostgreSQL
# - MongoDB
#
# without changing the frontend API structure.
# =============================================================


chart_sessions: dict[UUID, BirthData] = {}


# =============================================================
# HELPER - GET SESSION
# =============================================================


def get_birth_data(
    chart_id: UUID,
) -> BirthData:
    """
    Return BirthData for an existing chart session.

    Raises 404 if the chart session does not exist.
    """

    birth = chart_sessions.get(
        chart_id
    )

    if birth is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Chart session not found."
            ),
        )

    return birth


# =============================================================
# HELPER - GET CHART
# =============================================================


def get_chart_for_session(
    chart_id: UUID,
    division: int,
):
    """
    Resolve the chart session and calculate
    one requested divisional chart.
    """

    birth = get_birth_data(
        chart_id
    )

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
            "0.3.0"
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
# CREATE CHART SESSION
# =============================================================


@app.post(
    "/api/v1/chart-sessions",
    status_code=status.HTTP_201_CREATED,
)
def create_chart_session(
    birth: BirthData,
):
    """
    Create a reusable chart session.

    The client sends birth details only once.

    After this, use the returned chart_id
    to request individual charts with GET.
    """

    chart_id = uuid4()

    chart_sessions[
        chart_id
    ] = birth

    return {
        "chart_id": str(
            chart_id
        ),

        "message": (
            "Chart session created successfully."
        ),

        "available_charts": [
            chart["code"].lower()
            for chart
            in engine.get_supported_charts()
        ],
    }


# =============================================================
# GET CHART SESSION INFO
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}"
)
def get_chart_session(
    chart_id: UUID,
):

    birth = get_birth_data(
        chart_id
    )

    return {
        "chart_id": str(
            chart_id
        ),

        "birth": (
            birth.model_dump(
                mode="json"
            )
        ),

        "available_charts": (
            engine.get_supported_charts()
        ),
    }


# =============================================================
# DELETE CHART SESSION
# =============================================================


@app.delete(
    "/api/v1/chart-sessions/{chart_id}"
)
def delete_chart_session(
    chart_id: UUID,
):

    get_birth_data(
        chart_id
    )

    del chart_sessions[
        chart_id
    ]

    return {
        "chart_id": str(
            chart_id
        ),

        "message": (
            "Chart session deleted successfully."
        ),
    }


# =============================================================
# D1 - RASHI
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/d1"
)
def get_d1(
    chart_id: UUID,
):

    return get_chart_for_session(
        chart_id=chart_id,
        division=1,
    )


# =============================================================
# D2 - HORA
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/d2"
)
def get_d2(
    chart_id: UUID,
):

    return get_chart_for_session(
        chart_id=chart_id,
        division=2,
    )


# =============================================================
# D3 - DREKKANA
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/d3"
)
def get_d3(
    chart_id: UUID,
):

    return get_chart_for_session(
        chart_id=chart_id,
        division=3,
    )


# =============================================================
# D4 - CHATURTHAMSHA
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/d4"
)
def get_d4(
    chart_id: UUID,
):

    return get_chart_for_session(
        chart_id=chart_id,
        division=4,
    )


# =============================================================
# D7 - SAPTAMSHA
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/d7"
)
def get_d7(
    chart_id: UUID,
):

    return get_chart_for_session(
        chart_id=chart_id,
        division=7,
    )


# =============================================================
# D9 - NAVAMSHA
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/d9"
)
def get_d9(
    chart_id: UUID,
):

    return get_chart_for_session(
        chart_id=chart_id,
        division=9,
    )


# =============================================================
# D10 - DASHAMSHA
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/d10"
)
def get_d10(
    chart_id: UUID,
):

    return get_chart_for_session(
        chart_id=chart_id,
        division=10,
    )


# =============================================================
# D12 - DWADASHAMSHA
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/d12"
)
def get_d12(
    chart_id: UUID,
):

    return get_chart_for_session(
        chart_id=chart_id,
        division=12,
    )


# =============================================================
# GENERIC GET CHART ENDPOINT
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/charts/{division}"
)
def get_chart_by_division(
    chart_id: UUID,
    division: int,
):
    """
    Generic endpoint.

    Examples:

        GET /api/v1/chart-sessions/{chart_id}/charts/9

        GET /api/v1/chart-sessions/{chart_id}/charts/10
    """

    return get_chart_for_session(
        chart_id=chart_id,
        division=division,
    )


# =============================================================
# ALL CURRENTLY SUPPORTED CHARTS
# =============================================================


@app.get(
    "/api/v1/chart-sessions/{chart_id}/all"
)
def get_all_charts(
    chart_id: UUID,
):

    birth = get_birth_data(
        chart_id
    )

    return (
        engine.calculate_all_charts(
            birth
        )
    )


# =============================================================
# LEGACY POST ENDPOINTS
# =============================================================
#
# Keep these temporarily.
#
# This prevents existing tests or any existing frontend code
# from breaking while we migrate to chart sessions.
# =============================================================


# @app.post(
#     "/api/v1/chart/d1"
# )
# def calculate_d1(
#     birth: BirthData,
# ):

#     return engine.calculate_d1(
#         birth
#     )


# @app.post(
#     "/api/v1/chart/d2"
# )
# def calculate_d2(
#     birth: BirthData,
# ):

#     return engine.calculate_d2(
#         birth
#     )


# @app.post(
#     "/api/v1/chart/d3"
# )
# def calculate_d3(
#     birth: BirthData,
# ):

#     return engine.calculate_d3(
#         birth
#     )


# @app.post(
#     "/api/v1/chart/d4"
# )
# def calculate_d4(
#     birth: BirthData,
# ):

#     return engine.calculate_d4(
#         birth
#     )


# @app.post(
#     "/api/v1/chart/d7"
# )
# def calculate_d7(
#     birth: BirthData,
# ):

#     return engine.calculate_d7(
#         birth
#     )


# @app.post(
#     "/api/v1/chart/d9"
# )
# def calculate_d9(
#     birth: BirthData,
# ):

#     return engine.calculate_d9(
#         birth
#     )


# @app.post(
#     "/api/v1/chart/d10"
# )
# def calculate_d10(
#     birth: BirthData,
# ):

#     return engine.calculate_d10(
#         birth
#     )


# @app.post(
#     "/api/v1/chart/d12"
# )
# def calculate_d12(
#     birth: BirthData,
# ):

#     return engine.calculate_d12(
#         birth
#     )


# @app.post(
#     "/api/v1/chart/all"
# )
# def calculate_all_charts(
#     birth: BirthData,
# ):

#     return (
#         engine.calculate_all_charts(
#             birth
#         )
#     )


# @app.post(
#     "/api/v1/chart/{division}"
# )
# def calculate_chart_by_division(
#     division: int,
#     birth: BirthData,
# ):

#     try:

#         return (
#             engine.calculate_varga_chart(
#                 birth=birth,
#                 division=division,
#             )
#         )

#     except ValueError as error:

#         raise HTTPException(
#             status_code=404,
#             detail=str(
#                 error
#             ),
#         )


# @app.post(
#     "/api/v1/chart"
# )
# def calculate_chart_legacy(
#     birth: BirthData,
# ):

#     return (
#         engine.calculate_chart(
#             birth
#         )
#     )