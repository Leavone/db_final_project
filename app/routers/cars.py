from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..deps import get_db
from ..models import Car

router = APIRouter()

@router.post("", response_model=dict)
def create_car(payload: dict, db: Session = Depends(get_db)):
    car = Car(**payload)
    db.add(car)
    db.commit()
    db.refresh(car)
    return {"id": car.id}

@router.get("", response_model=list[dict])
def list_cars(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc"),
):
    sort_col = getattr(Car, sort_by, None)
    if sort_col is None:
        raise HTTPException(400, "Invalid sort_by")

    q = select(Car)
    q = q.order_by(sort_col.asc() if sort_dir == "asc" else sort_col.desc())
    q = q.limit(limit).offset(offset)

    rows = db.execute(q).scalars().all()
    return [
        {"id": c.id, "number": c.number, "brand": c.brand, "year": c.year, "owner_name": c.owner_name}
        for c in rows
    ]

@router.get("/{car_id}", response_model=dict)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    return {"id": car.id, "number": car.number, "brand": car.brand, "year": car.year, "owner_name": car.owner_name}

@router.put("/{car_id}", response_model=dict)
def update_car(car_id: int, payload: dict, db: Session = Depends(get_db)):
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    for k, v in payload.items():
        setattr(car, k, v)
    db.commit()
    return {"status": "ok"}

@router.delete("/{car_id}", response_model=dict)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(404, "Car not found")
    db.delete(car)
    db.commit()
    return {"status": "ok"}
