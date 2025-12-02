import pymysql
import os
import sys

def setup_database():
    host = os.getenv('DB_HOST', 'iot-sql-flexible-server.mysql.database.azure.com')
    user = os.getenv('DB_USER', 'sqladmin')
    password = os.getenv('DB_PASSWORD', 'YourSecurePassword123!')
    database = os.getenv('DB_NAME', 'iot-sensors-db')
    
    try:
        print(f"Connecting to {host}...")
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            ssl={'ca': None},
            charset='utf8mb4'
        )
        
        print("Reading SQL script...")
        with open('database_schema.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        with conn.cursor() as cursor:
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        print(f"Executing command {i}/{len(statements)}...")
                        cursor.execute(statement)
                    except Exception as e:
                        if "already exists" in str(e).lower() or "1050" in str(e):
                            print(f"  Skipped (already exists): {statement[:50]}...")
                        else:
                            print(f"  Error: {e}")
                            raise
        
        conn.commit()
        print("\n[OK] Database successfully configured!")
        
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\nCreated tables: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()


