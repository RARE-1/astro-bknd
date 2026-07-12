from app.constants import ZODIAC_SIGNS, NAKSHATRAS


NAKSHATRA_SIZE = 360.0 / 27.0
PADA_SIZE = NAKSHATRA_SIZE / 4.0


def normalize_degree(value: float) -> float:
    return value % 360.0


def sign_index_from_longitude(longitude: float) -> int:
    longitude = normalize_degree(longitude)
    return int(longitude // 30.0)


def sign_from_longitude(longitude: float) -> str:
    return ZODIAC_SIGNS[sign_index_from_longitude(longitude)]


def degree_in_sign(longitude: float) -> float:
    return normalize_degree(longitude) % 30.0


def nakshatra_details(longitude: float) -> dict:
    longitude = normalize_degree(longitude)

    index = int(longitude // NAKSHATRA_SIZE)

    # Floating-point protection near 360 degrees.
    index = min(index, 26)

    start = index * NAKSHATRA_SIZE
    degree_in_nakshatra = longitude - start

    pada = int(degree_in_nakshatra // PADA_SIZE) + 1
    pada = min(max(pada, 1), 4)

    name, lord = NAKSHATRAS[index]

    return {
        "index": index + 1,
        "name": name,
        "lord": lord,
        "pada": pada,
        "degree_in_nakshatra": round(degree_in_nakshatra, 8),
    }


def relative_house(
    object_sign_index: int,
    ascendant_sign_index: int,
) -> int:
    """
    Whole-sign house calculation.

    Ascendant sign = House 1.
    Next sign = House 2.
    ...
    """
    return ((object_sign_index - ascendant_sign_index) % 12) + 1


def decimal_to_dms(value: float) -> dict:
    value = abs(value)

    degrees = int(value)

    minutes_float = (value - degrees) * 60
    minutes = int(minutes_float)

    seconds = (minutes_float - minutes) * 60

    return {
        "degrees": degrees,
        "minutes": minutes,
        "seconds": round(seconds, 4),
    }