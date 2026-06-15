from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ParcelType(Base):
    __tablename__ = "parcel_type"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    parcels = relationship("Parcel", back_populates="type")


class Parcel(Base):
    session_id: Mapped[str] = mapped_column(String(255), nullable=False)
    __tablename__ = "parcel"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    weight_kg = Column(Float)
    type_id = Column(Integer, ForeignKey("parcel_type.id"))
    content_value_usd = Column(Float)
    delivery_cost_rub = Column(Float, nullable=True)
    user_session_id = Column(String)
    created_at = Column(DateTime, default=datetime)

    type = relationship("ParcelType", back_populates="parcels")
