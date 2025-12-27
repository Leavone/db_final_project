from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..deps import get_db
from ..models import Order, Car, Mechanic
from ..schemas import OrderCreate, OrderUpdate, OrderOut

router = APIRouter()

def apply_sort(model, sort_by: str, sort_dir: str):
    col = getattr(model, sort_by, None)
    if col is None:
        raise HTTPException(400, f"Invalid sort_by: {sort_by}")
    return col.asc() if sort_dir.lower() == "asc" else col.desc()

@router.post("", response_model=OrderOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    if not db.get(Car, payload.car_id):
        raise HTTPException(400, "car_id does not exist")
    if not db.get(Mechanic, payload.mechanic_id):
        raise HTTPException(400, "mechanic_id does not exist")

    data = payload.model_dump()
    if data.get("status") is None:
        data["status"] = "new"
    o = Order(**data)
    db.add(o)
    db.commit()
    db.refresh(o)
    return OrderOut(
        id=o.id, car_id=o.car_id, mechanic_id=o.mechanic_id,
        cost=float(o.cost), issue_date=o.issue_date, work_type=o.work_type,
        planned_end_date=o.planned_end_date, actual_end_date=o.actual_end_date,
        status=o.status, meta=o.meta
    )

@router.get("", response_model=list[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc"),
):
    q = select(Order).order_by(apply_sort(Order, sort_by, sort_dir)).limit(limit).offset(offset)
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

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.get(Order, order_id)
    if not o:
        raise HTTPException(404, "Order not found")
    return OrderOut(
        id=o.id, car_id=o.car_id, mechanic_id=o.mechanic_id,
        cost=float(o.cost), issue_date=o.issue_date, work_type=o.work_type,
        planned_end_date=o.planned_end_date, actual_end_date=o.actual_end_date,
        status=o.status, meta=o.meta
    )

@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db)):
    o = db.get(Order, order_id)
    if not o:
        raise HTTPException(404, "Order not found")

    data = payload.model_dump(exclude_unset=True)

    if "car_id" in data and not db.get(Car, data["car_id"]):
        raise HTTPException(400, "car_id does not exist")
    if "mechanic_id" in data and not db.get(Mechanic, data["mechanic_id"]):
        raise HTTPException(400, "mechanic_id does not exist")

    for k, v in data.items():
        setattr(o, k, v)

    db.commit()
    db.refresh(o)

    return OrderOut(
        id=o.id, car_id=o.car_id, mechanic_id=o.mechanic_id,
        cost=float(o.cost), issue_date=o.issue_date, work_type=o.work_type,
        planned_end_date=o.planned_end_date, actual_end_date=o.actual_end_date,
        status=o.status, meta=o.meta
    )

@router.delete("/{order_id}", response_model=dict)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    o = db.get(Order, order_id)
    if not o:
        raise HTTPException(404, "Order not found")
    db.delete(o)
    db.commit()
    return {"status": "ok"}
