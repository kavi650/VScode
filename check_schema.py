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
    
    # Check table structure
    print("\n📋 Checking table structures:")
    
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print(f"Found tables: {[table[0] for table in tables]}")
    
    # Check foreign key constraints for transaction table
    cursor.execute("""
        SELECT 
            tc.constraint_name, 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND tc.table_name = 'transaction';
    """)
    
    foreign_keys = cursor.fetchall()
    print(f"\nForeign key constraints on 'transaction' table:")
    for fk in foreign_keys:
        print(f"  Constraint: {fk[0]}")
        print(f"  Table: {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")
    
    # Check if there's a 'users' table vs 'user' table
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name IN ('user', 'users');
    """)
    
    user_tables = cursor.fetchall()
    print(f"\nUser-related tables: {[table[0] for table in user_tables]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")