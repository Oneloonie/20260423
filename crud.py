from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date
import models, schemas

# Employee CRUD
def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.empid == employee_id).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# Customer CRUD
def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.custid == customer_id).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

# Order CRUD
def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.orderid == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate):
    order_data = order.model_dump()
    details_data = order_data.pop("details")
    db_order = models.Order(**order_data)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    for detail in details_data:
        db_detail = models.OrderDetail(**detail, orderid=db_order.orderid)
        db.add(db_detail)
    
    db.commit()
    db.refresh(db_order)
    return db_order

# Advanced Queries
def get_orders_by_customer(db: Session, customer_id: int):
    return db.query(models.Order).filter(models.Order.custid == customer_id).all()

def get_employee_total_sales(db: Session):
    return db.query(
        models.Employee.firstname,
        models.Employee.lastname,
        func.sum(models.OrderDetail.unitprice * models.OrderDetail.qty).label("total_sales")
    ).join(models.Order, models.Employee.empid == models.Order.empid)\
     .join(models.OrderDetail, models.Order.orderid == models.OrderDetail.orderid)\
     .group_by(models.Employee.empid).all()

def get_top_selling_products(db: Session, limit: int = 5):
    return db.query(
        models.OrderDetail.productid,
        func.sum(models.OrderDetail.qty).label("total_qty")
    ).group_by(models.OrderDetail.productid)\
     .order_by(func.sum(models.OrderDetail.qty).desc())\
     .limit(limit).all()

# ── Analytics Cases 1–8 ──────────────────────────────────────────────────────

# Case 1 — all orders placed on the last day of activity
def get_last_day_orders(db: Session):
    max_date = db.query(func.max(models.Order.orderdate)).scalar()
    return db.query(models.Order).filter(models.Order.orderdate == max_date).all()

# Case 2 — all orders by customer(s) who placed the most orders (handles ties)
def get_top_customer_orders(db: Session):
    counts = (db.query(models.Order.custid, func.count().label("cnt"))
              .group_by(models.Order.custid).subquery())
    max_cnt = db.query(func.max(counts.c.cnt)).scalar()
    top_custs = (db.query(models.Order.custid)
                 .group_by(models.Order.custid)
                 .having(func.count() == max_cnt).all())
    ids = [r.custid for r in top_custs]
    return db.query(models.Order).filter(models.Order.custid.in_(ids)).all()

# Case 3 — employees who placed no orders on or after 2008-05-01
def get_inactive_employees(db: Session):
    cutoff = date(2008, 5, 1)
    active = db.query(models.Order.empid).filter(
        models.Order.orderdate >= cutoff).subquery()
    return db.query(models.Employee).filter(
        ~models.Employee.empid.in_(active)).all()

# Case 4 — countries with customers but no employees
def get_customer_only_countries(db: Session):
    emp_countries = db.query(models.Employee.country).subquery()
    return (db.query(models.Customer.country.distinct())
              .filter(~models.Customer.country.in_(emp_countries)).all())

# Case 5 — each customer's orders placed on their last day of activity
def get_customer_last_day_orders(db: Session):
    sub = (db.query(models.Order.custid,
                    func.max(models.Order.orderdate).label("last_date"))
             .group_by(models.Order.custid).subquery())
    return (db.query(models.Order)
              .join(sub, and_(models.Order.custid == sub.c.custid,
                              models.Order.orderdate == sub.c.last_date))
              .order_by(models.Order.custid).all())

# Case 6 — customers who ordered in 2007 but not in 2008
def get_customers_2007_not_2008(db: Session):
    in_2008 = (db.query(models.Order.custid)
                 .filter(func.strftime('%Y', models.Order.orderdate) == '2008')
                 .subquery())
    return (db.query(models.Order.custid.distinct())
              .filter(func.strftime('%Y', models.Order.orderdate) == '2007')
              .filter(~models.Order.custid.in_(in_2008)).all())

# Case 7 — customers who ordered a specific product
def get_customers_by_product(db: Session, product_id: int):
    return (db.query(models.Order.custid.distinct())
              .join(models.OrderDetail, models.Order.orderid == models.OrderDetail.orderid)
              .filter(models.OrderDetail.productid == product_id).all())

# Case 8 — running total quantity per customer per month
def get_running_total_qty(db: Session):
    yr_month = func.strftime('%Y-%m', models.Order.orderdate).label("yr_month")
    monthly = (db.query(
                   models.Order.custid, yr_month,
                   func.sum(models.OrderDetail.qty).label("monthly_qty"))
               .join(models.OrderDetail, models.Order.orderid == models.OrderDetail.orderid)
               .group_by(models.Order.custid, yr_month)
               .order_by(models.Order.custid, yr_month).all())
    running = {}
    result = []
    for row in monthly:
        running[row.custid] = running.get(row.custid, 0) + row.monthly_qty
        result.append({
            "custid": row.custid,
            "yr_month": row.yr_month,
            "monthly_qty": row.monthly_qty,
            "running_total": running[row.custid]
        })
    return result
