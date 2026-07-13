from app.constants import ZODIAC_SIGNS, SIGN_LORDS
from app.astrology.utils import normalize_degree


VARGA_NAMES = {
    1: "Rashi",
    2: "Hora",
    3: "Drekkana",
    4: "Chaturthamsha",
    7: "Saptamsha",
    9: "Navamsha",
    10: "Dashamsha",
    12: "Dwadashamsha",
    16: "Shodashamsha",
    20: "Vimshamsha",
    24: "Chaturvimshamsha",
    27: "Saptavimshamsha",
    30: "Trimshamsha",
}


def is_odd_sign(sign_index: int) -> bool:
    """
    sign_index is zero-based:
    Aries = 0, Taurus = 1, ..., Pisces = 11.

    Odd zodiac signs in traditional numbering:
    Aries 1, Gemini 3, Leo 5, Libra 7,
    Sagittarius 9, Aquarius 11.

    Therefore their zero-based indexes are even.
    """
    return sign_index % 2 == 0


def build_varga_position(
    source_longitude: float,
    target_sign_index: int,
    division: int,
    part_index: int,
) -> dict:
    """
    Build a normalized divisional-chart position.

    source_longitude:
        Original sidereal D1 longitude.

    target_sign_index:
        Destination sign in the divisional chart.

    division:
        D-number.

    part_index:
        Zero-based subdivision index inside the source sign.

    The degree within the target Varga sign is obtained by
    expanding the fractional progress through the source
    subdivision to a full 30-degree sign.
    """

    source_longitude = normalize_degree(source_longitude)

    source_sign_index = int(source_longitude // 30.0)
    degree_in_source_sign = source_longitude % 30.0

    segment_size = 30.0 / division

    segment_start = part_index * segment_size

    progress_inside_segment = (
        degree_in_source_sign - segment_start
    ) / segment_size

    # Floating-point protection.
    progress_inside_segment = max(
        0.0,
        min(progress_inside_segment, 0.999999999999)
    )

    degree_in_varga_sign = progress_inside_segment * 30.0

    varga_longitude = (
        target_sign_index * 30.0
        + degree_in_varga_sign
    ) % 360.0

    sign = ZODIAC_SIGNS[target_sign_index]

    return {
        "division": division,
        "chart": f"D{division}",
        "chart_name": VARGA_NAMES[division],

        "source_longitude": round(
            source_longitude,
            8,
        ),

        "source_sign_index": source_sign_index,
        "source_sign": ZODIAC_SIGNS[
            source_sign_index
        ],

        "part_index": part_index,
        "part_number": part_index + 1,

        "sign_index": target_sign_index,
        "sign_number": target_sign_index + 1,
        "sign": sign,
        "sign_lord": SIGN_LORDS[sign],

        "degree_in_sign": round(
            degree_in_varga_sign,
            8,
        ),

        "longitude": round(
            varga_longitude,
            8,
        ),
    }


# =============================================================
# D1 - RASHI
# =============================================================


def calculate_d1(longitude: float) -> dict:

    longitude = normalize_degree(longitude)

    sign_index = int(longitude // 30.0)

    return build_varga_position(
        source_longitude=longitude,
        target_sign_index=sign_index,
        division=1,
        part_index=0,
    )


# =============================================================
# D2 - HORA
# =============================================================


def calculate_d2(longitude: float) -> dict:
    """
    Parashari Hora.

    Each sign is divided into two 15-degree halves.

    Odd signs:
        0°-15°  -> Sun's Hora -> Leo
        15°-30° -> Moon's Hora -> Cancer

    Even signs:
        0°-15°  -> Moon's Hora -> Cancer
        15°-30° -> Sun's Hora -> Leo
    """

    longitude = normalize_degree(longitude)

    sign_index = int(longitude // 30.0)
    degree = longitude % 30.0

    part_index = min(
        int(degree // 15.0),
        1,
    )

    CANCER = 3
    LEO = 4

    if is_odd_sign(sign_index):

        target_sign = (
            LEO
            if part_index == 0
            else CANCER
        )

    else:

        target_sign = (
            CANCER
            if part_index == 0
            else LEO
        )

    return build_varga_position(
        longitude,
        target_sign,
        2,
        part_index,
    )


# =============================================================
# D3 - DREKKANA
# =============================================================


def calculate_d3(longitude: float) -> dict:
    """
    Parashari Drekkana.

    Three 10-degree divisions:

        1st -> source sign
        2nd -> 5th sign from source
        3rd -> 9th sign from source
    """

    longitude = normalize_degree(longitude)

    sign_index = int(longitude // 30.0)
    degree = longitude % 30.0

    part_index = min(
        int(degree // 10.0),
        2,
    )

    offsets = [
        0,
        4,
        8,
    ]

    target_sign = (
        sign_index
        + offsets[part_index]
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        3,
        part_index,
    )


# =============================================================
# D4 - CHATURTHAMSHA
# =============================================================


def calculate_d4(longitude: float) -> dict:
    """
    Chaturthamsha / Turyamsha.

    Four 7°30' divisions.

    Successive parts go to:

        1st from source
        4th from source
        7th from source
        10th from source
    """

    longitude = normalize_degree(longitude)

    sign_index = int(longitude // 30.0)
    degree = longitude % 30.0

    part_index = min(
        int(degree // 7.5),
        3,
    )

    offsets = [
        0,
        3,
        6,
        9,
    ]

    target_sign = (
        sign_index
        + offsets[part_index]
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        4,
        part_index,
    )


# =============================================================
# D7 - SAPTAMSHA
# =============================================================


def calculate_d7(longitude: float) -> dict:
    """
    Saptamsha.

    Seven equal divisions.

    Odd signs:
        count from the source sign.

    Even signs:
        count from the 7th sign from source.
    """

    longitude = normalize_degree(longitude)

    sign_index = int(longitude // 30.0)
    degree = longitude % 30.0

    division = 7
    segment_size = 30.0 / division

    part_index = min(
        int(degree / segment_size),
        division - 1,
    )

    if is_odd_sign(sign_index):
        start_sign = sign_index
    else:
        start_sign = (
            sign_index + 6
        ) % 12

    target_sign = (
        start_sign + part_index
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        7,
        part_index,
    )


# =============================================================
# D9 - NAVAMSHA
# =============================================================


def calculate_d9(longitude: float) -> dict:
    """
    Navamsha.

    Nine divisions of 3°20'.

    Starting signs:

        Movable signs -> same sign
        Fixed signs   -> 9th from source
        Dual signs    -> 5th from source

    Equivalent element-based starts:

        Fire  -> Aries
        Earth -> Capricorn
        Air   -> Libra
        Water -> Cancer
    """

    longitude = normalize_degree(longitude)

    sign_index = int(longitude // 30.0)
    degree = longitude % 30.0

    division = 9
    segment_size = 30.0 / division

    part_index = min(
        int(degree / segment_size),
        division - 1,
    )

    # Movable signs:
    # Aries, Cancer, Libra, Capricorn
    if sign_index in {
        0,
        3,
        6,
        9,
    }:
        start_sign = sign_index

    # Fixed signs:
    # Taurus, Leo, Scorpio, Aquarius
    elif sign_index in {
        1,
        4,
        7,
        10,
    }:
        start_sign = (
            sign_index + 8
        ) % 12

    # Dual signs:
    # Gemini, Virgo, Sagittarius, Pisces
    else:
        start_sign = (
            sign_index + 4
        ) % 12

    target_sign = (
        start_sign + part_index
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        9,
        part_index,
    )


# =============================================================
# D10 - DASHAMSHA
# =============================================================


def calculate_d10(longitude: float) -> dict:
    """
    Dashamsha / Dasamsa.

    Ten divisions of 3 degrees.

    Odd signs:
        start from source sign.

    Even signs:
        start from 9th sign from source.
    """

    longitude = normalize_degree(longitude)

    sign_index = int(longitude // 30.0)
    degree = longitude % 30.0

    division = 10
    segment_size = 3.0

    part_index = min(
        int(degree // segment_size),
        division - 1,
    )

    if is_odd_sign(sign_index):
        start_sign = sign_index
    else:
        start_sign = (
            sign_index + 8
        ) % 12

    target_sign = (
        start_sign + part_index
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        10,
        part_index,
    )


# =============================================================
# D12 - DWADASHAMSHA
# =============================================================


def calculate_d12(longitude: float) -> dict:
    """
    Dwadashamsha.

    Twelve divisions of 2°30'.

    Count successively from the source sign.
    """

    longitude = normalize_degree(longitude)

    sign_index = int(longitude // 30.0)
    degree = longitude % 30.0

    division = 12
    segment_size = 2.5

    part_index = min(
        int(degree // segment_size),
        division - 1,
    )

    target_sign = (
        sign_index + part_index
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        12,
        part_index,
    )


# =============================================================
# D16 - SHODASHAMSHA
# =============================================================


def calculate_d16(longitude: float) -> dict:
    """
    Shodashamsha / Kalamsa.

    Sixteen equal divisions.

    Each division is:

        30° / 16
        = 1.875°
        = 1°52'30"

    Parashari starting signs:

        Movable signs:
            start from Aries.

        Fixed signs:
            start from Leo.

        Dual signs:
            start from Sagittarius.

    From the appropriate starting sign,
    count zodiacally according to the
    zero-based subdivision index.
    """

    longitude = normalize_degree(
        longitude
    )

    sign_index = int(
        longitude // 30.0
    )

    degree = (
        longitude % 30.0
    )

    division = 16

    segment_size = (
        30.0 / division
    )

    part_index = min(
        int(
            degree / segment_size
        ),
        division - 1,
    )

    # ---------------------------------------------------------
    # MOVABLE SIGNS
    #
    # Aries
    # Cancer
    # Libra
    # Capricorn
    #
    # Start from Aries.
    # ---------------------------------------------------------

    if sign_index in {
        0,
        3,
        6,
        9,
    }:

        start_sign = 0  # Aries

    # ---------------------------------------------------------
    # FIXED SIGNS
    #
    # Taurus
    # Leo
    # Scorpio
    # Aquarius
    #
    # Start from Leo.
    # ---------------------------------------------------------

    elif sign_index in {
        1,
        4,
        7,
        10,
    }:

        start_sign = 4  # Leo

    # ---------------------------------------------------------
    # DUAL SIGNS
    #
    # Gemini
    # Virgo
    # Sagittarius
    # Pisces
    #
    # Start from Sagittarius.
    # ---------------------------------------------------------

    else:

        start_sign = 8  # Sagittarius

    target_sign = (
        start_sign
        + part_index
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        16,
        part_index,
    )

# =============================================================
# D20 - VIMSHAMSHA
# =============================================================


def calculate_d20(longitude: float) -> dict:
    """
    Vimshamsha.

    Twenty equal divisions.

    Each division is:

        30° / 20
        = 1.5°
        = 1°30'

    Parashari starting signs:

        Movable signs:
            start from Aries.

        Fixed signs:
            start from Sagittarius.

        Dual signs:
            start from Leo.

    From the appropriate starting sign,
    count zodiacally according to the
    zero-based subdivision index.
    """

    longitude = normalize_degree(
        longitude
    )

    sign_index = int(
        longitude // 30.0
    )

    degree = (
        longitude % 30.0
    )

    division = 20

    segment_size = (
        30.0 / division
    )

    part_index = min(
        int(
            degree / segment_size
        ),
        division - 1,
    )

    # ---------------------------------------------------------
    # MOVABLE SIGNS
    #
    # Aries
    # Cancer
    # Libra
    # Capricorn
    #
    # Start from Aries.
    # ---------------------------------------------------------

    if sign_index in {
        0,
        3,
        6,
        9,
    }:

        start_sign = 0  # Aries

    # ---------------------------------------------------------
    # FIXED SIGNS
    #
    # Taurus
    # Leo
    # Scorpio
    # Aquarius
    #
    # Start from Sagittarius.
    # ---------------------------------------------------------

    elif sign_index in {
        1,
        4,
        7,
        10,
    }:

        start_sign = 8  # Sagittarius

    # ---------------------------------------------------------
    # DUAL SIGNS
    #
    # Gemini
    # Virgo
    # Sagittarius
    # Pisces
    #
    # Start from Leo.
    # ---------------------------------------------------------

    else:

        start_sign = 4  # Leo

    target_sign = (
        start_sign
        + part_index
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        20,
        part_index,
    )

# =============================================================
# D24 - CHATURVIMSHAMSHA / SIDDHAMSHA
# =============================================================


def calculate_d24(longitude: float) -> dict:
    """
    Chaturvimshamsha / Siddhamsha.

    Twenty-four equal divisions.

    Each division:
        30° / 24 = 1.25° = 1°15'

    Parashari rule:

        Odd signs:
            start from Leo.

        Even signs:
            start from Cancer.

    Count zodiacally from the appropriate starting sign
    according to the zero-based subdivision index.
    """

    longitude = normalize_degree(
        longitude
    )

    sign_index = int(
        longitude // 30.0
    )

    degree = (
        longitude % 30.0
    )

    division = 24

    segment_size = (
        30.0 / division
    )

    part_index = min(
        int(
            degree / segment_size
        ),
        division - 1,
    )

    if is_odd_sign(
        sign_index
    ):
        # Odd signs start from Leo
        start_sign = 4

    else:
        # Even signs start from Cancer
        start_sign = 3

    target_sign = (
        start_sign
        + part_index
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        24,
        part_index,
    )

# =============================================================
# D27 - SAPTAVIMSHAMSHA / BHAMSA
# =============================================================


def calculate_d27(longitude: float) -> dict:
    """
    Saptavimshamsha / Bhamsa.

    Twenty-seven equal divisions.

    Each division:
        30° / 27
        = 1.111111...°
        = 1°06'40"

    Parashari starting signs by element:

        Fire signs:
            Aries

        Earth signs:
            Cancer

        Air signs:
            Libra

        Water signs:
            Capricorn

    Count zodiacally from the appropriate starting sign
    according to the zero-based subdivision index.
    """

    longitude = normalize_degree(
        longitude
    )

    sign_index = int(
        longitude // 30.0
    )

    degree = (
        longitude % 30.0
    )

    division = 27

    segment_size = (
        30.0 / division
    )

    part_index = min(
        int(
            degree / segment_size
        ),
        division - 1,
    )

    # Fire signs:
    # Aries, Leo, Sagittarius
    if sign_index in {
        0,
        4,
        8,
    }:
        start_sign = 0  # Aries

    # Earth signs:
    # Taurus, Virgo, Capricorn
    elif sign_index in {
        1,
        5,
        9,
    }:
        start_sign = 3  # Cancer

    # Air signs:
    # Gemini, Libra, Aquarius
    elif sign_index in {
        2,
        6,
        10,
    }:
        start_sign = 6  # Libra

    # Water signs:
    # Cancer, Scorpio, Pisces
    else:
        start_sign = 9  # Capricorn

    target_sign = (
        start_sign
        + part_index
    ) % 12

    return build_varga_position(
        longitude,
        target_sign,
        27,
        part_index,
    )

# =============================================================
# CALCULATOR REGISTRY
# =============================================================


VARGA_CALCULATORS = {
    1: calculate_d1,
    2: calculate_d2,
    3: calculate_d3,
    4: calculate_d4,
    7: calculate_d7,
    9: calculate_d9,
    10: calculate_d10,
    12: calculate_d12,
    16: calculate_d16,
    20: calculate_d20,
    24: calculate_d24,
    27: calculate_d27,
}


# =============================================================
# CALCULATE SINGLE POSITION
# =============================================================


def calculate_varga(
    longitude: float,
    division: int,
) -> dict:

    calculator = VARGA_CALCULATORS.get(
        division
    )

    if calculator is None:
        raise ValueError(
            f"D{division} is not implemented yet."
        )

    return calculator(longitude)


# =============================================================
# CALCULATE COMPLETE VARGA CHART
# =============================================================


def calculate_varga_chart(
    division: int,
    ascendant_longitude: float,
    planets: dict,
) -> dict:

    ascendant = calculate_varga(
        ascendant_longitude,
        division,
    )

    asc_sign_index = ascendant[
        "sign_index"
    ]

    varga_planets = {}

    for planet_name, planet_data in planets.items():

        position = calculate_varga(
            planet_data["longitude"],
            division,
        )

        position["house"] = (
            (
                position["sign_index"]
                - asc_sign_index
            )
            % 12
        ) + 1

        varga_planets[
            planet_name
        ] = position

    houses = []

    for house_number in range(
        1,
        13,
    ):

        sign_index = (
            asc_sign_index
            + house_number
            - 1
        ) % 12

        sign = ZODIAC_SIGNS[
            sign_index
        ]

        houses.append({
            "house": house_number,
            "sign_index": sign_index,
            "sign_number": (
                sign_index + 1
            ),
            "sign": sign,
            "lord": SIGN_LORDS[
                sign
            ],
        })

    return {
        "division": division,

        "code": f"D{division}",

        "name": VARGA_NAMES[
            division
        ],

        "ascendant": ascendant,

        "planets": varga_planets,

        "houses": houses,
    }


# =============================================================
# CALCULATE ALL SUPPORTED VARGAS
# =============================================================


def calculate_all_vargas(
    ascendant_longitude: float,
    planets: dict,
) -> dict:

    result = {}

    for division in (
        1,
        2,
        3,
        4,
        7,
        9,
        10,
        12,
        16,
        20,
        24,
        27,
    ):

        code = f"D{division}"

        result[code] = calculate_varga_chart(
            division=division,
            ascendant_longitude=ascendant_longitude,
            planets=planets,
        )

    return result