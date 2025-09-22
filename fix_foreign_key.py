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
    
    # Drop existing foreign key constraint
    print("\n🔧 Dropping existing foreign key constraint...")
    cursor.execute("ALTER TABLE transaction DROP CONSTRAINT IF EXISTS transaction_account_number_fkey;")
    
    # Create new foreign key constraint referencing the correct 'user' table
    print("Creating new foreign key constraint referencing 'user' table...")
    cursor.execute("""
        ALTER TABLE transaction 
        ADD CONSTRAINT transaction_account_number_fkey 
        FOREIGN KEY (account_number) 
        REFERENCES "user"(account_number);
    """)
    
    print("✅ Foreign key constraint updated successfully!")
    
    # Verify the change
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
        print(f"✅ Foreign key now references: {foreign_table[0]}")
    
    # Commit the changes
    conn.commit()
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
    
print("\n🎉 Fix complete! The foreign key now references the correct 'user' table.")
print("You should now be able to make deposits/transfers without ForeignKeyViolation errors.")