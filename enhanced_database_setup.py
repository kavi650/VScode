import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os
import json
from datetime import datetime

# Database configuration
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'ebankupdate'
DB_USER = 'postgres'  # Change this to your PostgreSQL username
DB_PASSWORD = '852685'  # Change this to your PostgreSQL password

def create_database():
    """Create the ebank database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if cursor.fetchone():
            print(f"✅ Database '{DB_NAME}' already exists.")
        else:
            # Create database
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"✅ Database '{DB_NAME}' created successfully.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

    return True

def create_enhanced_tables():
    """Create all the necessary tables for the Enhanced E-Bank application."""
    try:
        # Connect to the ebank database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        print("🔧 Creating enhanced database tables...")

        # Enhanced Users table with new fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "user" (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                mobile VARCHAR(15) UNIQUE NOT NULL,
                address TEXT NOT NULL,
                date_of_birth DATE NOT NULL,
                aadhar VARCHAR(12) UNIQUE NOT NULL,
                account_number VARCHAR(8) UNIQUE NOT NULL,
                pin VARCHAR(4) NOT NULL,
                account_balance FLOAT DEFAULT 0.0,
                wallet_balance FLOAT DEFAULT 0.0,
                profile_picture VARCHAR(200) DEFAULT 'default.jpg',
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                email_verification_token VARCHAR(100) UNIQUE,
                preferred_currency VARCHAR(3) DEFAULT 'INR',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Enhanced Users table created")

        # Enhanced Transactions table with new fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction (
                id SERIAL PRIMARY KEY,
                account_number VARCHAR(8) REFERENCES "user"(account_number),
                transaction_type VARCHAR(20) NOT NULL,
                amount FLOAT NOT NULL,
                currency VARCHAR(3) DEFAULT 'INR',
                exchange_rate FLOAT DEFAULT 1.0,
                converted_amount FLOAT,
                details TEXT,
                recipient_account VARCHAR(8),
                split_group_id VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                balance_after FLOAT NOT NULL
            );
        """)
        print("✅ Enhanced Transactions table created")

        # Split Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS split_payment (
                id SERIAL PRIMARY KEY,
                group_id VARCHAR(50) UNIQUE NOT NULL,
                organizer_account VARCHAR(8) NOT NULL,
                total_amount FLOAT NOT NULL,
                currency VARCHAR(3) DEFAULT 'INR',
                description TEXT NOT NULL,
                participants JSON NOT NULL,
                individual_amount FLOAT NOT NULL,
                paid_by JSON DEFAULT '[]',
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Split Payments table created")

        # User Activity table for admin monitoring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id SERIAL PRIMARY KEY,
                account_number VARCHAR(8) REFERENCES "user"(account_number),
                activity_type VARCHAR(50) NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                details JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ User Activity table created")

        # Currency Rates table for exchange rate caching
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS currency_rate (
                id SERIAL PRIMARY KEY,
                from_currency VARCHAR(3) NOT NULL,
                to_currency VARCHAR(3) NOT NULL,
                rate FLOAT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_currency, to_currency)
            );
        """)
        print("✅ Currency Rates table created")

        # Enhanced Chatbot Knowledge Base
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_knowledge (
                id SERIAL PRIMARY KEY,
                question_keywords JSON NOT NULL,
                answer TEXT NOT NULL,
                category VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Chatbot Knowledge table created")

        # System Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id SERIAL PRIMARY KEY,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ System Settings table created")

        # Admin Actions Log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_actions (
                id SERIAL PRIMARY KEY,
                admin_username VARCHAR(50) NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                target_account VARCHAR(8),
                description TEXT,
                ip_address VARCHAR(45),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Admin Actions table created")

        # Create enhanced indexes for better performance
        print("🔧 Creating database indexes...")

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_email ON \"user\"(email);",
            "CREATE INDEX IF NOT EXISTS idx_user_mobile ON \"user\"(mobile);",
            "CREATE INDEX IF NOT EXISTS idx_user_account_number ON \"user\"(account_number);",
            "CREATE INDEX IF NOT EXISTS idx_user_is_active ON \"user\"(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_user_email_verified ON \"user\"(email_verified);",

            "CREATE INDEX IF NOT EXISTS idx_transaction_account_number ON transaction(account_number);",
            "CREATE INDEX IF NOT EXISTS idx_transaction_timestamp ON transaction(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_transaction_type ON transaction(transaction_type);",
            "CREATE INDEX IF NOT EXISTS idx_transaction_currency ON transaction(currency);",

            "CREATE INDEX IF NOT EXISTS idx_split_payment_group_id ON split_payment(group_id);",
            "CREATE INDEX IF NOT EXISTS idx_split_payment_organizer ON split_payment(organizer_account);",
            "CREATE INDEX IF NOT EXISTS idx_split_payment_status ON split_payment(status);",

            "CREATE INDEX IF NOT EXISTS idx_user_activity_account ON user_activity(account_number);",
            "CREATE INDEX IF NOT EXISTS idx_user_activity_type ON user_activity(activity_type);",
            "CREATE INDEX IF NOT EXISTS idx_user_activity_timestamp ON user_activity(timestamp);",

            # The part you asked to complete:
            "CREATE INDEX IF NOT EXISTS idx_currency_rate_pair ON currency_rate(from_currency, to_currency);",
            "CREATE INDEX IF NOT EXISTS idx_currency_rate_updated ON currency_rate(updated_at);",

            "CREATE INDEX IF NOT EXISTS idx_chatbot_knowledge_category ON chatbot_knowledge(category);",
            "CREATE INDEX IF NOT EXISTS idx_chatbot_knowledge_active ON chatbot_knowledge(is_active);",

            "CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings(setting_key);",

            "CREATE INDEX IF NOT EXISTS idx_admin_actions_timestamp ON admin_actions(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_admin_actions_admin ON admin_actions(admin_username);"
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        print("✅ Database indexes created")

        conn.commit()
        print("✅ All enhanced tables created successfully")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"❌ Error creating tables: {e}")
        return False

    return True

def create_enhanced_sample_data():
    """Create comprehensive sample data for testing all features."""
    try:
        # Connect to the ebank database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Check if sample data already exists
        cursor.execute("SELECT COUNT(*) FROM \"user\"")
        user_count = cursor.fetchone()[0]

        if user_count > 0:
            print("✅ Sample data already exists.")
            cursor.close()
            conn.close()
            return True

        print("🔧 Creating enhanced sample data...")

        # Create sample users with enhanced fields
        sample_users = [
            ('John Doe', 'banktest650@gmail.co', '1234567890', '123 Main St, City, State', '1990-01-15', '123456789012', '12345678', '1234', 5000.00, 500.00, 'default.jpg', True, True, None, 'INR'),
            ('Jane Smith', 'jane.smith@email.com', '9876543210', '456 Oak Ave, City, State', '1985-05-20', '987654321098', '87654321', '5678', 3000.00, 200.00, 'default.jpg', True, True, None, 'USD'),
            ('Mike Johnson', 'mike.johnson@email.com', '5555555555', '789 Pine Rd, City, State', '1992-11-30', '555666777888', '11111111', '9999', 7500.00, 1000.00, 'default.jpg', True, False, 'sample_token_123', 'EUR'),
            ('Sarah Wilson', 'sarah.wilson@email.com', '1111111111', '321 Elm St, City, State', '1988-08-10', '111222333444', '22222222', '0000', 4200.00, 300.00, 'default.jpg', False, True, None, 'GBP'),
            ('David Brown', 'david.brown@email.com', '2222222222', '654 Maple Ave, City, State', '1995-03-25', '222333444555', '33333333', '1111', 6800.00, 750.00, 'default.jpg', True, True, None, 'INR')
        ]

        for user in sample_users:
            cursor.execute("""
                INSERT INTO "user" (name, email, mobile, address, date_of_birth, aadhar, account_number, pin,
                                     account_balance, wallet_balance, profile_picture, is_active, email_verified,
                                     email_verification_token, preferred_currency)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, user)

        print("✅ Sample users created")

        # Create enhanced sample transactions
        sample_transactions = [
            ('12345678', 'deposit', 1000.00, 'INR', 1.0, None, 'Initial deposit', None, None, 5000.00),
            ('87654321', 'deposit', 500.00, 'USD', 83.25, 41625.00, 'USD deposit converted to INR', None, None, 3000.00),
            ('11111111', 'withdraw', 250.00, 'INR', 1.0, None, 'ATM withdrawal', None, None, 7250.00),
            ('12345678', 'transfer', -200.00, 'INR', 1.0, None, 'Transfer to friend', '87654321', None, 4800.00),
            ('87654321', 'transfer', 200.00, 'INR', 1.0, None, 'Transfer from friend', '12345678', None, 3200.00),
            ('22222222', 'currency_exchange', -100.00, 'GBP', 103.50, 10350.00, 'GBP to INR exchange', None, None, 4100.00),
            ('33333333', 'split_payment', -150.00, 'INR', 1.0, None, 'Restaurant bill split', None, 'SPLIT_33333333_1234567890', 6650.00)
        ]

        for transaction in sample_transactions:
            cursor.execute("""
                INSERT INTO transaction (account_number, transaction_type, amount, currency, exchange_rate,
                                         converted_amount, details, recipient_account, split_group_id, balance_after)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, transaction)

        print("✅ Sample transactions created")

        # Create sample split payments
        sample_splits = [
            ('SPLIT_33333333_1234567890', '33333333', 600.00, 'INR', 'Restaurant dinner with friends',
             json.dumps(['33333333', '12345678', '87654321', '11111111']), 150.00, json.dumps(['33333333']), 'pending'),
            ('SPLIT_12345678_9876543210', '12345678', 1000.00, 'INR', 'Movie tickets and snacks',
             json.dumps(['12345678', '87654321']), 500.00, json.dumps(['12345678', '87654321']), 'completed'),
            ('SPLIT_87654321_1111111111', '87654321', 2400.00, 'USD', 'Weekend trip expenses',
             json.dumps(['87654321', '11111111', '22222222']), 800.00, json.dumps(['87654321']), 'pending')
        ]

        for split in sample_splits:
            cursor.execute("""
                INSERT INTO split_payment (group_id, organizer_account, total_amount, currency, description,
                                         participants, individual_amount, paid_by, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, split)

        print("✅ Sample split payments created")

        # Create sample user activities
        sample_activities = [
            ('12345678', 'login', '192.168.1.100', 'Mozilla/5.0 Chrome/91.0', json.dumps({'success': True})),
            ('87654321', 'login', '192.168.1.101', 'Mozilla/5.0 Safari/14.0', json.dumps({'success': True})),
            ('11111111', 'login_failed', '203.45.67.89', 'Mozilla/5.0 Firefox/89.0', json.dumps({'reason': 'wrong_pin'})),
            ('12345678', 'transaction', '192.168.1.100', 'Mozilla/5.0 Chrome/91.0', json.dumps({'type': 'transfer', 'amount': 200})),
            ('22222222', 'profile_update', '10.0.0.50', 'Mozilla/5.0 Mobile Safari', json.dumps({'type': 'profile_picture'})),
            ('33333333', 'split_payment', '192.168.1.105', 'Mozilla/5.0 Chrome/91.0', json.dumps({'group_id': 'SPLIT_33333333_1234567890'}))
        ]

        for activity in sample_activities:
            cursor.execute("""
                INSERT INTO user_activity (account_number, activity_type, ip_address, user_agent, details)
                VALUES (%s, %s, %s, %s, %s)
            """, activity)

        print("✅ Sample user activities created")

        # Create sample currency rates
        sample_rates = [
            ('USD', 'INR', 83.25),
            ('EUR', 'INR', 90.50),
            ('GBP', 'INR', 103.75),
            ('JPY', 'INR', 0.56),
            ('AUD', 'INR', 54.80),
            ('CAD', 'INR', 61.20),
            ('CHF', 'INR', 91.45),
            ('CNY', 'INR', 11.48),
            ('INR', 'USD', 0.012),
            ('INR', 'EUR', 0.011),
            ('INR', 'GBP', 0.0096),
            ('USD', 'EUR', 0.85),
            ('EUR', 'USD', 1.18),
            ('GBP', 'USD', 1.25),
            ('USD', 'GBP', 0.80)
        ]

        for rate in sample_rates:
            cursor.execute("""
                INSERT INTO currency_rate (from_currency, to_currency, rate)
                VALUES (%s, %s, %s)
            """, rate)

        print("✅ Sample currency rates created")

        # Create enhanced chatbot knowledge base
        chatbot_knowledge = [
            (json.dumps(['balance', 'money', 'account', 'funds']),
             'Your current account balance is {account_balance} and wallet balance is {wallet_balance}. Your account number is {account_number}.',
             'account_info'),
            (json.dumps(['transfer', 'send', 'payment']),
             'You can transfer money domestically through Operations or internationally through International Transactions with live exchange rates.',
             'transactions'),
            (json.dumps(['split', 'group', 'share', 'divide']),
             'Split Payments help you divide expenses among friends. Create a split, invite participants, and they can pay via QR codes.',
             'split_payments'),
            (json.dumps(['international', 'currency', 'exchange', 'foreign']),
             'E-Bank supports 12+ currencies with live exchange rates. Convert money or send international transfers with competitive rates.',
             'international'),
            (json.dumps(['profile', 'picture', 'photo', 'image']),
             'You can upload a profile picture in your Profile section. Supported formats: PNG, JPG, JPEG, GIF.',
             'profile'),
            (json.dumps(['qr', 'scan', 'code', 'quick']),
             'Generate QR codes for payments or scan others\' codes for quick transfers. Great for split payments and merchant payments.',
             'qr_payments'),
            (json.dumps(['budget', 'spending', 'analysis', 'chart']),
             'Check your Budgeting Tool for spending analysis with interactive charts and personalized financial insights.',
             'budgeting'),
            (json.dumps(['help', 'support', 'contact', 'assistance']),
             'I can help with account info, transfers, split payments, international transactions, QR payments, and budgeting. What do you need help with?',
             'support'),
            (json.dumps(['email', 'verify', 'verification', 'confirm']),
             'Email verification is required for account security. If you haven\'t received the verification email, you can request a new one from the login page.',
             'security'),
            (json.dumps(['voice', 'speak', 'audio', 'talk']),
             'I support voice interactions! You can speak your questions using the microphone button, and I can read my responses aloud when voice mode is enabled.',
             'features'),
            (json.dumps(['pin', 'password', 'security', 'change']),
             'You can change your PIN in the Profile section under Security Settings. Your PIN is used to authorize transactions and must be 4 digits.',
             'security'),
            (json.dumps(['transaction', 'history', 'statement', 'record']),
             'View your transaction history in the History section. You can also download PDF statements for weekly, monthly, or yearly periods.',
             'transactions'),
            (json.dumps(['limit', 'maximum', 'daily', 'restriction']),
             'Your daily transaction limit is ₹1,00,000 for transfers and ₹50,000 for wallet transactions. Contact support to modify limits.',
             'account_info'),
            (json.dumps(['fee', 'charge', 'cost', 'price']),
             'Most domestic transactions are free. International transfers have competitive fees based on the amount and destination country.',
             'fees'),
            (json.dumps(['mobile', 'app', 'phone', 'device']),
             'Access E-Bank on mobile devices through our responsive web interface. All features work seamlessly on phones and tablets.',
             'features')
        ]

        for knowledge in chatbot_knowledge:
            cursor.execute("""
                INSERT INTO chatbot_knowledge (question_keywords, answer, category)
                VALUES (%s, %s, %s)
            """, knowledge)

        print("✅ Enhanced chatbot knowledge base created")

        # Create system settings
        system_settings = [
            ('maintenance_mode', 'false', 'Enable/disable maintenance mode'),
            ('max_transaction_limit', '100000', 'Maximum transaction limit per day'),
            ('max_wallet_limit', '50000', 'Maximum wallet transaction limit'),
            ('currency_update_interval', '300', 'Currency rate update interval in seconds'),
            ('email_notifications', 'true', 'Enable email notifications'),
            ('sms_notifications', 'true', 'Enable SMS notifications'),
            ('min_pin_attempts', '3', 'Minimum failed PIN attempts before lockout'),
            ('session_timeout', '1800', 'Session timeout in seconds'),
            ('file_upload_max_size', '16777216', 'Maximum file upload size in bytes (16MB)'),
            ('supported_currencies', json.dumps(['INR', 'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'AED', 'SGD', 'HKD']), 'List of supported currencies')
        ]

        for setting in system_settings:
            cursor.execute("""
                INSERT INTO system_settings (setting_key, setting_value, description)
                VALUES (%s, %s, %s)
            """, setting)

        print("✅ System settings created")

        # Create sample admin actions
        admin_actions = [
            ('admin', 'user_created', '33333333', 'Created new user account', '192.168.1.1'),
            ('admin', 'user_suspended', '22222222', 'Suspended user account for security review', '192.168.1.1'),
            ('admin', 'balance_adjustment', '12345678', 'Adjusted account balance by +1000.00', '192.168.1.1'),
            ('admin', 'system_settings_updated', None, 'Updated currency update interval', '192.168.1.1')
        ]

        for action in admin_actions:
            cursor.execute("""
                INSERT INTO admin_actions (admin_username, action_type, target_account, description, ip_address)
                VALUES (%s, %s, %s, %s, %s)
            """, action)

        print("✅ Sample admin actions logged")

        conn.commit()

        # Display sample credentials
        print("\n" + "="*60)
        print("🎉 ENHANCED E-BANK SAMPLE DATA CREATED SUCCESSFULLY!")
        print("="*60)
        print("📋 SAMPLE USER CREDENTIALS FOR TESTING:")
        print("-"*60)
        print("👤 User 1 (Active, Email Verified):")
        print("   Email: john.doe@email.com")
        print("   Mobile: 1234567890")
        print("   PIN: 1234")
        print("   Account: 12345678")
        print("   Currency: INR")
        print("")
        print("👤 User 2 (Active, Email Verified):")
        print("   Email: jane.smith@email.com")
        print("   Mobile: 9876543210")
        print("   PIN: 5678")
        print("   Account: 87654321")
        print("   Currency: USD")
        print("")
        print("👤 User 3 (Active, Email NOT Verified):")
        print("   Email: mike.johnson@email.com")
        print("   Mobile: 5555555555")
        print("   PIN: 9999")
        print("   Account: 11111111")
        print("   Currency: EUR")
        print("")
        print("👤 User 4 (SUSPENDED Account):")
        print("   Email: sarah.wilson@email.com")
        print("   Mobile: 1111111111")
        print("   PIN: 0000")
        print("   Account: 22222222")
        print("   Currency: GBP")
        print("")
        print("👤 User 5 (Active, Email Verified):")
        print("   Email: david.brown@email.com")
        print("   Mobile: 2222222222")
        print("   PIN: 1111")
        print("   Account: 33333333")
        print("   Currency: INR")
        print("-"*60)
        print("🔧 ADMIN CREDENTIALS:")
        print("   Username: admin")
        print("   Password: a123")
        print("-"*60)
        print("🌟 ENHANCED FEATURES TO TEST:")
        print("   ✅ Email verification during login")
        print("   ✅ Split payments with QR codes")
        print("   ✅ International transactions")
        print("   ✅ Enhanced chatbot with voice")
        print("   ✅ Profile picture upload")
        print("   ✅ Advanced analytics charts")
        print("   ✅ User activity monitoring")
        print("   ✅ Multi-currency support")
        print("   ✅ Account suspension system")
        print("   ✅ Currency rate caching")
        print("="*60)

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"❌ Error creating sample data: {e}")
        return False

    return True

def update_config_file():
    """Generate configuration information for the Flask app."""
    config_info = f"""
🔧 DATABASE CONFIGURATION FOR app.py:
{'-'*50}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

📧 EMAIL CONFIGURATION (Update with your settings):
{'-'*50}
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'

💱 EXCHANGE RATE API (Get free API key):
{'-'*50}
EXCHANGE_RATE_API_KEY = 'your-api-key-here'
# Get free API key from: https://exchangerate-api.com/

📁 FILE UPLOAD CONFIGURATION:
{'-'*50}
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

🔐 SECURITY SETTINGS:
{'-'*50}
app.secret_key = 'your-secret-key-here'  # Change this!
"""

    print(config_info)

def verify_installation():
    """Verify that all tables and data were created successfully."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        print("🔍 VERIFYING INSTALLATION...")
        print("-"*40)

        # Check tables
        tables = ['user', 'transaction', 'split_payment', 'user_activity',
                  'currency_rate', 'chatbot_knowledge', 'system_settings', 'admin_actions']

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ {table.replace('_', ' ').title()}: {count} records")

        print("-"*40)
        print("✅ All tables verified successfully!")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"❌ Verification failed: {e}")

def main():
    """Main setup function for enhanced E-Bank."""
    print("🏦 ENHANCED E-BANK DATABASE SETUP")
    print("=" * 50)
    print("🚀 Setting up advanced banking features...")
    print("")

    # Check if psycopg2 is installed
    try:
        import psycopg2
        print("✅ psycopg2 module found")
    except ImportError:
        print("❌ psycopg2 is not installed.")
        print("📦 Install it using: pip install psycopg2-binary")
        sys.exit(1)

    print(f"🔧 Setting up database '{DB_NAME}' on {DB_HOST}:{DB_PORT}")
    print(f"👤 Using PostgreSQL user: {DB_USER}")
    print("")

    # Create database
    if not create_database():
        print("❌ Failed to create database. Exiting.")
        sys.exit(1)

    # Create enhanced tables
    if not create_enhanced_tables():
        print("❌ Failed to create tables. Exiting.")
        sys.exit(1)

    # Create sample data
    create_sample = input("\n❓ Do you want to create comprehensive sample data for testing? (y/n): ")
    if create_sample.lower() in ['y', 'yes']:
        if not create_enhanced_sample_data():
            print("⚠️  Failed to create sample data.")

    # Verify installation
    verify_installation()

    # Show configuration
    update_config_file()

    print("\n🎉 ENHANCED E-BANK DATABASE SETUP COMPLETED!")
    print("=" * 60)
    print("📝 NEXT STEPS:")
    print("1. ✅ Database setup completed")
    print("2. 📧 Configure email settings in app.py")
    print("3. 💱 Get exchange rate API key (optional)")
    print("4. 📦 Install Python dependencies:")
    print("   pip install flask flask-sqlalchemy flask-mail psycopg2-binary")
    print("   pip install pillow requests pandas reportlab matplotlib")
    print("5. 🚀 Run the application: python app.py")
    print("6. 🌐 Access at: http://localhost:5000")
    print("")
    print("🎯 READY TO TEST ALL ENHANCED FEATURES!")
    print("=" * 60)

if __name__ == "__main__":
    main()