from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Employee
class EmployeeBase(BaseModel):
    lastname: str
    firstname: str
    title: str
    titleofcourtesy: str
    birthdate: str
    hiredate: str
    address: str
    city: str
    region: Optional[str] = None
    postalcode: Optional[str] = None
    country: str
    phone: str
    mgrid: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    empid: int
    model_config = ConfigDict(from_attributes=True)

# Customer
class CustomerBase(BaseModel):
    companyname: str
    contactname: str
    contacttitle: str
    address: str
    city: str
    region: Optional[str] = None
    postalcode: Optional[str] = None
    country: str
    phone: str
    fax: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    custid: int
    model_config = ConfigDict(from_attributes=True)

# OrderDetail
class OrderDetailBase(BaseModel):
    productid: int
    unitprice: float
    qty: int
    discount: float

class OrderDetailCreate(OrderDetailBase):
    pass

class OrderDetail(OrderDetailBase):
    orderid: int
    model_config = ConfigDict(from_attributes=True)

# Order
class OrderBase(BaseModel):
    custid: Optional[int] = None
    empid: int
    orderdate: str
    requireddate: str
    shippeddate: Optional[str] = None
    shipperid: int
    freight: float
    shipname: str
    shipaddress: str
    shipcity: str
    shipregion: Optional[str] = None
    shippostalcode: Optional[str] = None
    shipcountry: str

class OrderCreate(OrderBase):
    details: List[OrderDetailCreate]

class Order(OrderBase):
    orderid: int
    details: List[OrderDetail] = []
    model_config = ConfigDict(from_attributes=True)
