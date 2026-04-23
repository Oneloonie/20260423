from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas
from database import engine, get_db

# Create tables (though setup_db.py handles most of it, this ensures Base is consistent)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TSQL2012 API", version="0.1.0")

# Employees
@app.get("/v0/employees/", response_model=List[schemas.Employee])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_employees(db, skip=skip, limit=limit)

@app.get("/v0/employees/{employee_id}", response_model=schemas.Employee)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.post("/v0/employees/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db=db, employee=employee)

# Customers
@app.get("/v0/customers/", response_model=List[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_customers(db, skip=skip, limit=limit)

@app.get("/v0/customers/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.post("/v0/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, customer=customer)

# Orders
@app.get("/v0/orders/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_orders(db, skip=skip, limit=limit)

@app.post("/v0/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

# Advanced
@app.get("/v0/analytics/employee-sales")
def get_employee_sales(db: Session = Depends(get_db)):
    results = crud.get_employee_total_sales(db)
    return [{"name": f"{r[0]} {r[1]}", "total_sales": r[2]} for r in results]

@app.get("/v0/analytics/top-products")
def get_top_products(limit: int = 5, db: Session = Depends(get_db)):
    results = crud.get_top_selling_products(db, limit=limit)
    return [{"product_id": r[0], "total_qty": r[1]} for r in results]

# ── Analytics Cases 1–8 ──────────────────────────────────────────────────────

@app.get("/v0/analytics/last-day-orders")
def last_day_orders(db: Session = Depends(get_db)):
    return crud.get_last_day_orders(db)

@app.get("/v0/analytics/top-customer-orders")
def top_customer_orders(db: Session = Depends(get_db)):
    return crud.get_top_customer_orders(db)

@app.get("/v0/analytics/inactive-employees")
def inactive_employees(db: Session = Depends(get_db)):
    return crud.get_inactive_employees(db)

@app.get("/v0/analytics/customer-only-countries")
def customer_only_countries(db: Session = Depends(get_db)):
    results = crud.get_customer_only_countries(db)
    return [r.country for r in results]

@app.get("/v0/analytics/customer-last-day-orders")
def customer_last_day_orders(db: Session = Depends(get_db)):
    return crud.get_customer_last_day_orders(db)

@app.get("/v0/analytics/customers-2007-not-2008")
def customers_2007_not_2008(db: Session = Depends(get_db)):
    results = crud.get_customers_2007_not_2008(db)
    return [r.custid for r in results]

@app.get("/v0/analytics/customers-product/{product_id}")
def customers_by_product(product_id: int, db: Session = Depends(get_db)):
    results = crud.get_customers_by_product(db, product_id)
    return [r.custid for r in results]

@app.get("/v0/analytics/running-total-qty")
def running_total_qty(db: Session = Depends(get_db)):
    return crud.get_running_total_qty(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
