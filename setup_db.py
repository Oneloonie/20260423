import sqlite3
import re
import os

def setup_database():
    sql_file = 'TSQL2012.sql'
    db_file = 'TSQL2012.db'

    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except PermissionError:
            print(f"Error: {db_file} is in use.")
            return

    with open(sql_file, 'r', encoding='utf-16') as f:
        content = f.read()

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE Employees (
        empid INTEGER PRIMARY KEY, lastname TEXT, firstname TEXT, title TEXT, titleofcourtesy TEXT,
        birthdate TEXT, hiredate TEXT, address TEXT, city TEXT, region TEXT, postalcode TEXT,
        country TEXT, phone TEXT, mgrid INTEGER)""")
    
    cursor.execute("""CREATE TABLE Customers (
        custid INTEGER PRIMARY KEY, companyname TEXT, contactname TEXT, contacttitle TEXT,
        address TEXT, city TEXT, region TEXT, postalcode TEXT, country TEXT, phone TEXT, fax TEXT)""")
    
    cursor.execute("""CREATE TABLE Orders (
        orderid INTEGER PRIMARY KEY, custid INTEGER, empid INTEGER, orderdate TEXT,
        requireddate TEXT, shippeddate TEXT, shipperid INTEGER, freight REAL, shipname TEXT,
        shipaddress TEXT, shipcity TEXT, shipregion TEXT, shippostalcode TEXT, shipcountry TEXT)""")
    
    cursor.execute("""CREATE TABLE OrderDetails (
        orderid INTEGER, productid INTEGER, unitprice REAL, qty INTEGER, discount REAL,
        PRIMARY KEY (orderid, productid))""")

    def clean_val(v):
        v = v.strip()
        if v.upper() == "NULL": return None
        # Remove N prefix
        if v.startswith("N'"): v = v[1:]
        # Remove surrounding quotes and handle escaped single quotes
        while v.startswith("'") and v.endswith("'"):
            v = v[1:-1]
        v = v.replace("''", "'")
        # Format dates: "20060704 00:00:00.000" -> "2006-07-04"
        if v and re.match(r'^\d{8}\s.*', v):
            v = f"{v[0:4]}-{v[4:6]}-{v[6:8]}"
        return v

    def split_sql_values(s):
        results = []
        current = []
        in_string = False
        i = 0
        while i < len(s):
            char = s[i]
            if char == "'" and not in_string:
                in_string = True
                current.append(char)
            elif char == "'" and in_string:
                # Check for escaped single quote ''
                if i + 1 < len(s) and s[i+1] == "'":
                    current.append("''")
                    i += 1
                else:
                    in_string = False
                    current.append(char)
            elif char == "," and not in_string:
                results.append("".join(current).strip())
                current = []
            else:
                current.append(char)
            i += 1
        results.append("".join(current).strip())
        return results

    def parse_and_insert(t_sql_name, sqlite_name, expected_cols):
        print(f"Processing {sqlite_name}...")
        pattern = rf"INSERT\s+INTO\s+{re.escape(t_sql_name)}[^;]+?VALUES\s*\((.*?)\);"
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
        
        count = 0
        for match in matches:
            vals_str = match.group(1).replace('\n', ' ').replace('\r', ' ')
            raw_vals = split_sql_values(vals_str)
            cleaned = [clean_val(v) for v in raw_vals]
            
            if len(cleaned) > expected_cols:
                cleaned = cleaned[:expected_cols]
            
            placeholders = ",".join(["?"] * len(cleaned))
            cursor.execute(f"INSERT INTO {sqlite_name} VALUES ({placeholders})", cleaned)
            count += 1
        print(f"Inserted {count} rows.")

    parse_and_insert("HR.Employees", "Employees", 14)
    parse_and_insert("Sales.Customers", "Customers", 11)
    parse_and_insert("Sales.Orders", "Orders", 14)
    parse_and_insert("Sales.OrderDetails", "OrderDetails", 5)

    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()
