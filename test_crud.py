import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_TSQL2012.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_TSQL2012.db"):
        os.remove("./test_TSQL2012.db")

def test_create_employee():
    response = client.post(
        "/v0/employees/",
        json={
            "lastname": "Doe",
            "firstname": "John",
            "title": "Sales Manager",
            "titleofcourtesy": "Mr.",
            "birthdate": "1980-01-01",
            "hiredate": "2020-01-01",
            "address": "123 Main St",
            "city": "Seattle",
            "country": "USA",
            "phone": "(206) 555-0100"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["lastname"] == "Doe"
    assert "empid" in data

def test_read_employees():
    response = client.get("/v0/employees/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_create_customer():
    response = client.post(
        "/v0/customers/",
        json={
            "companyname": "Test Co",
            "contactname": "Jane Smith",
            "contacttitle": "Owner",
            "address": "456 Test Ave",
            "city": "Portland",
            "country": "USA",
            "phone": "(503) 555-0199"
        },
    )
    assert response.status_code == 200
    assert response.json()["companyname"] == "Test Co"

def test_create_order():
    # We need an employee and potentially a customer (custid can be null in schema but good to have)
    emp_id = 1 # From previous test
    response = client.post(
        "/v0/orders/",
        json={
            "custid": 1,
            "empid": 1,
            "orderdate": "2023-01-01",
            "requireddate": "2023-01-10",
            "shipperid": 1,
            "freight": 10.5,
            "shipname": "Test Co",
            "shipaddress": "456 Test Ave",
            "shipcity": "Portland",
            "shipcountry": "USA",
            "details": [
                {
                    "productid": 1,
                    "unitprice": 20.0,
                    "qty": 5,
                    "discount": 0.0
                }
            ]
        },
    )
    assert response.status_code == 200
    assert response.json()["orderid"] is not None
