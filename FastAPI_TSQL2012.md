# Prompt: FastAPI + TSQL2012 SQLite Deployment

Build a FastAPI + SQLAlchemy + SQLite project based on the provided `TSQL2012.sql` file (UTF-16 encoding).

### 1. Database Setup (`setup_db.py`)
Rewrite `setup_db.py` to:
- Open `TSQL2012.sql` with `utf-16` encoding.
- Use a character-by-character parser (not a simple regex split) to extract `INSERT INTO` statements for exactly 4 tables: `HR.Employees`, `Sales.Customers`, `Sales.Orders`, and `Sales.OrderDetails`.
- Mapping: `HR.Employees` -> `Employees`, `Sales.Customers` -> `Customers`, `Sales.Orders` -> `Orders`, `Sales.OrderDetails` -> `OrderDetails`.
- **Parsing Logic:** 
    - Handle `N'string'` literals and escaped single quotes (`''`).
    - Respect commas inside quoted strings (e.g., addresses like '123 Main St, Apt 4').
    - Convert T-SQL dates (e.g., `20060704 00:00:00.000`) to SQLite format (`2006-07-04`).
    - Strip all `N` prefixes and surrounding single quotes from values.
- **Expected Counts:** 9 Employees, 91 Customers, 830 Orders, 2155 OrderDetails.

### 2. Application Files
- **`models.py`**: SQLAlchemy models matching the 4 PascalCase tables.
- **`schemas.py`**: Pydantic V2 models (`ConfigDict`, `from_attributes=True`).
- **`crud.py`**: Basic CRUD + advanced analytics (Employee Sales, Top Products).
- **`main.py`**: FastAPI app with versioned `/v0/` endpoints.
- **`database.py`**: SQLite connection string `sqlite:///./TSQL2012.db`.

### 3. Deployment & DevOps
- **`requirements.txt`**: Include `fastapi[standard]`, `sqlalchemy`, `pydantic`.
- **`build.sh`**: A bash script that runs `python setup_db.py` to initialize the database before deployment.
- **`render.yaml`**: Configuration for Render (Web Service):
    - **Runtime**: `Python 3`
    - **Build Command**: `bash build.sh`
    - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Other Files**: `.gitignore`, `.dockerignore`, `Dockerfile`, `test_crud.py` (pytest).
