from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_, cast, Text, update
from ..deps import get_db
from ..models import Order, Car, Mechanic
from ..schemas import OrderOut, OrderDetailsOut, CarOut, MechanicOut

router = APIRouter()

def apply_sort(model, sort_by: str, sort_dir: str):
    col = getattr(model, sort_by, None)
    if col is None:
        raise HTTPException(400, f"Invalid sort_by: {sort_by}")
    return col.asc() if sort_dir.lower() == "asc" else col.desc()

@router.get("/orders/filter", response_model=list[OrderOut])
def filter_orders(
    db: Session = Depends(get_db),
    brand: str | None = None,
    min_cost: float | None = Query(None, ge=0),
    max_cost: float | None = Query(None, ge=0),
    grade_gte: int | None = Query(None, ge=1),
    issue_from: date | None = None,
    issue_to: date | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc"),
):
    conditions = []

    q = select(Order).join(Car, Order.car_id == Car.id).join(Mechanic, Order.mechanic_id == Mechanic.id)

    if brand:
        conditions.append(Car.brand == brand)
    if min_cost is not None:
        conditions.append(Order.cost >= min_cost)
    if max_cost is not None:
        conditions.append(Order.cost <= max_cost)
    if grade_gte is not None:
        conditions.append(Mechanic.grade >= grade_gte)
    if issue_from:
        conditions.append(Order.issue_date >= issue_from)
    if issue_to:
        conditions.append(Order.issue_date <= issue_to)

    if conditions:
        q = q.where(and_(*conditions))

    q = q.order_by(apply_sort(Order, sort_by, sort_dir)).limit(limit).offset(offset)
    rows = db.execute(q).scalars().all()

    return [
        OrderOut(
            id=o.id, car_id=o.car_id, mechanic_id=o.mechanic_id,
            cost=float(o.cost), issue_date=o.issue_date, work_type=o.work_type,
            planned_end_date=o.planned_end_date, actual_end_date=o.actual_end_date,
            status=o.status, meta=o.meta
        )
        for o in rows
    ]

@router.get("/orders/with-details", response_model=list[OrderDetailsOut])
def orders_with_details(
    db: Session = Depends(get_db),
    issue_from: date | None = None,
    issue_to: date | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc"),
):
    q = (
        select(Order)
        .options(joinedload(Order.car), joinedload(Order.mechanic))
    )
    if issue_from:
        q = q.where(Order.issue_date >= issue_from)
    if issue_to:
        q = q.where(Order.issue_date <= issue_to)

    q = q.order_by(apply_sort(Order, sort_by, sort_dir)).limit(limit).offset(offset)
    rows = db.execute(q).scalars().all()

    result = []
    for o in rows:
        result.append(
            OrderDetailsOut(
                id=o.id,
                cost=float(o.cost),
                issue_date=o.issue_date,
                work_type=o.work_type,
                planned_end_date=o.planned_end_date,
                actual_end_date=o.actual_end_date,
                status=o.status,
                meta=o.meta,
                car=CarOut(id=o.car.id, number=o.car.number, brand=o.car.brand, year=o.car.year, owner_name=o.car.owner_name),
                mechanic=MechanicOut(id=o.mechanic.id, employee_no=o.mechanic.employee_no, full_name=o.mechanic.full_name, experience_years=o.mechanic.experience_years, grade=o.mechanic.grade)
            )
        )
    return result

@router.post("/orders/close-overdue", response_model=dict)
def close_overdue_orders(db: Session = Depends(get_db)):
    stmt = (
        update(Order)
        .where(and_(Order.actual_end_date.is_not(None), Order.actual_end_date > Order.planned_end_date))
        .values(status="done")
    )
    res = db.execute(stmt)
    db.commit()
    return {"updated": res.rowcount}

@router.get("/revenue/by-mechanic", response_model=list[dict])
def revenue_by_mechanic(
    db: Session = Depends(get_db),
    issue_from: date | None = None,
    issue_to: date | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort_dir: str = Query("desc"),
):
    q = (
        select(
            Mechanic.id.label("mechanic_id"),
            Mechanic.full_name.label("full_name"),
            func.sum(Order.cost).label("revenue"),
            func.count(Order.id).label("orders_count"),
        )
        .join(Order, Order.mechanic_id == Mechanic.id)
        .group_by(Mechanic.id, Mechanic.full_name)
    )
    if issue_from:
        q = q.where(Order.issue_date >= issue_from)
    if issue_to:
        q = q.where(Order.issue_date <= issue_to)

    q = q.order_by(func.sum(Order.cost).asc() if sort_dir == "asc" else func.sum(Order.cost).desc())
    q = q.limit(limit).offset(offset)

    rows = db.execute(q).all()
    return [
        {"mechanic_id": r.mechanic_id, "full_name": r.full_name, "revenue": float(r.revenue or 0), "orders_count": int(r.orders_count)}
        for r in rows
    ]

@router.get("/orders/search-meta", response_model=list[OrderOut])
def search_orders_in_meta(
    pattern: str = Query(..., description="psql regex for ~ operator"),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    cond = cast(Order.meta, Text).op("~")(pattern)
    q = select(Order).where(cond).order_by(Order.id.asc()).limit(limit).offset(offset)
    rows = db.execute(q).scalars().all()
    return [
        OrderOut(
            id=o.id, car_id=o.car_id, mechanic_id=o.mechanic_id,
            cost=float(o.cost), issue_date=o.issue_date, work_type=o.work_type,
            planned_end_date=o.planned_end_date, actual_end_date=o.actual_end_date,
            status=o.status, meta=o.meta
        )
        for o in rows
    ]
