from fastapi.testclient import TestClient

from app.main import app


client = TestClient(
    app
)


BIRTH_DATA = {
    "date": (
        "2003-10-10"
    ),

    "time": (
        "23:40:00"
    ),

    "latitude": (
        28.67
    ),

    "longitude": (
        77.21
    ),

    "timezone_offset": (
        5.5
    ),

    "ayanamsha": (
        "lahiri"
    ),

    "node_type": (
        "mean"
    ),
}


def test_root():

    response = client.get(
        "/"
    )

    assert (
        response.status_code
        == 200
    )


def test_supported_charts():

    response = client.get(
        "/api/v1/charts"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        len(
            data[
                "charts"
            ]
        )
        == 8
    )


def test_d1_endpoint():

    response = client.post(
        "/api/v1/chart/d1",
        json=BIRTH_DATA,
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data[
            "chart"
        ][
            "code"
        ]
        == "D1"
    )


def test_d9_endpoint():

    response = client.post(
        "/api/v1/chart/d9",
        json=BIRTH_DATA,
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data[
            "chart"
        ][
            "code"
        ]
        == "D9"
    )

    assert (
        data[
            "chart"
        ][
            "name"
        ]
        == "Navamsha"
    )


def test_d10_endpoint():

    response = client.post(
        "/api/v1/chart/d10",
        json=BIRTH_DATA,
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data[
            "chart"
        ][
            "code"
        ]
        == "D10"
    )


def test_generic_chart_endpoint():

    response = client.post(
        "/api/v1/chart/9",
        json=BIRTH_DATA,
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()[
            "chart"
        ][
            "code"
        ]
        == "D9"
    )


def test_unsupported_chart():

    response = client.post(
        "/api/v1/chart/99",
        json=BIRTH_DATA,
    )

    assert (
        response.status_code
        == 404
    )


def test_all_charts_endpoint():

    response = client.post(
        "/api/v1/chart/all",
        json=BIRTH_DATA,
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        "D1"
        in data[
            "charts"
        ]
    )

    assert (
        "D9"
        in data[
            "charts"
        ]
    )

    assert (
        "D10"
        in data[
            "charts"
        ]
    )