from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..deps import get_db
from ..models import Mechanic
from ..schemas import MechanicCreate, MechanicUpdate, MechanicOut

router = APIRouter()

def apply_sort(model, sort_by: str, sort_dir: str):
    col = getattr(model, sort_by, None)
    if col is None:
        raise HTTPException(400, f"Invalid sort_by: {sort_by}")
    return col.asc() if sort_dir.lower() == "asc" else col.desc()

@router.post("", response_model=MechanicOut)
def create_mechanic(payload: MechanicCreate, db: Session = Depends(get_db)):
    m = Mechanic(**payload.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return MechanicOut(id=m.id, employee_no=m.employee_no, full_name=m.full_name, experience_years=m.experience_years, grade=m.grade)

@router.get("", response_model=list[MechanicOut])
def list_mechanics(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc"),
):
    q = select(Mechanic).order_by(apply_sort(Mechanic, sort_by, sort_dir)).limit(limit).offset(offset)
    rows = db.execute(q).scalars().all()
    return [MechanicOut(id=x.id, employee_no=x.employee_no, full_name=x.full_name, experience_years=x.experience_years, grade=x.grade) for x in rows]

@router.get("/{mechanic_id}", response_model=MechanicOut)
def get_mechanic(mechanic_id: int, db: Session = Depends(get_db)):
    m = db.get(Mechanic, mechanic_id)
    if not m:
        raise HTTPException(404, "Mechanic not found")
    return MechanicOut(id=m.id, employee_no=m.employee_no, full_name=m.full_name, experience_years=m.experience_years, grade=m.grade)

@router.put("/{mechanic_id}", response_model=MechanicOut)
def update_mechanic(mechanic_id: int, payload: MechanicUpdate, db: Session = Depends(get_db)):
    m = db.get(Mechanic, mechanic_id)
    if not m:
        raise HTTPException(404, "Mechanic not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return MechanicOut(id=m.id, employee_no=m.employee_no, full_name=m.full_name, experience_years=m.experience_years, grade=m.grade)

@router.delete("/{mechanic_id}", response_model=dict)
def delete_mechanic(mechanic_id: int, db: Session = Depends(get_db)):
    m = db.get(Mechanic, mechanic_id)
    if not m:
        raise HTTPException(404, "Mechanic not found")
    db.delete(m)
    db.commit()
    return {"status": "ok"}
