from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Employee(Base):
    __tablename__ = "Employees"

    empid = Column(Integer, primary_key=True, index=True)
    lastname = Column(String)
    firstname = Column(String)
    title = Column(String)
    titleofcourtesy = Column(String)
    birthdate = Column(String)
    hiredate = Column(String)
    address = Column(String)
    city = Column(String)
    region = Column(String, nullable=True)
    postalcode = Column(String, nullable=True)
    country = Column(String)
    phone = Column(String)
    mgrid = Column(Integer, ForeignKey("Employees.empid"), nullable=True)

    manager = relationship("Employee", remote_side=[empid])
    orders = relationship("Order", back_populates="employee")

class Customer(Base):
    __tablename__ = "Customers"

    custid = Column(Integer, primary_key=True, index=True)
    companyname = Column(String)
    contactname = Column(String)
    contacttitle = Column(String)
    address = Column(String)
    city = Column(String)
    region = Column(String, nullable=True)
    postalcode = Column(String, nullable=True)
    country = Column(String)
    phone = Column(String)
    fax = Column(String, nullable=True)

    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "Orders"

    orderid = Column(Integer, primary_key=True, index=True)
    custid = Column(Integer, ForeignKey("Customers.custid"))
    empid = Column(Integer, ForeignKey("Employees.empid"))
    orderdate = Column(String)
    requireddate = Column(String)
    shippeddate = Column(String, nullable=True)
    shipperid = Column(Integer)
    freight = Column(Float)
    shipname = Column(String)
    shipaddress = Column(String)
    shipcity = Column(String)
    shipregion = Column(String, nullable=True)
    shippostalcode = Column(String, nullable=True)
    shipcountry = Column(String)

    customer = relationship("Customer", back_populates="orders")
    employee = relationship("Employee", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order")

class OrderDetail(Base):
    __tablename__ = "OrderDetails"

    orderid = Column(Integer, ForeignKey("Orders.orderid"), primary_key=True)
    productid = Column(Integer, primary_key=True)
    unitprice = Column(Float)
    qty = Column(Integer)
    discount = Column(Float)

    order = relationship("Order", back_populates="details")
