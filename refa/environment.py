from pydantic import BaseModel, Field
import datetime as dt


class Environment(BaseModel):
    """Env‑tab – weather & geographic data."""
    date: dt.date = Field(default_factory=dt.date.today)
    latitude: float = Field(..., ge=-90, le=90)
    elevation_m: float = Field(..., ge=0)
    wind_speed_m_per_s: float = Field(..., ge=0)
    wind_angle: int = Field(..., ge=0, le=90)
    cw_angle_direction_rel_to_north: int = Field(..., ge=0, le=90)
    hour: int = Field(..., ge=0, le=24)
    atmosphere: dict = Field(...)
    ambient_temperature_c: float = Field(...)