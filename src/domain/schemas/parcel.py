from pydantic import BaseModel, Field


class ParcelTypeSchemas(BaseModel):
    id: int
    name: str


class ParcelCreateSchemas(BaseModel):
    name: str = Field(min_length=1, description="Название посылки")
    weight_kg: float = Field(gt=0, description="Вес в килограммах")
    type_id: int = Field(gt=0, description="ID типа посылки")
    content_price_usd: float = Field(ge=0, description="Стоимость содержимого в USD")


class ParcelResponseSchemas(BaseModel):
    id: int
    name: str
    weight_kg: float
    type_id: int
    type_name: str
    content_price_usd: float
    delivery_cost_rub: float | None = None
