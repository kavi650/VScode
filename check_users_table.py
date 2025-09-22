import psycopg2

# Database connection parameters
conn_params = {
    'host': 'localhost',
    'port': 5433,
    'database': 'ebankupdate',
    'user': 'postgres',
    'password': '852685'
}

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    print("✅ Successfully connected to PostgreSQL!")
    
    # Check both user tables
    print("\n📋 Checking both user tables:")
    
    # Check 'user' table (singular)
    cursor.execute("SELECT COUNT(*) FROM \"user\"")
    user_count = cursor.fetchone()[0]
    print(f"'user' table count: {user_count}")
    
    cursor.execute("SELECT account_number, name, email FROM \"user\"")
    user_data = cursor.fetchall()
    print("'user' table data:")
    for row in user_data:
        print(f"  Account: {row[0]}, Name: {row[1]}, Email: {row[2]}")
    
    # Check 'users' table (plural)
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    print(f"\n'users' table count: {users_count}")
    
    if users_count > 0:
        cursor.execute("SELECT account_number, name, email FROM users")
        users_data = cursor.fetchall()
        print("'users' table data:")
        for row in users_data:
            print(f"  Account: {row[0]}, Name: {row[1]}, Email: {row[2]}")
    else:
        print("'users' table is empty!")
    
    # Check which table the foreign key references
    cursor.execute("""
        SELECT ccu.table_name AS foreign_table_name
        FROM information_schema.table_constraints AS tc 
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND tc.table_name = 'transaction';
    """)
    
    foreign_table = cursor.fetchone()
    if foreign_table:
        print(f"\nForeign key on 'transaction' table references: {foreign_table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")