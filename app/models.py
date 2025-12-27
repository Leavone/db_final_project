from sqlalchemy import String, Integer, ForeignKey, Date, Numeric, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Car(Base):
    __tablename__ = "cars"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    brand: Mapped[str] = mapped_column(String(64), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    owner_name: Mapped[str] = mapped_column(String(128), index=True)

    orders = relationship("Order", back_populates="car", cascade="all,delete")

class Mechanic(Base):
    __tablename__ = "mechanics"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(128), index=True)
    experience_years: Mapped[int] = mapped_column(Integer, index=True)
    grade: Mapped[int] = mapped_column(Integer, index=True)

    orders = relationship("Order", back_populates="mechanic", cascade="all,delete")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)

    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), index=True)
    mechanic_id: Mapped[int] = mapped_column(ForeignKey("mechanics.id", ondelete="CASCADE"), index=True)

    cost: Mapped[float] = mapped_column(Numeric(12, 2), index=True)
    issue_date: Mapped["Date"] = mapped_column(Date, index=True)
    work_type: Mapped[str] = mapped_column(String(128), index=True)
    planned_end_date: Mapped["Date"] = mapped_column(Date, index=True)
    actual_end_date: Mapped["Date | None"] = mapped_column(Date, nullable=True, index=True)

    meta: Mapped[dict] = mapped_column(JSONB, default=dict)

    car = relationship("Car", back_populates="orders")
    mechanic = relationship("Mechanic", back_populates="orders")

Index("ix_orders_car_mechanic", Order.car_id, Order.mechanic_id)
