from sqlalchemy.orm import Session
from sqlalchemy import func
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
