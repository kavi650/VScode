import psycopg2
import sys

def check_database():
    """Check database connection and existing data"""
    try:
        # Try to connect to PostgreSQL
        print("Attempting to connect to PostgreSQL...")
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='ebankupdate',
            user='postgres',
            password='852685'
        )
        print("✅ Successfully connected to PostgreSQL!")
        
        cursor = conn.cursor()
        
        # Check if 'user' table exists (need to escape since user is a reserved word)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user'
            );
        """)
        user_table_exists = cursor.fetchone()[0]
        
        if user_table_exists:
            print("✅ 'user' table exists")
            
            # Get all users
            cursor.execute('SELECT account_number, name, email FROM "user" ORDER BY account_number')
            users = cursor.fetchall()
            
            if users:
                print(f"\n📋 Found {len(users)} users:")
                for user in users:
                    print(f"  Account: {user[0]}, Name: {user[1]}, Email: {user[2]}")
            else:
                print("\n⚠️  No users found in the database!")
                
            # Check for account number 62634574 specifically
            cursor.execute('SELECT account_number, name FROM "user" WHERE account_number = %s', ('62634574',))
            specific_user = cursor.fetchone()
            
            if specific_user:
                print(f"\n✅ User with account 62634574 found: {specific_user[1]}")
            else:
                print(f"\n❌ User with account 62634574 NOT found!")
                
        else:
            print("❌ 'user' table does not exist!")
        
        # Check transactions table
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'transaction'
            );
        """)
        transaction_table_exists = cursor.fetchone()[0]
        
        if transaction_table_exists:
            print("\n✅ 'transaction' table exists")
            
            # Get recent transactions
            cursor.execute('SELECT account_number, transaction_type, amount, timestamp FROM transaction ORDER BY timestamp DESC LIMIT 5')
            transactions = cursor.fetchall()
            
            if transactions:
                print("\n📊 Recent transactions:")
                for txn in transactions:
                    print(f"  Account: {txn[0]}, Type: {txn[1]}, Amount: {txn[2]}, Time: {txn[3]}")
            else:
                print("\n⚠️  No transactions found!")
        else:
            print("\n❌ 'transaction' table does not exist!")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Possible solutions:")
        print("1. Make sure PostgreSQL is running on port 5433")
        print("2. Check if the database 'ebankupdate' exists")
        print("3. Verify username and password are correct")
        print("4. Try running: python enhanced_database_setup.py")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_database()