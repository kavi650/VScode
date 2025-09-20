# E-Bank - Modern Banking Solution

A complete e-banking web application built with Flask, PostgreSQL, HTML/CSS and JavaScript. Features separate admin and customer portals with comprehensive banking operations.

## 🌟 Features

### Landing Page
- **Welcome page** with admin and customer login portals
- **Admin login**: Username: `admin`, Password: `a123`
- **Customer login**: Mobile number and 4-digit PIN

### Admin Dashboard
- **Create Account**: Register new customers with auto-generated account numbers
- **Analytics**: Interactive charts showing weekly/monthly/yearly transaction data
- **Transaction Reports**: Generate and filter transaction reports with PDF export
- **Search Profiles**: Find customer profiles by account number
- **Users Management**: View all customers, edit/delete accounts, download statements

### Customer Dashboard  
- **Balance Display**: Account balance and wallet balance
- **Operations**: Deposit, withdraw to wallet, transfer money
- **Profile**: View personal account information
- **Transaction History**: View all transactions with PDF export
- **Chatbot**: AI assistant for account queries
- **Budgeting Tool**: Financial insights with charts and suggestions
- **QR Scanner**: Scan & Pay functionality for wallet payments

### Key Features
- **Responsive Design** with modern UI/UX
- **Real-time Analytics** with Chart.js
- **PDF Statement Generation** 
- **QR Code Payments**
- **Secure PIN-based Authentication**
- **PostgreSQL Database** with optimized queries
- **Color Scheme**: Primary Dark Blue (#0053ba) and Light Blue (#00addb)

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **PDF Generation**: ReportLab
- **Icons**: Font Awesome

## 📋 Prerequisites

Before installing, ensure you have:

1. **Python 3.7+** installed
2. **PostgreSQL** installed and running
3. **Git** (optional, for version control)

### Installing PostgreSQL

#### Windows:
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer and follow the setup wizard
3. Remember the password you set for the 'postgres' user
4. Default port is 5432

#### macOS:
```bash
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## 🚀 Installation Steps

### Step 1: Clone/Download the Project

If using Git:
```bash
git clone <repository-url>
cd ebank-project
```

Or download the zip file and extract to `ebank-project` folder.

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv ebank_env

# Activate virtual environment
# On Windows:
ebank_env\Scripts\activate
# On macOS/Linux:
source ebank_env/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL Database

#### Option A: Use the Setup Script (Recommended)

1. Edit `setup_database.py` and update these variables:
   ```python
   DB_USER = 'postgres'        # Your PostgreSQL username
   DB_PASSWORD = 'your_password'  # Your PostgreSQL password
   ```

2. Run the setup script:
   ```bash
   python setup_database.py
   ```

3. Choose 'y' when asked to create sample data for testing.

#### Option B: Manual Setup

1. Connect to PostgreSQL:
   ```bash
   psql -U postgres -h localhost
   ```

2. Create database:
   ```sql
   CREATE DATABASE ebank;
   \q
   ```

3. The Flask app will create tables automatically on first run.

### Step 5: Configure Flask Application

1. Open `app.py` in a text editor
2. Update the database configuration line:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/ebank'
   ```
   Replace `username` and `password` with your PostgreSQL credentials.

### Step 6: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 🎯 Usage Guide

### Admin Access
1. Go to `http://localhost:5000`
2. Click **Admin Login**
3. Enter:
   - Username: `admin`
   - Password: `a123`

### Customer Access
If you created sample data, use these test accounts:

**Test User 1:**
- Mobile: `1234567890`
- PIN: `1234`

**Test User 2:**
- Mobile: `9876543210` 
- PIN: `5678`

**Test User 3:**
- Mobile: `5555555555`
- PIN: `9999`

### Creating New Customers
1. Login as admin
2. Go to **Create Account**
3. Fill in customer details
4. System generates 8-digit account number and uses admin-set PIN
5. Provide credentials to customer

## 📁 Project Structure

```
ebank-project/
├── app.py                 # Main Flask application
├── setup_database.py      # Database setup script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── main.js       # JavaScript functions
│   └── images/           # Image assets
└── templates/
    ├── base.html         # Base template
    ├── landing.html      # Landing page
    ├── admin_dashboard.html
    ├── customer_dashboard.html
    ├── create_account.html
    ├── analytics.html
    ├── operations.html
    └── [other templates]
```

## 🔧 Configuration Options

### Database Configuration
Edit these variables in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/ebank'
app.secret_key = 'your-secret-key-here'  # Change this for production
```

### Admin Credentials
To change admin credentials, edit in `app.py`:
```python
if username == 'admin' and password == 'a123':  # Change these values
```

## 📊 Database Schema

### Users Table
- `id` (Primary Key)
- `name` - Customer name
- `mobile` - Phone number (unique)
- `address` - Customer address
- `date_of_birth` - Birth date
- `aadhar` - Aadhar number (unique)
- `account_number` - 8-digit account number (unique)
- `pin` - 4-digit PIN
- `account_balance` - Main account balance
- `wallet_balance` - Wallet balance for QR payments
- `created_at` - Account creation timestamp

### Transactions Table
- `id` (Primary Key)
- `account_number` - Foreign key to users
- `transaction_type` - deposit/withdraw/transfer
- `amount` - Transaction amount
- `details` - Transaction description
- `timestamp` - Transaction time
- `balance_after` - Balance after transaction

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check username/password in configuration
   - Verify database name exists

2. **Port Already in Use**
   - Change port in app.py: `app.run(debug=True, port=5001)`

3. **Missing Dependencies**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

4. **Permission Errors**
   - On Windows, run command prompt as Administrator
   - On Linux/macOS, check file permissions

### Debug Mode
The application runs in debug mode by default. For production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## 🔒 Security Considerations

For production deployment:
1. Change the secret key
2. Use environment variables for sensitive data
3. Enable HTTPS
4. Implement rate limiting
5. Add input validation and sanitization
6. Use password hashing for admin credentials

## 🎨 Customization

### Colors
The application uses CSS variables for colors. Edit `static/css/style.css`:
```css
:root {
    --primary-dark: #0053ba;    /* Dark Blue */
    --primary-light: #00addb;   /* Light Blue */
    --background: #ffffff;      /* White background */
}
```

### Logo
Replace the Font Awesome icon in templates with your logo:
```html
<div class="logo">
    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
    <span>Your Bank Name</span>
</div>
```

## 📈 Features Implemented

- ✅ Landing page with dual login
- ✅ Admin dashboard with full management
- ✅ Customer dashboard with banking operations  
- ✅ Account creation with auto-generated account numbers
- ✅ Interactive analytics with charts
- ✅ Transaction history and reporting
- ✅ PDF statement generation
- ✅ QR scanner modal for payments
- ✅ Chatbot for customer queries
- ✅ Budgeting tools with insights
- ✅ Responsive design
- ✅ Modern UI with specified color scheme
- ✅ Form validation and error handling

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all installation steps
3. Ensure all dependencies are installed
4. Check PostgreSQL connection

## 📜 License

This project is created for educational purposes. Feel free to modify and use according to your needs.

---

**E-Bank® 2025. All Rights Reserved**
