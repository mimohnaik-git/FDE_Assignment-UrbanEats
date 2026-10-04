from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
    StrictStr,
    field_validator,
)


def iso_timestamp(value):
    if not isinstance(value, (str, datetime)):
        raise ValueError("ISO timestamp required")
    if isinstance(value, str) and "T" not in value:
        raise ValueError("Full ISO timestamp required")
    return value


class PlacementOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_id: StrictStr = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    placed_at: datetime
    restaurant_name: StrictStr = Field(min_length=1, max_length=100)
    delivery_zone: Literal["North", "South", "East", "West", "Central"]
    order_value: StrictInt | StrictFloat = Field(gt=0, le=5000)
    payment_method: Literal["Cash", "Card", "UPI", "Wallet"]
    discount_applied: StrictInt | StrictFloat = Field(ge=0, le=5000)

    _timestamp = field_validator("placed_at", mode="before")(iso_timestamp)


class CurrentBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["placement-v1"]
    source_batch_id: StrictStr = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    source_dataset: StrictStr = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")
    source_mode: Literal["synthetic_demo", "configured_source"]
    generated_at: datetime
    target_population: Literal["Delivered_vs_Cancelled_conditional"]
    orders: list[PlacementOrder] = Field(min_length=1, max_length=10000)

    _timestamp = field_validator("generated_at", mode="before")(iso_timestamp)
