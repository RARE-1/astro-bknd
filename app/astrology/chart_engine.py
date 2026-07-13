from datetime import datetime, timedelta, timezone

import swisseph as swe

from app.constants import SIGN_LORDS, ZODIAC_SIGNS
from app.models import BirthData

from app.astrology.utils import (
    normalize_degree,
    sign_index_from_longitude,
    sign_from_longitude,
    degree_in_sign,
    nakshatra_details,
    relative_house,
    decimal_to_dms,
)

from app.astrology.vargas import (
    VARGA_NAMES,
    VARGA_CALCULATORS,
    calculate_varga_chart,
    calculate_all_vargas,
)


PLANET_IDS = {
    # Classical planets
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,

    # Outer planets
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}


class VedicChartEngine:

    def __init__(self):
        """
        Vedic astrology calculation engine.

        Current settings:
        - Swiss Ephemeris
        - Sidereal zodiac
        - Lahiri / Chitrapaksha ayanamsha
        - Whole-sign houses
        """

        swe.set_sid_mode(swe.SIDM_LAHIRI)

    # =========================================================
    # TIME
    # =========================================================

    def _local_datetime(
        self,
        birth: BirthData,
    ) -> datetime:

        tz = timezone(
            timedelta(
                hours=birth.timezone_offset
            )
        )

        return datetime.combine(
            birth.date,
            birth.time,
            tzinfo=tz,
        )

    def _utc_datetime(
        self,
        birth: BirthData,
    ) -> datetime:

        return self._local_datetime(
            birth
        ).astimezone(
            timezone.utc
        )

    # =========================================================
    # JULIAN DAY
    # =========================================================

    def _julian_day_ut(
        self,
        dt_utc: datetime,
    ) -> float:

        decimal_hour = (
            dt_utc.hour
            + dt_utc.minute / 60.0
            + dt_utc.second / 3600.0
            + dt_utc.microsecond
            / 3_600_000_000.0
        )

        return swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            decimal_hour,
            swe.GREG_CAL,
        )

    # =========================================================
    # SWISS EPHEMERIS FLAGS
    # =========================================================

    def _planet_flags(
        self,
    ) -> int:

        return (
            swe.FLG_SWIEPH
            | swe.FLG_SPEED
            | swe.FLG_SIDEREAL
        )

    # =========================================================
    # PLANET CALCULATION
    # =========================================================

    def _calculate_planet(
        self,
        jd_ut: float,
        planet_id: int,
    ) -> dict:

        result, return_flag = swe.calc_ut(
            jd_ut,
            planet_id,
            self._planet_flags(),
        )

        longitude = normalize_degree(
            result[0]
        )

        latitude = result[1]
        distance = result[2]
        longitude_speed = result[3]

        sign_index = (
            sign_index_from_longitude(
                longitude
            )
        )

        sign = sign_from_longitude(
            longitude
        )

        degree = degree_in_sign(
            longitude
        )

        return {
            "longitude": round(
                longitude,
                8,
            ),

            "latitude": round(
                latitude,
                8,
            ),

            "distance_au": round(
                distance,
                8,
            ),

            "speed_longitude": round(
                longitude_speed,
                8,
            ),

            "retrograde": (
                longitude_speed < 0
            ),

            "sign_index": (
                sign_index
            ),

            "sign_number": (
                sign_index + 1
            ),

            "sign": (
                sign
            ),

            "sign_lord": (
                SIGN_LORDS[
                    sign
                ]
            ),

            "degree_in_sign": round(
                degree,
                8,
            ),

            "degree_dms": (
                decimal_to_dms(
                    degree
                )
            ),

            "nakshatra": (
                nakshatra_details(
                    longitude
                )
            ),

            "swiss_ephemeris_return_flag": (
                return_flag
            ),
        }

    # =========================================================
    # RAHU
    # =========================================================

    def _calculate_rahu(
        self,
        jd_ut: float,
        node_type: str,
    ) -> dict:

        node_id = (
            swe.TRUE_NODE
            if node_type == "true"
            else swe.MEAN_NODE
        )

        return self._calculate_planet(
            jd_ut,
            node_id,
        )

    # =========================================================
    # KETU
    # =========================================================

    def _calculate_ketu(
        self,
        rahu: dict,
    ) -> dict:

        longitude = normalize_degree(
            rahu["longitude"]
            + 180.0
        )

        sign_index = (
            sign_index_from_longitude(
                longitude
            )
        )

        sign = sign_from_longitude(
            longitude
        )

        degree = degree_in_sign(
            longitude
        )

        return {
            "longitude": round(
                longitude,
                8,
            ),

            "latitude": round(
                -rahu["latitude"],
                8,
            ),

            "distance_au": (
                rahu[
                    "distance_au"
                ]
            ),

            "speed_longitude": (
                rahu[
                    "speed_longitude"
                ]
            ),

            "retrograde": (
                rahu[
                    "retrograde"
                ]
            ),

            "sign_index": (
                sign_index
            ),

            "sign_number": (
                sign_index + 1
            ),

            "sign": (
                sign
            ),

            "sign_lord": (
                SIGN_LORDS[
                    sign
                ]
            ),

            "degree_in_sign": round(
                degree,
                8,
            ),

            "degree_dms": (
                decimal_to_dms(
                    degree
                )
            ),

            "nakshatra": (
                nakshatra_details(
                    longitude
                )
            ),

            "derived_from": (
                "Rahu + 180 degrees"
            ),
        }

    # =========================================================
    # ASCENDANT
    # =========================================================

    def _calculate_ascendant(
        self,
        jd_ut: float,
        latitude: float,
        longitude: float,
    ) -> dict:

        _, ascmc = swe.houses_ex(
            jd_ut,
            latitude,
            longitude,
            b"P",
            swe.FLG_SIDEREAL,
        )

        asc_longitude = normalize_degree(
            ascmc[0]
        )

        sign_index = (
            sign_index_from_longitude(
                asc_longitude
            )
        )

        sign = sign_from_longitude(
            asc_longitude
        )

        degree = degree_in_sign(
            asc_longitude
        )

        return {
            "longitude": round(
                asc_longitude,
                8,
            ),

            "sign_index": (
                sign_index
            ),

            "sign_number": (
                sign_index + 1
            ),

            "sign": (
                sign
            ),

            "sign_lord": (
                SIGN_LORDS[
                    sign
                ]
            ),

            "degree_in_sign": round(
                degree,
                8,
            ),

            "degree_dms": (
                decimal_to_dms(
                    degree
                )
            ),

            "nakshatra": (
                nakshatra_details(
                    asc_longitude
                )
            ),
        }

    # =========================================================
    # WHOLE-SIGN HOUSES
    # =========================================================

    def _build_whole_sign_houses(
        self,
        asc_sign_index: int,
    ) -> list[dict]:

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
                "house": (
                    house_number
                ),

                "sign_index": (
                    sign_index
                ),

                "sign_number": (
                    sign_index + 1
                ),

                "sign": (
                    sign
                ),

                "lord": (
                    SIGN_LORDS[
                        sign
                    ]
                ),
            })

        return houses

    # =========================================================
    # BASE ASTRONOMICAL CHART DATA
    # =========================================================

    def calculate_base_chart(
        self,
        birth: BirthData,
    ) -> dict:
        """
        Calculate the shared astronomical foundation.

        This method does NOT calculate every Varga.

        All individual chart endpoints reuse this method.
        """

        swe.set_sid_mode(
            swe.SIDM_LAHIRI
        )

        # -----------------------------------------------------
        # TIME
        # -----------------------------------------------------

        local_dt = (
            self._local_datetime(
                birth
            )
        )

        utc_dt = (
            self._utc_datetime(
                birth
            )
        )

        # -----------------------------------------------------
        # JULIAN DAY
        # -----------------------------------------------------

        jd_ut = (
            self._julian_day_ut(
                utc_dt
            )
        )

        # -----------------------------------------------------
        # AYANAMSHA
        # -----------------------------------------------------

        ayanamsha = (
            swe.get_ayanamsa_ut(
                jd_ut
            )
        )

        # -----------------------------------------------------
        # ASCENDANT
        # -----------------------------------------------------

        ascendant = (
            self._calculate_ascendant(
                jd_ut=jd_ut,
                latitude=birth.latitude,
                longitude=birth.longitude,
            )
        )

        asc_sign_index = (
            ascendant[
                "sign_index"
            ]
        )

        # -----------------------------------------------------
        # PLANETS
        # -----------------------------------------------------

        planets = {}

        for (
            name,
            planet_id,
        ) in PLANET_IDS.items():

            planet = (
                self._calculate_planet(
                    jd_ut,
                    planet_id,
                )
            )

            planet["house"] = (
                relative_house(
                    planet[
                        "sign_index"
                    ],
                    asc_sign_index,
                )
            )

            planets[
                name
            ] = planet

        # -----------------------------------------------------
        # RAHU
        # -----------------------------------------------------

        rahu = (
            self._calculate_rahu(
                jd_ut,
                birth.node_type,
            )
        )

        rahu["house"] = (
            relative_house(
                rahu[
                    "sign_index"
                ],
                asc_sign_index,
            )
        )

        planets[
            "Rahu"
        ] = rahu

        # -----------------------------------------------------
        # KETU
        # -----------------------------------------------------

        ketu = (
            self._calculate_ketu(
                rahu
            )
        )

        ketu["house"] = (
            relative_house(
                ketu[
                    "sign_index"
                ],
                asc_sign_index,
            )
        )

        planets[
            "Ketu"
        ] = ketu

        # -----------------------------------------------------
        # D1 HOUSES
        # -----------------------------------------------------

        houses = (
            self._build_whole_sign_houses(
                asc_sign_index
            )
        )

        return {
            "engine": {
                "astronomical_engine": (
                    "Swiss Ephemeris"
                ),

                "zodiac": (
                    "sidereal"
                ),

                "ayanamsha": (
                    "Lahiri / Chitrapaksha"
                ),

                "house_system": (
                    "whole_sign"
                ),

                "node_type": (
                    birth.node_type
                ),
            },

            "birth": {
                "local_datetime": (
                    local_dt.isoformat()
                ),

                "utc_datetime": (
                    utc_dt.isoformat()
                ),

                "latitude": (
                    birth.latitude
                ),

                "longitude": (
                    birth.longitude
                ),

                "timezone_offset": (
                    birth.timezone_offset
                ),
            },

            "astronomy": {
                "julian_day_ut": round(
                    jd_ut,
                    8,
                ),

                "ayanamsha_degrees": round(
                    ayanamsha,
                    8,
                ),
            },

            "ascendant": (
                ascendant
            ),

            "planets": (
                planets
            ),

            "houses": (
                houses
            ),
        }

    # =========================================================
    # INDIVIDUAL VARGA
    # =========================================================

    def calculate_varga_chart(
        self,
        birth: BirthData,
        division: int,
    ) -> dict:
        """
        Calculate one requested divisional chart only.

        Examples:
            division=1  -> D1
            division=9  -> D9
            division=10 -> D10
        """

        if division not in VARGA_CALCULATORS:
            raise ValueError(
                f"D{division} is not implemented."
            )

        base_chart = (
            self.calculate_base_chart(
                birth
            )
        )

        varga = calculate_varga_chart(
            division=division,
            ascendant_longitude=(
                base_chart[
                    "ascendant"
                ]["longitude"]
            ),
            planets=(
                base_chart[
                    "planets"
                ]
            ),
        )

        return {
            "engine": (
                base_chart[
                    "engine"
                ]
            ),

            "birth": (
                base_chart[
                    "birth"
                ]
            ),

            "astronomy": (
                base_chart[
                    "astronomy"
                ]
            ),

            "chart": (
                varga
            ),
        }

    # =========================================================
    # D1
    # =========================================================

    def calculate_d1(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=1,
        )

    # =========================================================
    # D2
    # =========================================================

    def calculate_d2(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=2,
        )

    # =========================================================
    # D3
    # =========================================================

    def calculate_d3(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=3,
        )

    # =========================================================
    # D4
    # =========================================================

    def calculate_d4(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=4,
        )

    # =========================================================
    # D7
    # =========================================================

    def calculate_d7(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=7,
        )

    # =========================================================
    # D9
    # =========================================================

    def calculate_d9(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=9,
        )

    # =========================================================
    # D10
    # =========================================================

    def calculate_d10(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=10,
        )

    # =========================================================
    # D12
    # =========================================================

    def calculate_d12(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=12,
        )
    
    # =========================================================
    # D16
    # =========================================================

    def calculate_d16(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=16,
        )
    
    # =========================================================
    # D20
    # =========================================================

    def calculate_d20(
        self,
        birth: BirthData,
    ) -> dict:

        return self.calculate_varga_chart(
            birth=birth,
            division=20,
        )
    
    # =========================================================
    # ALL VARGAS
    # =========================================================

    def calculate_all_charts(
        self,
        birth: BirthData,
    ) -> dict:

        base_chart = (
            self.calculate_base_chart(
                birth
            )
        )

        vargas = (
            calculate_all_vargas(
                ascendant_longitude=(
                    base_chart[
                        "ascendant"
                    ]["longitude"]
                ),
                planets=(
                    base_chart[
                        "planets"
                    ]
                ),
            )
        )

        return {
            "engine": (
                base_chart[
                    "engine"
                ]
            ),

            "birth": (
                base_chart[
                    "birth"
                ]
            ),

            "astronomy": (
                base_chart[
                    "astronomy"
                ]
            ),

            "charts": (
                vargas
            ),
        }

    # =========================================================
    # BACKWARD COMPATIBILITY
    # =========================================================

    def calculate_chart(
        self,
        birth: BirthData,
    ) -> dict:
        """
        Kept so existing code and tests do not break.

        Returns the complete currently-supported chart set.
        """

        base_chart = (
            self.calculate_base_chart(
                birth
            )
        )

        vargas = (
            calculate_all_vargas(
                ascendant_longitude=(
                    base_chart[
                        "ascendant"
                    ]["longitude"]
                ),
                planets=(
                    base_chart[
                        "planets"
                    ]
                ),
            )
        )

        return {
            **base_chart,

            "vargas": (
                vargas
            ),
        }

    # =========================================================
    # SUPPORTED CHARTS
    # =========================================================

    def get_supported_charts(
        self,
    ) -> list[dict]:

        return [
            {
                "division": division,
                "code": f"D{division}",
                "name": VARGA_NAMES[
                    division
                ],
            }
            for division in sorted(
                VARGA_CALCULATORS.keys()
            )
        ]