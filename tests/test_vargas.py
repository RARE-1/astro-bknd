import pytest

from app.astrology.vargas import (
    calculate_d1,
    calculate_d2,
    calculate_d3,
    calculate_d4,
    calculate_d7,
    calculate_d9,
    calculate_d10,
    calculate_d12,
    calculate_all_vargas,
)

from app.models import BirthData
from app.astrology.chart_engine import (
    VedicChartEngine,
)


def test_d1_preserves_sign():

    result = calculate_d1(
        162.46133062
    )

    assert result["sign"] == "Virgo"


def test_d2_odd_first_half_goes_to_leo():

    # Aries 10 degrees.
    result = calculate_d2(
        10.0
    )

    assert result["sign"] == "Leo"


def test_d2_even_first_half_goes_to_cancer():

    # Taurus 10 degrees.
    # Absolute longitude = 40 degrees.
    result = calculate_d2(
        40.0
    )

    assert result["sign"] == "Cancer"


def test_d3_first_drekkana_same_sign():

    # Aries 5 degrees.
    result = calculate_d3(
        5.0
    )

    assert result["sign"] == "Aries"


def test_d3_second_drekkana_fifth_sign():

    # Aries 15 degrees.
    result = calculate_d3(
        15.0
    )

    assert result["sign"] == "Leo"


def test_d3_third_drekkana_ninth_sign():

    # Aries 25 degrees.
    result = calculate_d3(
        25.0
    )

    assert result["sign"] == "Sagittarius"


def test_d4_aries_quarters():

    assert calculate_d4(
        1.0
    )["sign"] == "Aries"

    assert calculate_d4(
        8.0
    )["sign"] == "Cancer"

    assert calculate_d4(
        16.0
    )["sign"] == "Libra"

    assert calculate_d4(
        24.0
    )["sign"] == "Capricorn"


def test_d9_aries_first_navamsa():

    result = calculate_d9(
        1.0
    )

    assert result["sign"] == "Aries"


def test_d9_taurus_first_navamsa():

    # Taurus is fixed.
    # First Navamsha begins from Capricorn.
    result = calculate_d9(
        31.0
    )

    assert result["sign"] == "Capricorn"


def test_d9_gemini_first_navamsa():

    # Gemini is dual.
    # First Navamsha begins from Libra.
    result = calculate_d9(
        61.0
    )

    assert result["sign"] == "Libra"


def test_d10_aries_first_dashamsha():

    result = calculate_d10(
        1.0
    )

    assert result["sign"] == "Aries"


def test_d10_taurus_first_dashamsha():

    # Taurus is even.
    # Start from 9th sign from Taurus:
    # Capricorn.
    result = calculate_d10(
        31.0
    )

    assert result["sign"] == "Capricorn"


def test_d12_counts_from_source_sign():

    # Aries:
    # first part -> Aries
    # second part -> Taurus

    assert calculate_d12(
        1.0
    )["sign"] == "Aries"

    assert calculate_d12(
        3.0
    )["sign"] == "Taurus"


def test_full_chart_generates_vargas():

    engine = VedicChartEngine()

    birth = BirthData(
        date="2003-10-10",
        time="23:40:00",
        latitude=28.67,
        longitude=77.21,
        timezone_offset=5.5,
        ayanamsha="lahiri",
        node_type="mean",
    )

    result = engine.calculate_chart(
        birth
    )

    assert "vargas" in result

    assert "D1" in result["vargas"]
    assert "D9" in result["vargas"]
    assert "D10" in result["vargas"]

    assert (
        len(
            result[
                "vargas"
            ]["D9"]["planets"]
        )
        == 9
    )

    assert (
        len(
            result[
                "vargas"
            ]["D10"]["houses"]
        )
        == 12
    )


def test_all_varga_longitudes_are_valid():

    engine = VedicChartEngine()

    birth = BirthData(
        date="2003-10-10",
        time="23:40:00",
        latitude=28.67,
        longitude=77.21,
        timezone_offset=5.5,
    )

    chart = engine.calculate_chart(
        birth
    )

    for varga in chart[
        "vargas"
    ].values():

        asc_longitude = varga[
            "ascendant"
        ]["longitude"]

        assert (
            0.0
            <= asc_longitude
            < 360.0
        )

        for planet in varga[
            "planets"
        ].values():

            assert (
                0.0
                <= planet[
                    "longitude"
                ]
                < 360.0
            )