import random
import datetime as dt
import requests

BASE = "http://localhost:5400"

BRANDS = ["Toyota", "BMW", "Mercedes", "Lada", "Kia", "Hyundai", "Ford", "Audi"]
WORKS = ["ТО", "Замена масла", "Диагностика", "Тормоза", "Подвеска", "Электрика", "Шиномонтаж"]

def post(path, json):
    r = requests.post(BASE + path, json=json, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    random.seed(42)

    car_ids = []
    for i in range(200):
        num = f"AA{i:04d}BB"
        car = {
            "number": num,
            "brand": random.choice(BRANDS),
            "year": random.randint(1998, 2024),
            "owner_name": f"Owner {i}"
        }
        car_ids.append(post("/cars", car)["id"])

    mech_ids = []
    for i in range(40):
        mech = {
            "employee_no": f"EMP{i:04d}",
            "full_name": f"Mechanic {i}",
            "experience_years": random.randint(0, 25),
            "grade": random.randint(1, 6),
        }
        mech_ids.append(post("/mechanics", mech)["id"])

    for i in range(2000):
        issue = dt.date.today() - dt.timedelta(days=random.randint(0, 365))
        planned = issue + dt.timedelta(days=random.randint(1, 14))
        actual = planned + dt.timedelta(days=random.randint(-2, 5))
        if random.random() < 0.2:
            actual = None

        meta = {
            "symptoms": random.choice(["стук", "вибрация", "не заводится", "тянет в сторону", "шум", "нет тяги"]),
            "comment": f"client note #{i} " + random.choice(["urgent", "check", "repeat", "noise", "oil"]),
            "parts": [{"name": random.choice(["filter", "pads", "belt", "spark"]), "qty": random.randint(1, 4)}]
        }

        order = {
            "car_id": random.choice(car_ids),
            "mechanic_id": random.choice(mech_ids),
            "cost": round(random.uniform(10, 1500), 2),
            "issue_date": str(issue),
            "work_type": random.choice(WORKS),
            "planned_end_date": str(planned),
            "actual_end_date": (str(actual) if actual else None),
            "meta": meta
        }
        post("/orders", order)

    print("Seed done")

if __name__ == "__main__":
    main()
