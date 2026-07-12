from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


BIRTH_DATA = {
    "date": "2003-10-10",
    "time": "23:40:00",
    "latitude": 28.67,
    "longitude": 77.21,
    "timezone_offset": 5.5,
    "ayanamsha": "lahiri",
    "node_type": "mean",
}


# =============================================================
# HELPER
# =============================================================


def create_chart_session() -> str:
    """
    Create a chart session and return its chart_id.
    """

    response = client.post(
        "/api/v1/chart-sessions",
        json=BIRTH_DATA,
    )

    assert response.status_code == 201

    data = response.json()

    assert "chart_id" in data

    return data["chart_id"]


# =============================================================
# ROOT
# =============================================================


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Jyotish AI Backend"
    assert data["status"] == "running"


# =============================================================
# HEALTH
# =============================================================


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


# =============================================================
# SUPPORTED CHARTS
# =============================================================


def test_supported_charts():

    response = client.get(
        "/api/v1/charts"
    )

    assert response.status_code == 200

    data = response.json()

    assert "charts" in data

    codes = [
        chart["code"]
        for chart in data["charts"]
    ]

    assert "D1" in codes
    assert "D9" in codes
    assert "D10" in codes
    assert "D12" in codes


# =============================================================
# CREATE CHART SESSION
# =============================================================


def test_create_chart_session():

    response = client.post(
        "/api/v1/chart-sessions",
        json=BIRTH_DATA,
    )

    assert response.status_code == 201

    data = response.json()

    assert "chart_id" in data

    assert (
        data["message"]
        == "Chart session created successfully."
    )

    assert "available_charts" in data

    assert "d1" in data["available_charts"]
    assert "d9" in data["available_charts"]
    assert "d10" in data["available_charts"]


# =============================================================
# GET CHART SESSION INFO
# =============================================================


def test_get_chart_session():

    chart_id = create_chart_session()

    response = client.get(
        f"/api/v1/chart-sessions/{chart_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["chart_id"] == chart_id

    assert "birth" in data

    assert (
        data["birth"]["date"]
        == BIRTH_DATA["date"]
    )

    assert (
        data["birth"]["latitude"]
        == BIRTH_DATA["latitude"]
    )


# =============================================================
# D1 ENDPOINT
# =============================================================


def test_d1_endpoint():

    chart_id = create_chart_session()

    response = client.get(
        f"/api/v1/chart-sessions/{chart_id}/d1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["chart"]["division"] == 1
    assert data["chart"]["code"] == "D1"
    assert data["chart"]["name"] == "Rashi"

    assert (
        data["chart"]["ascendant"]["sign"]
        == "Gemini"
    )


# =============================================================
# D9 ENDPOINT
# =============================================================


def test_d9_endpoint():

    chart_id = create_chart_session()

    response = client.get(
        f"/api/v1/chart-sessions/{chart_id}/d9"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["chart"]["division"] == 9
    assert data["chart"]["code"] == "D9"
    assert data["chart"]["name"] == "Navamsha"

    assert (
        data["chart"]["ascendant"]["sign"]
        == "Taurus"
    )


# =============================================================
# D10 ENDPOINT
# =============================================================


def test_d10_endpoint():

    chart_id = create_chart_session()

    response = client.get(
        f"/api/v1/chart-sessions/{chart_id}/d10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["chart"]["division"] == 10
    assert data["chart"]["code"] == "D10"
    assert data["chart"]["name"] == "Dashamsha"

    assert (
        data["chart"]["ascendant"]["sign"]
        == "Aquarius"
    )


# =============================================================
# GENERIC CHART ENDPOINT
# =============================================================


def test_generic_chart_endpoint():

    chart_id = create_chart_session()

    response = client.get(
        (
            f"/api/v1/chart-sessions/"
            f"{chart_id}/charts/9"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["chart"]["division"] == 9
    assert data["chart"]["code"] == "D9"


# =============================================================
# UNSUPPORTED GENERIC CHART
# =============================================================


def test_unsupported_chart_endpoint():

    chart_id = create_chart_session()

    response = client.get(
        (
            f"/api/v1/chart-sessions/"
            f"{chart_id}/charts/999"
        )
    )

    assert response.status_code == 404


# =============================================================
# ALL CHARTS ENDPOINT
# =============================================================


def test_all_charts_endpoint():

    chart_id = create_chart_session()

    response = client.get(
        f"/api/v1/chart-sessions/{chart_id}/all"
    )

    assert response.status_code == 200

    data = response.json()

    assert "charts" in data

    assert "D1" in data["charts"]
    assert "D9" in data["charts"]
    assert "D10" in data["charts"]
    assert "D12" in data["charts"]


# =============================================================
# UNKNOWN CHART SESSION
# =============================================================


def test_unknown_chart_session():

    fake_chart_id = (
        "00000000-0000-0000-0000-000000000000"
    )

    response = client.get(
        f"/api/v1/chart-sessions/{fake_chart_id}/d1"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Chart session not found."
    }


# =============================================================
# INVALID UUID
# =============================================================


def test_invalid_chart_id():

    response = client.get(
        "/api/v1/chart-sessions/not-a-valid-uuid/d1"
    )

    assert response.status_code == 422


# =============================================================
# DELETE CHART SESSION
# =============================================================


def test_delete_chart_session():

    chart_id = create_chart_session()

    delete_response = client.delete(
        f"/api/v1/chart-sessions/{chart_id}"
    )

    assert delete_response.status_code == 200

    # The session should no longer exist.

    get_response = client.get(
        f"/api/v1/chart-sessions/{chart_id}/d1"
    )

    assert get_response.status_code == 404