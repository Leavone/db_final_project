from __future__ import annotations
from datetime import date
from pydantic import BaseModel, Field

class CarCreate(BaseModel):
    number: str
    brand: str
    year: int = Field(ge=1900, le=2100)
    owner_name: str

class CarUpdate(BaseModel):
    number: str | None = None
    brand: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    owner_name: str | None = None

class CarOut(BaseModel):
    id: int
    number: str
    brand: str
    year: int
    owner_name: str

class MechanicCreate(BaseModel):
    employee_no: str
    full_name: str
    experience_years: int = Field(ge=0, le=80)
    grade: int = Field(ge=1, le=10)

class MechanicUpdate(BaseModel):
    employee_no: str | None = None
    full_name: str | None = None
    experience_years: int | None = Field(default=None, ge=0, le=80)
    grade: int | None = Field(default=None, ge=1, le=10)

class MechanicOut(BaseModel):
    id: int
    employee_no: str
    full_name: str
    experience_years: int
    grade: int

class OrderCreate(BaseModel):
    car_id: int
    mechanic_id: int
    cost: float = Field(ge=0)
    issue_date: date
    work_type: str
    planned_end_date: date
    actual_end_date: date | None = None
    status: str | None = None
    meta: dict = Field(default_factory=dict)

class OrderUpdate(BaseModel):
    car_id: int | None = None
    mechanic_id: int | None = None
    cost: float | None = Field(default=None, ge=0)
    issue_date: date | None = None
    work_type: str | None = None
    planned_end_date: date | None = None
    actual_end_date: date | None = None
    status: str | None = None
    meta: dict | None = None

class OrderOut(BaseModel):
    id: int
    car_id: int
    mechanic_id: int
    cost: float
    issue_date: date
    work_type: str
    planned_end_date: date
    actual_end_date: date | None
    status: str
    meta: dict

class OrderDetailsOut(BaseModel):
    id: int
    cost: float
    issue_date: date
    work_type: str
    planned_end_date: date
    actual_end_date: date | None
    status: str
    meta: dict
    car: CarOut
    mechanic: MechanicOut
