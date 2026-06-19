from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ParcelType(Base):
    __tablename__ = "parcel_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Связь с посылками
    parcels: Mapped[list["Parcel"]] = relationship("Parcel", back_populates="parcel_type")


class Parcel(Base):
    __tablename__ = "parcel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("parcel_type.id"), nullable=False)
    content_value_usd: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_cost_rub: Mapped[float | None] = mapped_column(Float, nullable=True)
    user_session_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Связь с типом посылки
    parcel_type: Mapped["ParcelType"] = relationship("ParcelType", back_populates="parcels")
