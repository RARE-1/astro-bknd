from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field


class BirthData(BaseModel):
    date: date
    time: time

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    # For today we require the UTC offset explicitly.
    # India = 5.5
    # Example: New Delhi => 5.5
    timezone_offset: float = Field(ge=-14, le=14)

    ayanamsha: Literal["lahiri"] = "lahiri"

    # Keep node convention explicit.
    node_type: Literal["mean", "true"] = "mean"