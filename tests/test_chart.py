from app.models import BirthData
from app.astrology.chart_engine import VedicChartEngine


def test_chart_generation():

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

    result = engine.calculate_chart(birth)

    assert "ascendant" in result
    assert "planets" in result

    assert len(result["planets"]) == 12
    assert len(result["houses"]) == 12

    assert 0 <= result["planets"]["Sun"]["longitude"] < 360
    assert 0 <= result["planets"]["Moon"]["longitude"] < 360

    rahu = result["planets"]["Rahu"]["longitude"]
    ketu = result["planets"]["Ketu"]["longitude"]

    difference = (ketu - rahu) % 360

    assert abs(difference - 180) < 0.000001