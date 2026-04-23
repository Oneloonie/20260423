import sqlite3
import re
import os

def setup_database():
    sql_file = 'TSQL2012.sql'
    db_file = 'TSQL2012.db'

    if os.path.exists(db_file):
        os.remove(db_file)

    print(f"Reading {sql_file}...")
    with open(sql_file, 'r', encoding='utf-16') as f:
        sql_content = f.read()

    print("Cleaning up SQL syntax for SQLite...")
    
    # Remove comments
    sql_content = re.sub(r'--.*', '', sql_content)
    sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)

    # Remove T-SQL specifics
    sql_content = re.sub(r'(?i)\bUSE\s+\w+;?', '', sql_content)
    sql_content = re.sub(r'(?i)CREATE\s+SCHEMA\s+\w+\s+AUTHORIZATION\s+dbo;?', '', sql_content)
    sql_content = re.sub(r'(?i)IF\s+DB_ID.*?GO', '', sql_content, flags=re.DOTALL)
    sql_content = re.sub(r'(?i)CREATE\s+DATABASE\s+\w+;?', '', sql_content)
    sql_content = sql_content.replace('NONCLUSTERED', '')
    sql_content = re.sub(r'(?i)WITH\s+NOWAIT,\s+LOG;?', '', sql_content)

    # IDENTITY to AUTOINCREMENT
    sql_content = re.sub(r'(\w+)\s+INT\s+NOT\s+NULL\s+IDENTITY', r'\1 INTEGER PRIMARY KEY AUTOINCREMENT', sql_content)
    
    # Remove redundant PRIMARY KEY constraints
    sql_content = re.sub(r'(?i),\s*CONSTRAINT\s+PK_\w+\s+PRIMARY\s+KEY\s*\([^)]+\)', '', sql_content)

    # Schema prefix to underscore
    sql_content = re.sub(r'\b(HR|Sales|Production|Stats|dbo)\.(\w+)\b', r'\1_\2', sql_content)

    # Type replacements
    sql_content = sql_content.replace('NVARCHAR', 'TEXT')
    sql_content = sql_content.replace('MONEY', 'REAL')
    sql_content = sql_content.replace('DATETIME', 'TEXT')
    sql_content = sql_content.replace('BIT', 'INTEGER')
    sql_content = sql_content.replace('NUMERIC(4, 3)', 'REAL')
    sql_content = sql_content.replace('SMALLINT', 'INTEGER')

    # Split by GO
    statements = re.split(r'(?i)\bGO\b', sql_content)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    executed_count = 0
    error_count = 0
    for statement in statements:
        for stmt in statement.split(';'):
            stmt = stmt.strip()
            if not stmt: continue
            try:
                cursor.execute(stmt)
                executed_count += 1
            except sqlite3.Error as e:
                error_count += 1
                # Only print create table errors for debugging
                if "CREATE TABLE" in stmt.upper():
                    print(f"Error: {e} | Stmt: {stmt[:50]}...")

    conn.commit()
    conn.close()
    print(f"Database {db_file} created. Executed: {executed_count}, Errors: {error_count}")

if __name__ == "__main__":
    setup_database()
