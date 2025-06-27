import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="screener_db",
    user="postgres",       # replace with your PostgreSQL username
    password="password",   # replace with your password
    host="localhost",
    port="5432"                 # default PostgreSQL port
)

# Create a cursor object
cur = conn.cursor()

# Step 1: Fetch all table names in the public schema
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public';
""")

tables = cur.fetchall()

# Step 2: Print all table names and contents
print("All tables in screener_db:\n")

for table in tables:
    table_name = table[0]
    print(f"\n--- Table: {table_name} ---")
    
    try:
        cur.execute(f"SELECT * FROM {table_name};")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        
        # Print column headers
        print(" | ".join(column_names))
        print("-" * 40)
        
        # Print each row
        for row in rows:
            print(" | ".join(str(cell) for cell in row))

    except Exception as e:
        print(f"Error reading table {table_name}: {e}")

# Close connections
cur.close()
conn.close()
