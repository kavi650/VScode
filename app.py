from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import random
import string
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import json
import base64
import os
import io
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests
from PIL import Image
import secrets

app = Flask(__name__)
app.secret_key = 'your-enhanced-secret-key-change-in-production'

# Email configuration
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 8025
app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None
app.config['MAIL_DEFAULT_SENDER'] = ('E-Bank', 'no-reply@ebank.local')


# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:852685@localhost:5433/ebankupdate'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)
mail = Mail(app)

# Exchange rate API configuration
EXCHANGE_RATE_API_KEY = 'your-api-key-here'  # Get from exchangerate-api.com
EXCHANGE_RATE_API_URL = 'https://v6.exchangerate-api.com/v6/'

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    aadhar = db.Column(db.String(12), unique=True, nullable=False)
    account_number = db.Column(db.String(8), unique=True, nullable=False)
    pin = db.Column(db.String(4), nullable=False)
    account_balance = db.Column(db.Float, default=0.0)
    wallet_balance = db.Column(db.Float, default=0.0)
    profile_picture = db.Column(db.String(200), default='default.jpg')
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), unique=True)
    preferred_currency = db.Column(db.String(3), default='INR')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(8), db.ForeignKey('user.account_number'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='INR')
    exchange_rate = db.Column(db.Float, default=1.0)
    converted_amount = db.Column(db.Float)
    details = db.Column(db.Text)
    recipient_account = db.Column(db.String(8))
    split_group_id = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    balance_after = db.Column(db.Float, nullable=False)

class SplitPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(50), unique=True, nullable=False)
    organizer_account = db.Column(db.String(8), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='INR')
    description = db.Column(db.Text, nullable=False)
    participants = db.Column(db.JSON)
    individual_amount = db.Column(db.Float, nullable=False)
    paid_by = db.Column(db.JSON, default=list)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(8), db.ForeignKey('user.account_number'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    details = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CurrencyRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(3), nullable=False)
    to_currency = db.Column(db.String(3), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatbotKnowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_keywords = db.Column(db.JSON, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdminActions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_username = db.Column(db.String(50), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    target_account = db.Column(db.String(8))
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    sms_alerts = db.Column(db.Boolean, default=True)
    marketing_emails = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Helper functions
def jsonb_contains(column, value):
    from sqlalchemy.dialects.postgresql import JSONB
    return column.cast(JSONB).op('@>')(f'["{value}"]')

def generate_account_number():
    return ''.join(random.choices(string.digits, k=8))

def generate_verification_token():
    return secrets.token_urlsafe(32)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_verification_email(user):
    token = generate_verification_token()
    user.email_verification_token = token
    db.session.commit()
    
    msg = Message('Verify your E-Bank account',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.html = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #0053ba, #00addb); padding: 2rem; text-align: center; color: white;">
            <h1>🏦 E-Bank</h1>
            <h2>Email Verification</h2>
        </div>
        <div style="padding: 2rem; background: #f8f9fa;">
            <p>Hello {user.name},</p>
            <p>Thank you for joining E-Bank! Please verify your email address by clicking the button below:</p>
            <div style="text-align: center; margin: 2rem 0;">
                <a href="{url_for('verify_email', token=token, _external=True)}" 
                   style="background: #0053ba; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 5px; display: inline-block;">
                   Verify Email Address
                </a>
            </div>
            <p>Your account details:</p>
            <ul>
                <li>Account Number: {user.account_number}</li>
                <li>Mobile: {user.mobile}</li>
            </ul>
            <p>If you didn't create this account, please ignore this email.</p>
        </div>
    </div>
    '''
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def get_exchange_rate(from_currency, to_currency):
    if from_currency == to_currency:
        return 1.0
    
    # Check database cache (updated within last hour)
    cached_rate = CurrencyRate.query.filter_by(
        from_currency=from_currency,
        to_currency=to_currency
    ).filter(
        CurrencyRate.updated_at > datetime.utcnow() - timedelta(hours=1)
    ).first()
    
    if cached_rate:
        return cached_rate.rate
    
    # Mock exchange rates for demo (replace with real API)
    mock_rates = {
        'USD_INR': 83.25, 'EUR_INR': 90.50, 'GBP_INR': 103.75, 'JPY_INR': 0.56,
        'INR_USD': 0.012, 'INR_EUR': 0.011, 'INR_GBP': 0.0096, 'INR_JPY': 1.79,
        'USD_EUR': 0.85, 'EUR_USD': 1.18, 'GBP_USD': 1.25, 'USD_GBP': 0.80
    }
    
    rate_key = f"{from_currency}_{to_currency}"
    rate = mock_rates.get(rate_key, 1.0)
    
    # Update database cache
    existing_rate = CurrencyRate.query.filter_by(
        from_currency=from_currency, to_currency=to_currency
    ).first()
    
    if existing_rate:
        existing_rate.rate = rate
        existing_rate.updated_at = datetime.utcnow()
    else:
        new_rate = CurrencyRate(
            from_currency=from_currency, to_currency=to_currency, rate=rate
        )
        db.session.add(new_rate)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    return rate

def log_user_activity(account_number, activity_type, details=None):
    activity = UserActivity(
        account_number=account_number,
        activity_type=activity_type,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        details=details or {}
    )
    db.session.add(activity)
    try:
        db.session.commit()
    except:
        db.session.rollback()

def log_admin_action(admin_username, action_type, target_account=None, description=None):
    action = AdminActions(
        admin_username=admin_username,
        action_type=action_type,
        target_account=target_account,
        description=description,
        ip_address=request.remote_addr
    )
    db.session.add(action)
    try:
        db.session.commit()
    except:
        db.session.rollback()

def is_admin_logged_in():
    return session.get('admin_logged_in', False)

def is_user_logged_in():
    return 'user_account' in session

def get_current_user():
    if 'user_account' in session:
        return User.query.filter_by(account_number=session['user_account']).first()
    return None

# Add these improved routes to your app.py file

import re
import json
from datetime import datetime, timedelta

class EnhancedChatbot:
    def __init__(self):
        self.banking_responses = {
            'balance': [
                "Let me check your account balance for you.",
                "I'll fetch your current balance information.",
                "Here's your balance information:"
            ],
            'transactions': [
                "Let me get your recent transaction history.",
                "I'll show you your latest transactions.",
                "Here are your recent transactions:"
            ],
            'transfer': [
                "I can help you with money transfers.",
                "You can send money through our Operations section.",
                "For transfers, you'll need the recipient's account number."
            ],
            'international': [
                "We support international transfers with live exchange rates.",
                "You can send money internationally in 12+ currencies.",
                "International transfers take 1-3 business days."
            ],
            'split': [
                "Split payments help you divide expenses with friends.",
                "You can create group expenses and collect payments via QR codes.",
                "Each participant gets a unique payment link."
            ]
        }

    def get_intent(self, query):
        query_lower = query.lower()
        
        # Banking operations
        if any(word in query_lower for word in ['balance', 'money', 'account', 'amount', 'funds']):
            return 'balance'
        elif any(word in query_lower for word in ['transaction', 'history', 'statement', 'recent', 'last']):
            return 'transactions'  
        elif any(word in query_lower for word in ['transfer', 'send', 'payment', 'pay']):
            return 'transfer'
        elif any(word in query_lower for word in ['international', 'foreign', 'currency', 'exchange']):
            return 'international'
        elif any(word in query_lower for word in ['split', 'group', 'share', 'divide']):
            return 'split'
        elif any(word in query_lower for word in ['help', 'support', 'assist']):
            return 'help'
        elif any(word in query_lower for word in ['hello', 'hi', 'hey', 'good']):
            return 'greeting'
        else:
            return 'general'

def enhanced_chatbot_response(query, user):
    """Enhanced chatbot with better banking intelligence"""
    
    chatbot = EnhancedChatbot()
    intent = chatbot.get_intent(query)
    query_lower = query.lower()
    
    # Greeting responses
    if intent == 'greeting':
        return f"Hello {user.name}! I'm your E-Bank Smart Assistant. How can I help you with your banking needs today?"
    
    # Balance queries
    elif intent == 'balance':
        return f"""💰 **Account Balance Information**
        
**Account Details:**
• Account Number: {user.account_number}
• Account Holder: {user.name}

**Current Balances:**
• 🏦 Bank Account: ₹{user.account_balance:,.2f}
• 👛 Wallet Balance: ₹{user.wallet_balance:,.2f}
• 💎 Total Balance: ₹{(user.account_balance + user.wallet_balance):,.2f}

**Quick Actions:**
• Use Operations to deposit/withdraw money
• Transfer to wallet for quick payments
• Set up international transfers
• Create QR codes for payments

Is there anything specific you'd like to know about your account?"""

    # Transaction history
    elif intent == 'transactions':
        # Get recent transactions from database
        recent_transactions = Transaction.query.filter_by(
            account_number=user.account_number
        ).order_by(Transaction.timestamp.desc()).limit(5).all()
        
        if not recent_transactions:
            return f"""📋 **Transaction History**

No recent transactions found for account {user.account_number}.

**Getting Started:**
• Make your first deposit through Operations
• Try our Split Payment feature
• Send money internationally
• Use QR codes for quick payments

Would you like me to explain any of these features?"""
        
        response = f"📊 **Recent Transaction History**\n\n"
        for i, txn in enumerate(recent_transactions, 1):
            emoji = "💰" if txn.amount > 0 else "💸"
            response += f"{emoji} **Transaction {i}:**\n"
            response += f"• Type: {txn.transaction_type.replace('_', ' ').title()}\n"
            response += f"• Amount: ₹{abs(txn.amount):,.2f}\n"
            response += f"• Date: {txn.timestamp.strftime('%B %d, %Y at %I:%M %p')}\n"
            if txn.details:
                response += f"• Details: {txn.details}\n"
            response += f"• Balance After: ₹{txn.balance_after:,.2f}\n\n"
        
        response += "💡 **Need More Details?**\n"
        response += "• View complete history in the History section\n"
        response += "• Download statements as PDF\n"
        response += "• Filter by date range or transaction type"
        
        return response

    # Transfer assistance
    elif intent == 'transfer':
        return f"""💸 **Money Transfer Guide**

**Domestic Transfers:**
• Go to Operations → Transfer
• Enter recipient's 8-digit account number
• Specify amount and confirm with PIN
• Transfers are instant and free

**International Transfers:**
• Visit International Transactions section
• Support for 12+ major currencies
• Live exchange rates updated hourly
• Transfer fees: 1-2% of amount

**Quick Payments:**
• Use QR codes for instant payments
• Generate your payment QR
• Scan others' QR codes to pay
• Perfect for split bills

**Current Limits:**
• Daily transfer limit: ₹1,00,000
• International limit: ₹5,00,000
• Your available balance: ₹{user.account_balance:,.2f}

Would you like me to guide you through any specific transfer type?"""

    # International banking
    elif intent == 'international':
        return f"""🌍 **International Banking Services**

**Supported Currencies:**
• USD (US Dollar) 🇺🇸
• EUR (Euro) 🇪🇺  
• GBP (British Pound) 🇬🇧
• JPY (Japanese Yen) 🇯🇵
• AUD (Australian Dollar) 🇦🇺
• CAD (Canadian Dollar) 🇨🇦
• And 6 more currencies!

**Features:**
• ⚡ Live exchange rates (updated hourly)
• 🔒 Secure international transfers  
• 📱 Multi-currency wallet support
• 📊 Exchange rate alerts
• 📄 Compliance with international regulations

**Transfer Times:**
• Same-day processing for major currencies
• 1-3 business days for delivery
• Weekend transfers processed Monday

**Fees:**
• Exchange margin: 1-2% above inter-bank rate
• Transfer fee: ₹200-500 depending on amount
• No hidden charges - all costs shown upfront

**Your Current Balance:** ₹{user.account_balance:,.2f}

Ready to make an international transfer? I can guide you through the process!"""

    # Split payments
    elif intent == 'split':
        return f"""👥 **Split Payment Feature**

**How It Works:**
1. Create a group expense with description
2. Add participant account numbers
3. System calculates equal splits automatically
4. Participants receive QR codes to pay
5. Track who has paid in real-time

**Perfect For:**
• 🍕 Restaurant bills with friends
• 🏠 Shared rent and utilities  
• 🎁 Group gifts and celebrations
• ✈️ Travel expenses
• 🛒 Group purchases

**Example Scenario:**
If you split ₹1,200 among 4 people:
• Each person pays: ₹300
• You organize and collect
• Automatic notifications sent
• QR codes for easy payment

**Your Current Wallet Balance:** ₹{user.wallet_balance:,.2f}
(Split payments use wallet for quick processing)

**Active Split Payments:**
{get_active_splits_summary(user)}

Want to create a new split payment or pay an existing one?"""

    # Help and support
    elif intent == 'help':
        return f"""🎯 **E-Bank Smart Assistant Help**

**I Can Help You With:**

**💰 Account Management:**
• Check balances and limits
• View transaction history
• Update profile information
• Security settings

**💸 Transactions:**
• Domestic money transfers
• International currency exchange
• QR code payments
• Deposit and withdrawal guidance

**👥 Group Features:**
• Create split payments
• Manage group expenses  
• Track payment status
• Generate payment QR codes

**📊 Financial Tools:**
• Budgeting insights and tips
• Spending analysis
• EMI calculators
• Compound interest calculations

**🔒 Security:**
• Account safety tips
• Fraud prevention
• PIN management
• Activity monitoring

**🌍 International:**
• Currency exchange rates
• Cross-border transfers
• Multi-currency accounts
• Compliance information

**Quick Commands:**
• "What's my balance?" - Get account info
• "Show transactions" - View history  
• "How to transfer money?" - Transfer guide
• "Create split payment" - Group expenses
• "Exchange rates" - Currency information

What would you like help with specifically?"""

    # Check for specific banking operations in query
    elif any(word in query_lower for word in ['pin', 'password', 'security']):
        return f"""🔐 **Account Security Information**

**Your Account Security:**
• Account Number: {user.account_number} ✅
• Mobile Verified: {user.mobile} ✅  
• Email Verified: {'✅' if user.email_verified else '❌ Pending verification'}
• PIN Protection: Active ✅

**Security Tips:**
• Never share your PIN with anyone
• Log out from public devices
• Monitor your transactions regularly
• Report suspicious activity immediately

**PIN Management:**
• Change PIN every 3-6 months
• Don't use obvious numbers (1234, birth year)
• Visit any branch to reset forgotten PIN
• Use different PINs for different accounts

**If You Suspect Fraud:**
1. Change your PIN immediately
2. Contact customer service: 1800-XXX-XXXX
3. Review recent transactions
4. File a complaint if needed

Your account security status: 🟢 **SECURE**

Need help with any security settings?"""

    elif any(word in query_lower for word in ['loan', 'credit', 'emi']):
        return f"""💳 **Loan and Credit Information**

**Available Services:**
• Personal Loans: Up to ₹25,00,000
• Home Loans: Competitive rates from 8.5%
• Car Loans: Quick approval, low rates
• Education Loans: For higher studies
• Credit Cards: Multiple variants

**EMI Calculator:**
I can help calculate EMIs for any loan amount. Use the Smart Calculator feature in this chat for:
• Monthly EMI calculations
• Total interest payable
• Loan comparison
• Savings goal planning

**Pre-qualification Check:**
Based on your account activity:
• Account Age: Active since {user.created_at.strftime('%B %Y')}
• Current Balance: ₹{user.account_balance:,.2f}
• Transaction History: Available for review

**Next Steps:**
• Use the EMI calculator below
• Visit nearest branch for application
• Submit income documents
• Get instant pre-approval

**Customer Service:** 1800-XXX-XXXX
**Online Application:** Available in our main banking portal

Would you like me to calculate EMI for a specific loan amount?"""

    elif any(word in query_lower for word in ['budget', 'saving', 'invest']):
        return f"""📈 **Personal Finance & Budgeting**

**Your Financial Overview:**
• Current Balance: ₹{user.account_balance:,.2f}
• Wallet Balance: ₹{user.wallet_balance:,.2f}
• Account Age: {(datetime.now() - user.created_at).days} days

**Smart Budgeting Tips:**
• 💡 Follow 50-30-20 rule: 50% needs, 30% wants, 20% savings
• 📊 Track expenses using our History section
• 🎯 Set monthly spending limits
• 💰 Automate savings transfers

**Available Tools:**
• **Budgeting Dashboard:** Visualize spending patterns
• **Savings Calculator:** Plan your financial goals
• **Expense Categories:** Track where money goes
• **Monthly Reports:** Automated insights

**Investment Options:**
• Fixed Deposits: 6-8% returns
• Mutual Funds: SIP starting ₹500
• Gold Investment: Digital gold available
• Insurance Plans: Life and health coverage

**Personalized Suggestions:**
Based on your transaction history, I recommend:
1. Set up automatic savings of ₹{int(user.account_balance * 0.1):,} monthly
2. Use split payments to track group expenses
3. Monitor international transfer costs
4. Consider fixed deposits for emergency fund

Want detailed budgeting analysis? Visit the Enhanced Budgeting section!"""

    # General fallback with context-aware response
    else:
        # Try to extract specific information from the query
        if 'account number' in query_lower:
            return f"Your account number is **{user.account_number}**. This 8-digit number uniquely identifies your E-Bank account."
        elif 'mobile' in query_lower or 'phone' in query_lower:
            return f"Your registered mobile number is **{user.mobile}**. This is used for SMS alerts and verification."
        elif 'email' in query_lower:
            return f"Your registered email is **{user.email}**. Verification status: {'✅ Verified' if user.email_verified else '❌ Pending verification'}"
        elif 'name' in query_lower:
            return f"Hello **{user.name}**! Your account is registered under this name."
        elif any(word in query_lower for word in ['time', 'date', 'when']):
            return f"Current time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}. Your account was created on {user.created_at.strftime('%B %d, %Y')}."
        else:
            return f"""🤔 **I'm here to help with your banking needs!**

I understand you're asking: "{query}"

**I can help you with:**
• 💰 Account balance and transaction queries
• 💸 Money transfers (domestic & international)  
• 👥 Split payments and group expenses
• 🔒 Security and account management
• 📊 Budgeting and financial planning
• 🌍 Currency exchange and rates
• 🧮 EMI and loan calculations

**Quick Examples:**
• "What's my balance?"
• "Show recent transactions"  
• "How to send money abroad?"
• "Create a split payment"
• "Calculate EMI for ₹5 lakh loan"

**Need Immediate Help?**
• Customer Service: 1800-XXX-XXXX (24/7)
• Visit nearest branch
• Email: support@ebank.com

Could you please be more specific about what you'd like help with?"""

def get_active_splits_summary(user):
    """Get summary of user's active split payments"""
    try:
        # Organized splits
        organized = SplitPayment.query.filter_by(
            organizer_account=user.account_number,
            status='pending'
        ).count()
        
        # Participant splits where user hasn't paid
        participant_splits = SplitPayment.query.filter(
            SplitPayment.participants.cast(JSONB).contains([user.account_number])
        ).filter(
            ~SplitPayment.paid_by.cast(JSONB).contains([user.account_number])
        ).count()
        
        if organized == 0 and participant_splits == 0:
            return "No active split payments"
        
        summary = ""
        if organized > 0:
            summary += f"• {organized} split(s) you organized\n"
        if participant_splits > 0:  
            summary += f"• {participant_splits} pending payment(s)"
            
        return summary
        
    except Exception as e:
        return "Split payment status unavailable"

# Update the existing chatbot routes in your app.py

@app.route('/enhanced_chatbot', methods=['GET', 'POST'])
def enhanced_chatbot():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    response = None
    current_time = datetime.now().strftime('%I:%M %p')
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            response = enhanced_chatbot_response(query, user)
            log_user_activity(user.account_number, 'chatbot_query', {'query': query})
    
    return render_template('enhanced_chatbot.html', 
                         user=user, 
                         response=response, 
                         current_time=current_time)

@app.route('/chatbot_api', methods=['POST'])
def chatbot_api():
    if not is_user_logged_in():
        return jsonify({'error': 'Not authenticated', 'redirect': '/landing_page'})
    
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'})
        
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'No query provided'})
        
        # Generate response using enhanced chatbot
        response = enhanced_chatbot_response(query, user)
        
        # Log the interaction
        log_user_activity(user.account_number, 'chatbot_api_query', {'query': query})
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'user_name': user.name
        })
        
    except Exception as e:
        print(f"Chatbot API error: {e}")
        return jsonify({'error': 'Internal server error'})
    
@app.route('/')
def landing_page():
    return render_template('enhanced_landing.html')

@app.route('/verify_email/<token>')
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    if user:
        user.email_verified = True
        user.email_verification_token = None
        db.session.commit()
        flash('Email verified successfully! You can now log in.', 'success')
    else:
        flash('Invalid verification token.', 'error')
    return redirect(url_for('landing_page'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'a123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            log_admin_action(username, 'login', description='Admin login successful')
            return redirect(url_for('admin_dashboard'))
        else:
            log_admin_action(username, 'login_failed', description='Invalid credentials')
            return render_template('enhanced_landing.html', admin_error='Invalid credentials')
    
    return redirect(url_for('landing_page'))

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        pin = request.form['pin']
        email = request.form.get('email', '')
        
        user = User.query.filter_by(mobile=mobile, pin=pin).first()
        
        if user:
            if not user.is_active:
                log_user_activity(user.account_number, 'login_failed', {'reason': 'account_suspended'})
                return render_template('enhanced_landing.html', user_error='Account is suspended. Please contact admin.')
            
            if email and user.email != email:
                log_user_activity(user.account_number, 'login_failed', {'reason': 'email_mismatch'})
                return render_template('enhanced_landing.html', user_error='Email does not match account records')
            
            if not user.email_verified:
                return render_template('enhanced_landing.html', 
                                     user_error='Please verify your email before logging in', 
                                     show_resend=True, user_email=user.email)
            
            session['user_account'] = user.account_number
            session['user_name'] = user.name
            log_user_activity(user.account_number, 'login', {'success': True})
            return redirect(url_for('enhanced_customer_dashboard'))
        else:
            return render_template('enhanced_landing.html', user_error='Invalid credentials')
    
    return redirect(url_for('landing_page'))

@app.route('/resend_verification')
def resend_verification():
    email = request.args.get('email')
    if email:
        user = User.query.filter_by(email=email).first()
        if user and not user.email_verified:
            if send_verification_email(user):
                flash('Verification email sent!', 'success')
            else:
                flash('Failed to send verification email', 'error')
    return redirect(url_for('landing_page'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    total_customers = User.query.count()
    active_customers = User.query.filter_by(is_active=True).count()
    total_bank_balance = db.session.query(db.func.sum(User.account_balance)).scalar() or 0
    total_wallet_balance = db.session.query(db.func.sum(User.wallet_balance)).scalar() or 0
    
    recent_activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).limit(10).all()
    
    return render_template('enhanced_admin_dashboard.html',
                         total_customers=total_customers,
                         active_customers=active_customers,
                         total_bank_balance=total_bank_balance,
                         total_wallet_balance=total_wallet_balance,
                         recent_activities=recent_activities)

from sqlalchemy.dialects.postgresql import JSONB

@app.route('/enhanced_customer_dashboard')
def enhanced_customer_dashboard():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    recent_transactions = Transaction.query.filter_by(
        account_number=user.account_number
    ).order_by(Transaction.timestamp.desc()).limit(5).all()
    
    # Get pending split payments (PostgreSQL JSONB compliant)
    

    pending_splits = SplitPayment.query.filter(
    SplitPayment.participants.cast(JSONB).contains([user.account_number])
).filter(
    ~SplitPayment.paid_by.cast(JSONB).contains([user.account_number])
).count()

    
    return render_template('enhanced_customer_dashboard.html', 
                           user=user, 
                           recent_transactions=recent_transactions,
                           pending_splits=pending_splits)


@app.route('/enhanced_create_account', methods=['GET', 'POST'])
def enhanced_create_account():
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        address = request.form['address']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        aadhar = request.form['aadhar']
        pin = request.form['pin']
        preferred_currency = request.form.get('preferred_currency', 'INR')
        
        account_number = generate_account_number()
        while User.query.filter_by(account_number=account_number).first():
            account_number = generate_account_number()
        
        new_user = User(
            name=name, email=email, mobile=mobile, address=address,
            date_of_birth=dob, aadhar=aadhar, account_number=account_number,
            pin=pin, preferred_currency=preferred_currency, email_verified=False
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            log_admin_action(session['admin_username'], 'user_created', 
                           account_number, f'Created account for {name}')
            
            email_status = "Account created successfully"
            if send_verification_email(new_user):
                email_status = "Account created and verification email sent"
            
            return render_template('enhanced_create_account.html', 
                                 success=True, account_number=account_number,
                                 pin=pin, email_status=email_status)
        except Exception as e:
            db.session.rollback()
            return render_template('enhanced_create_account.html', error='Account creation failed')
    
    currencies = {
        'INR': 'Indian Rupee', 'USD': 'US Dollar', 'EUR': 'Euro', 
        'GBP': 'British Pound', 'JPY': 'Japanese Yen'
    }
    
    return render_template('enhanced_create_account.html', currencies=currencies)

@app.route('/split_payments')
def split_payments():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))

    user = get_current_user()
    
    try:
        # Splits organized by the user
        organized_splits = SplitPayment.query.filter_by(
            organizer_account=user.account_number
        ).all()
    except:
        organized_splits = []

    try:
        # Splits where the user is a participant
        participant_splits = SplitPayment.query.filter(
            SplitPayment.participants.cast(JSONB).contains([user.account_number])
        ).all()
    except:
        participant_splits = []

    return render_template(
        'split_payments.html', 
        user=user, 
        organized_splits=organized_splits,
        participant_splits=participant_splits
    )


    
    return render_template('split_payments.html', 
                         user=user, organized_splits=organized_splits,
                         participant_splits=participant_splits)

@app.route('/create_split_payment', methods=['POST'])
def create_split_payment():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    
    try:
        total_amount = float(request.form['total_amount'])
        description = request.form['description']
        participants_str = request.form['participants']
        currency = request.form.get('currency', 'INR')
        
        participants = [p.strip() for p in participants_str.split(',') if p.strip()]
        participants.append(user.account_number)
        participants = list(set(participants))
        
        if len(participants) < 2:
            flash('At least 2 participants required', 'error')
            return redirect(url_for('split_payments'))
        
        individual_amount = total_amount / len(participants)
        group_id = f"SPLIT_{user.account_number}_{int(datetime.utcnow().timestamp())}"
        
        split_payment = SplitPayment(
            group_id=group_id, organizer_account=user.account_number,
            total_amount=total_amount, currency=currency, description=description,
            participants=participants, individual_amount=individual_amount
        )
        
        db.session.add(split_payment)
        db.session.commit()
        
        log_user_activity(user.account_number, 'split_payment_created', 
                         {'group_id': group_id, 'amount': total_amount})
        
        flash(f'Split payment created! Group ID: {group_id}', 'success')
        
    except Exception as e:
        flash('Failed to create split payment', 'error')
    
    return redirect(url_for('split_payments'))

@app.route('/pay_split/<group_id>')
def pay_split(group_id):
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    split_payment = SplitPayment.query.filter_by(group_id=group_id).first()
    
    if not split_payment or user.account_number not in split_payment.participants:
        flash('Split payment not found', 'error')
        return redirect(url_for('split_payments'))
    
    return render_template('pay_split.html', user=user, split_payment=split_payment)

@app.route('/process_split_payment', methods=['POST'])
def process_split_payment():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    group_id = request.form['group_id']
    pin = request.form['pin']
    
    if pin != user.pin:
        flash('Invalid PIN', 'error')
        return redirect(url_for('pay_split', group_id=group_id))
    
    split_payment = SplitPayment.query.filter_by(group_id=group_id).first()
    
    if user.account_number in (split_payment.paid_by or []):
        flash('Already paid', 'info')
        return redirect(url_for('split_payments'))
    
    if user.wallet_balance < split_payment.individual_amount:
        flash('Insufficient wallet balance', 'error')
        return redirect(url_for('pay_split', group_id=group_id))
    
    try:
        user.wallet_balance -= split_payment.individual_amount
        
        organizer = User.query.filter_by(account_number=split_payment.organizer_account).first()
        if organizer:
            organizer.account_balance += split_payment.individual_amount
        
        paid_by_list = split_payment.paid_by or []
        paid_by_list.append(user.account_number)
        split_payment.paid_by = paid_by_list
        
        if len(paid_by_list) == len(split_payment.participants):
            split_payment.status = 'completed'
        
        transaction = Transaction(
            account_number=user.account_number, transaction_type='split_payment',
            amount=-split_payment.individual_amount, currency=split_payment.currency,
            details=f'Split payment: {split_payment.description}',
            split_group_id=group_id, balance_after=user.account_balance
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        log_user_activity(user.account_number, 'split_payment_paid', 
                         {'group_id': group_id, 'amount': split_payment.individual_amount})
        
        flash(f'Payment successful! Paid ₹{split_payment.individual_amount:.2f}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Payment failed', 'error')
    
    return redirect(url_for('split_payments'))

@app.route('/international_transactions')
def international_transactions():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    currencies = {
        'INR': 'Indian Rupee', 'USD': 'US Dollar', 'EUR': 'Euro',
        'GBP': 'British Pound', 'JPY': 'Japanese Yen', 'AUD': 'Australian Dollar',
        'CAD': 'Canadian Dollar', 'CHF': 'Swiss Franc', 'CNY': 'Chinese Yuan',
        'AED': 'UAE Dirham', 'SGD': 'Singapore Dollar', 'HKD': 'Hong Kong Dollar'
    }
    
    return render_template('international_transactions.html', user=user, currencies=currencies)

@app.route('/get_exchange_rate/<from_curr>/<to_curr>')
def get_exchange_rate_api(from_curr, to_curr):
    rate = get_exchange_rate(from_curr, to_curr)
    return jsonify({'rate': rate, 'timestamp': datetime.utcnow().isoformat()})

@app.route('/international_transfer', methods=['POST'])
def international_transfer():
    if not is_user_logged_in():
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    user = get_current_user()
    
    try:
        recipient_account = request.form['recipient_account']
        amount = float(request.form['amount'])
        from_currency = request.form['from_currency']
        to_currency = request.form['to_currency']
        pin = request.form['pin']
        
        if pin != user.pin:
            return jsonify({'success': False, 'error': 'Invalid PIN'})
        
        rate = get_exchange_rate(from_currency, to_currency)
        converted_amount = amount * rate
        
        # Check balance
        if from_currency == 'INR':
            if amount > user.account_balance:
                return jsonify({'success': False, 'error': 'Insufficient balance'})
            user.account_balance -= amount
        else:
            inr_equivalent = amount * get_exchange_rate(from_currency, 'INR')
            if inr_equivalent > user.account_balance:
                return jsonify({'success': False, 'error': 'Insufficient balance'})
            user.account_balance -= inr_equivalent
        
        # Find recipient and add to their account
        recipient = User.query.filter_by(account_number=recipient_account).first()
        if recipient:
            if to_currency == 'INR':
                recipient.account_balance += converted_amount
            else:
                inr_amount = converted_amount * get_exchange_rate(to_currency, 'INR')
                recipient.account_balance += inr_amount
        
        # Create transaction records
        sender_transaction = Transaction(
            account_number=user.account_number, transaction_type='currency_exchange',
            amount=-amount, currency=from_currency, exchange_rate=rate,
            converted_amount=converted_amount, details=f'International transfer to {recipient_account}',
            recipient_account=recipient_account, balance_after=user.account_balance
        )
        if recipient:
            recipient_transaction = Transaction(
                account_number=recipient_account, transaction_type='currency_exchange',
                amount=converted_amount if to_currency == 'INR' else converted_amount * get_exchange_rate(to_currency, 'INR'),
                currency=to_currency, exchange_rate=rate,
                details=f'International transfer from {user.account_number}',
                balance_after=recipient.account_balance
            )
            db.session.add(recipient_transaction)
        
        db.session.add(sender_transaction)
        db.session.commit()
        
        log_user_activity(user.account_number, 'international_transfer', {
            'amount': amount, 'from_currency': from_currency, 'to_currency': to_currency,
            'recipient': recipient_account, 'rate': rate
        })
        
        return jsonify({
            'success': True,
            'message': f'Transfer successful! Sent {amount} {from_currency}, recipient received {converted_amount:.2f} {to_currency}',
            'exchange_rate': rate
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/enhanced_profile')
def enhanced_profile():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    return render_template('enhanced_profile.html', user=user)

@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if not is_user_logged_in():
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    user = get_current_user()
    
    if 'profile_picture' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'})
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            filename = secure_filename(file.filename)
            timestamp = str(int(datetime.utcnow().timestamp()))
            filename = f"{user.account_number}_{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save and resize image
            image = Image.open(file.stream)
            image = image.resize((300, 300), Image.Resampling.LANCZOS)
            image.save(file_path, optimize=True, quality=85)
            
            # Update user profile
            user.profile_picture = filename
            db.session.commit()
            
            log_user_activity(user.account_number, 'profile_update', {'type': 'profile_picture'})
            
            return jsonify({
                'success': True, 
                'message': 'Profile picture updated successfully!',
                'image_url': f'/static/uploads/{filename}'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': 'Failed to upload profile picture'})
    else:
        return jsonify({'success': False, 'error': 'Invalid file type'})


# The corrected and completed code for the enhanced_operations route
@app.route('/enhanced_operations', methods=['GET', 'POST'])
def enhanced_operations():
    if not is_user_logged_in():
        flash('Please log in to perform operations.', 'warning')
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    if not user:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('landing_page'))

    message = None
    
    if request.method == 'POST':
        try:
            operation = request.form['operation']
            amount = float(request.form['amount'])
            pin = request.form['pin']
            currency = request.form.get('currency', 'INR')

            if pin != user.pin:
                message = "Invalid PIN."
                return render_template('enhanced_operations.html', user=user, message=message)

            if amount <= 0:
                message = "Amount must be greater than zero."
                return render_template('enhanced_operations.html', user=user, message=message)

            if operation == 'deposit':
                user.account_balance += amount
                
                transaction = Transaction(
                    account_number=user.account_number,
                    transaction_type='deposit',
                    amount=amount,
                    currency=currency,
                    details=f'Deposit of {amount} {currency}',
                    balance_after=user.account_balance
                )
                db.session.add(transaction)
                db.session.commit()
                
                log_user_activity(user.account_number, 'deposit', {'amount': amount})
                
                message = f"Successfully deposited ₹{amount:,.2f}."
                return render_template('enhanced_operations.html', user=user, message=message)

            elif operation == 'withdraw':
                if amount > user.account_balance:
                    message = "Insufficient balance."
                    return render_template('enhanced_operations.html', user=user, message=message)
                
                user.account_balance -= amount
                user.wallet_balance += amount  # Add to wallet for QR payments
                
                transaction = Transaction(
                    account_number=user.account_number,
                    transaction_type='withdrawal',
                    amount=-amount,
                    currency=currency,
                    details=f'Withdrawal of {amount} {currency} to wallet',
                    balance_after=user.account_balance
                )
                db.session.add(transaction)
                db.session.commit()
                
                log_user_activity(user.account_number, 'withdrawal', {'amount': amount})
                
                message = f"Successfully withdrew ₹{amount:,.2f} to wallet."
                return render_template('enhanced_operations.html', user=user, message=message)

            elif operation == 'transfer':
                to_account = request.form['to_account'].strip()
                
                # Validate recipient account
                recipient = User.query.filter_by(account_number=to_account).first()
                if not recipient:
                    message = "Recipient account not found."
                    return render_template('enhanced_operations.html', user=user, message=message)
                
                if to_account == user.account_number:
                    message = "Cannot transfer to your own account."
                    return render_template('enhanced_operations.html', user=user, message=message)
                
                if not recipient.is_active:
                    message = "Recipient account is inactive."
                    return render_template('enhanced_operations.html', user=user, message=message)
                
                if amount > user.account_balance:
                    message = "Insufficient balance."
                    return render_template('enhanced_operations.html', user=user, message=message)
                
                # Process transfer
                user.account_balance -= amount
                recipient.account_balance += amount
                
                # Create sender transaction
                sender_transaction = Transaction(
                    account_number=user.account_number,
                    transaction_type='transfer',
                    amount=-amount,
                    currency=currency,
                    details=f'Transfer to {recipient.name} ({to_account})',
                    recipient_account=to_account,
                    balance_after=user.account_balance
                )
                
                # Create recipient transaction
                recipient_transaction = Transaction(
                    account_number=to_account,
                    transaction_type='transfer',
                    amount=amount,
                    currency=currency,
                    details=f'Transfer from {user.name} ({user.account_number})',
                    recipient_account=user.account_number,
                    balance_after=recipient.account_balance
                )
                
                db.session.add(sender_transaction)
                db.session.add(recipient_transaction)
                db.session.commit()
                
                log_user_activity(user.account_number, 'transfer_sent', {
                    'amount': amount, 
                    'recipient': to_account,
                    'recipient_name': recipient.name
                })
                
                log_user_activity(to_account, 'transfer_received', {
                    'amount': amount,
                    'sender': user.account_number,
                    'sender_name': user.name
                })
                
                message = f"Successfully transferred ₹{amount:,.2f} to {recipient.name} ({to_account})."
                return render_template('enhanced_operations.html', user=user, message=message)
                
        except ValueError:
            message = "Invalid amount. Please enter a valid number."
        except Exception as e:
            db.session.rollback()
            print(f"Error during operation: {e}")
            message = f"Error during operation: {str(e)}"
    
    return render_template('enhanced_operations.html', user=user, message=message)
@app.route('/enhanced_history')
def enhanced_history():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    transactions = Transaction.query.filter_by(
        account_number=user.account_number
    ).order_by(Transaction.timestamp.desc()).all()
    
    # Calculate statistics for charts
    deposits = sum(t.amount for t in transactions if t.transaction_type == 'deposit' and t.amount > 0)
    withdrawals = sum(t.amount for t in transactions if t.transaction_type == 'withdraw' and t.amount > 0)
    transfers_out = sum(abs(t.amount) for t in transactions if t.transaction_type == 'transfer' and t.amount < 0)
    transfers_in = sum(t.amount for t in transactions if t.transaction_type == 'transfer' and t.amount > 0)
    
    chart_data = {
        'deposits': float(deposits),
        'withdrawals': float(withdrawals),
        'transfers_out': float(transfers_out),
        'transfers_in': float(transfers_in)
    }
    
    return render_template('enhanced_history.html', 
                         user=user, transactions=transactions, chart_data=chart_data)

@app.route('/enhanced_budgeting')
def enhanced_budgeting():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    
    # Get transaction data for last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    transactions = Transaction.query.filter(
        Transaction.account_number == user.account_number,
        Transaction.timestamp >= thirty_days_ago
    ).all()
    
    # Calculate category-wise spending
    spending_categories = {
        'deposits': sum(t.amount for t in transactions if t.transaction_type == 'deposit' and t.amount > 0),
        'withdrawals': sum(t.amount for t in transactions if t.transaction_type == 'withdraw' and t.amount > 0),
        'transfers': sum(abs(t.amount) for t in transactions if t.transaction_type == 'transfer' and t.amount != 0),
        'split_payments': sum(abs(t.amount) for t in transactions if t.transaction_type == 'split_payment'),
        'international': sum(abs(t.amount) for t in transactions if t.transaction_type == 'currency_exchange'),
        'account_balance': float(user.account_balance)
    }
    
    # Generate suggestions
    suggestions = []
    total_spending = spending_categories['withdrawals'] + spending_categories['transfers'] + spending_categories['split_payments'] + spending_categories['international']
    
    if spending_categories['deposits'] > 0 and total_spending > spending_categories['deposits']:
        suggestions.append("Consider reducing your spending as your expenses exceed your deposits.")
    if user.account_balance < 1000:
        suggestions.append("Your account balance is low. Consider making a deposit or reducing expenses.")
    if user.wallet_balance > user.account_balance:
        suggestions.append("You have more money in your wallet than your main account. Consider transferring some back.")
    if spending_categories['international'] > 0:
        suggestions.append("You've made international transactions. Monitor exchange rates for better deals.")
    if len(transactions) == 0:
        suggestions.append("Start using your account to see personalized budgeting insights.")
    
    return render_template('enhanced_budgeting.html', 
                         user=user, chart_data=spending_categories, suggestions=suggestions)

@app.route('/enhanced_users_management')
def enhanced_users_management():
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    users = User.query.all()
    total_customers = len(users)
    active_customers = User.query.filter_by(is_active=True).count()
    suspended_customers = User.query.filter_by(is_active=False).count()
    total_bank_balance = sum(user.account_balance for user in users)
    total_wallet_balance = sum(user.wallet_balance for user in users)
    
    # Get user activities for each user
    user_activities = {}
    for user in users:
        activities = UserActivity.query.filter_by(
            account_number=user.account_number
        ).order_by(UserActivity.timestamp.desc()).limit(5).all()
        user_activities[user.account_number] = activities
    
    return render_template('enhanced_users_management.html', 
                         users=users, total_customers=total_customers,
                         active_customers=active_customers, suspended_customers=suspended_customers,
                         total_bank_balance=total_bank_balance, total_wallet_balance=total_wallet_balance,
                         user_activities=user_activities)

@app.route('/suspend_user/<account_number>')
def suspend_user(account_number):
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    user = User.query.filter_by(account_number=account_number).first()
    if user:
        user.is_active = False
        db.session.commit()
        log_admin_action(session['admin_username'], 'user_suspended', 
                        account_number, f'Suspended user {user.name}')
        flash(f'User {user.name} suspended successfully', 'success')
    
    return redirect(url_for('enhanced_users_management'))

@app.route('/reactivate_user/<account_number>')
def reactivate_user(account_number):
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    user = User.query.filter_by(account_number=account_number).first()
    if user:
        user.is_active = True
        db.session.commit()
        log_admin_action(session['admin_username'], 'user_reactivated', 
                        account_number, f'Reactivated user {user.name}')
        flash(f'User {user.name} reactivated successfully', 'success')
    
    return redirect(url_for('enhanced_users_management'))

@app.route('/user_activity_logs/<account_number>')
def user_activity_logs(account_number):
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    user = User.query.filter_by(account_number=account_number).first()
    activities = UserActivity.query.filter_by(
        account_number=account_number
    ).order_by(UserActivity.timestamp.desc()).all()
    
    return render_template('user_activity_logs.html', user=user, activities=activities)

@app.route('/multi_currency_dashboard')
def multi_currency_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    currency_rates = CurrencyRate.query.all()
    
    # Calculate total balances in different currencies
    total_inr = db.session.query(db.func.sum(User.account_balance)).scalar() or 0
    
    currency_totals = {
        'INR': total_inr,
        'USD': total_inr * get_exchange_rate('INR', 'USD'),
        'EUR': total_inr * get_exchange_rate('INR', 'EUR'),
        'GBP': total_inr * get_exchange_rate('INR', 'GBP')
    }
    
    international_transactions = Transaction.query.filter_by(
        transaction_type='currency_exchange'
    ).order_by(Transaction.timestamp.desc()).limit(20).all()
    
    return render_template('multi_currency_dashboard.html',
                         currency_rates=currency_rates, currency_totals=currency_totals,
                         international_transactions=international_transactions)

@app.route('/analytics')
def analytics():
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    return render_template('enhanced_analytics.html')

@app.route('/analytics_data/<period>')
def analytics_data(period):
    if not is_admin_logged_in():
        return jsonify({'error': 'Unauthorized'})
    
    end_date = datetime.now()
    
    if period == 'weekly':
        start_date = end_date - timedelta(weeks=12)
        group_format = '%Y-W%U'
    elif period == 'monthly':
        start_date = end_date - timedelta(days=365)
        group_format = '%Y-%m'
    else:  # yearly
        start_date = end_date - timedelta(days=365*5)
        group_format = '%Y'
    
    transactions = Transaction.query.filter(Transaction.timestamp >= start_date).all()
    
    data = {}
    for transaction in transactions:
        period_key = transaction.timestamp.strftime(group_format)
        if period_key not in data:
            data[period_key] = {'deposits': 0, 'withdrawals': 0, 'transfers': 0, 'international': 0}
        
        if transaction.transaction_type == 'deposit':
            data[period_key]['deposits'] += transaction.amount
        elif transaction.transaction_type == 'withdraw':
            data[period_key]['withdrawals'] += transaction.amount
        elif transaction.transaction_type == 'transfer':
            data[period_key]['transfers'] += abs(transaction.amount)
        elif transaction.transaction_type == 'currency_exchange':
            data[period_key]['international'] += abs(transaction.amount)
    
    return jsonify(data)

@app.route('/transaction_reports', methods=['GET', 'POST'])
def transaction_reports():
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    transactions = []
    if request.method == 'POST':
        account_number = request.form.get('account_number', '').strip()
        from_date = request.form.get('from_date', '').strip()
        to_date = request.form.get('to_date', '').strip()
        
        query = Transaction.query
        
        if account_number:
            query = query.filter_by(account_number=account_number)
        
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
                query = query.filter(Transaction.timestamp >= from_date_obj)
            except ValueError:
                pass
        
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Transaction.timestamp < to_date_obj)
            except ValueError:
                pass
        
        transactions = query.order_by(Transaction.timestamp.desc()).all()
    
    return render_template('enhanced_transaction_reports.html', transactions=transactions)

@app.route('/search_profiles', methods=['GET', 'POST'])
def search_profiles():
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    user = None
    if request.method == 'POST':
        account_number = request.form['account_number']
        user = User.query.filter_by(account_number=account_number).first()
    
    return render_template('enhanced_search_profiles.html', user=user)

@app.route('/scan_and_pay', methods=['GET', 'POST'])
def scan_and_pay():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    message = None
    
    if request.method == 'POST':
        try:
            qr_data = request.form.get('qr_data')
            pin = request.form.get('pin')
            
            if pin != user.pin:
                message = "Invalid PIN"
            elif qr_data:
                try:
                    parts = qr_data.split(':')
                    if len(parts) >= 2:
                        to_account = parts[0]
                        amount = float(parts[1])
                        description = parts[2] if len(parts) > 2 else "QR Payment"
                        
                        to_user = User.query.filter_by(account_number=to_account).first()
                        
                        if not to_user:
                            message = "Invalid QR code: Recipient account not found"
                        elif amount <= 0:
                            message = "Invalid amount in QR code"
                        elif amount > user.wallet_balance:
                            message = "Insufficient wallet balance for this payment"
                        else:
                            user.wallet_balance -= amount
                            to_user.account_balance += amount
                            
                            transaction1 = Transaction(
                                account_number=user.account_number, transaction_type='transfer',
                                amount=-amount, details=f'QR Payment to {to_account}: {description}',
                                recipient_account=to_account, balance_after=user.account_balance
                            )
                            transaction2 = Transaction(
                                account_number=to_account, transaction_type='transfer',
                                amount=amount, details=f'QR Payment from {user.account_number}: {description}',
                                balance_after=to_user.account_balance
                            )
                            
                            db.session.add(transaction1)
                            db.session.add(transaction2)
                            db.session.commit()
                            
                            log_user_activity(user.account_number, 'qr_payment', 
                                            {'amount': amount, 'recipient': to_account})
                            
                            message = f"Payment successful! ₹{amount:.2f} sent to {to_account}"
                    else:
                        message = "Invalid QR code format"
                except ValueError:
                    message = "Invalid QR code: Amount must be a number"
                except Exception as e:
                    db.session.rollback()
                    message = "Payment failed. Please try again."
            else:
                message = "No QR code data received"
                
        except Exception as e:
            message = "An error occurred. Please try again."
    
    return render_template('enhanced_scan_and_pay.html', user=user, message=message)

@app.route('/generate_qr')
def generate_qr():
    if not is_user_logged_in():
        return redirect(url_for('landing_page'))
    
    user = get_current_user()
    amount = request.args.get('amount', '0')
    description = request.args.get('description', 'Payment Request')
    
    qr_data = f"{user.account_number}:{amount}:{description}"
    
    return render_template('enhanced_generate_qr.html', 
                         user=user, qr_data=qr_data, amount=amount, description=description)

@app.route('/download_statement/<statement_type>')
def download_statement(statement_type):
    if not (is_admin_logged_in() or is_user_logged_in()):
        return redirect(url_for('landing_page'))
    
    # Generate PDF statement
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add content to PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "E-Bank Enhanced Statement")
    
    if is_user_logged_in():
        user = get_current_user()
        account_number = user.account_number
    else:
        account_number = request.args.get('account', 'ALL')
    
    end_date = datetime.now()
    if statement_type == 'weekly':
        start_date = end_date - timedelta(weeks=1)
    elif statement_type == 'monthly':
        start_date = end_date - timedelta(days=30)
    else:  # yearly
        start_date = end_date - timedelta(days=365)
    
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    if account_number != 'ALL':
        p.drawString(50, 700, f"Account Number: {account_number}")
    
    # Get transactions
    query = Transaction.query.filter(Transaction.timestamp >= start_date)
    if account_number != 'ALL':
        query = query.filter_by(account_number=account_number)
    
    transactions = query.order_by(Transaction.timestamp.desc()).all()
    
    y_position = 650
    p.drawString(50, y_position, "Date")
    p.drawString(150, y_position, "Type")
    p.drawString(250, y_position, "Amount")
    p.drawString(350, y_position, "Currency")
    p.drawString(450, y_position, "Details")
    
    y_position -= 20
    for transaction in transactions:
        if y_position < 50:
            p.showPage()
            y_position = 750
        
        p.drawString(50, y_position, transaction.timestamp.strftime('%Y-%m-%d'))
        p.drawString(150, y_position, transaction.transaction_type)
        p.drawString(250, y_position, f"{transaction.amount:.2f}")
        p.drawString(350, y_position, transaction.currency or 'INR')
        p.drawString(450, y_position, (transaction.details or '')[:20])
        y_position -= 20
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer, as_attachment=True,
        download_name=f'ebank_statement_{statement_type}_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

from flask import redirect, url_for, session, flash

@app.route('/logout')
def logout():
    # Log actions before clearing session
    if is_user_logged_in():
        log_user_activity(session.get('user_account'), 'logout')
    elif is_admin_logged_in():
        log_admin_action(session.get('admin_username'), 'logout')
    
    # Clear session
    session.clear()

    # Optional flash message
    flash('You have been logged out successfully.', 'success')

    # Redirect to landing page
    return redirect(url_for('landing_page'))



@app.route('/delete_user/<account_number>')
def delete_user(account_number):
    if not is_admin_logged_in():
        return redirect(url_for('landing_page'))
    
    user = User.query.filter_by(account_number=account_number).first()
    if user:
        # Delete associated data
        Transaction.query.filter_by(account_number=account_number).delete()
        UserActivity.query.filter_by(account_number=account_number).delete()
        SplitPayment.query.filter_by(organizer_account=account_number).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        log_admin_action(session['admin_username'], 'user_deleted', 
                        account_number, f'Deleted user {user.name}')
        flash(f'User {user.name} deleted successfully', 'success')
    
    return redirect(url_for('enhanced_users_management'))


if __name__ == '__main__':
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Initialize enhanced features
            init_chatbot_knowledge()
            print("✅ Chatbot knowledge base initialized")
            
            # Create upload directory
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            print("✅ Upload directory created")
            
            print("\n🏦 E-Bank Enhanced Application")
            print("=" * 40)
            print("🌟 New Features Available:")
            print("  • Email verification during login")
            print("  • Split payments with QR codes")
            print("  • International transactions (12+ currencies)")
            print("  • Enhanced chatbot with voice support")
            print("  • Profile picture upload")
            print("  • Advanced analytics with pie charts")
            print("  • User activity monitoring")
            print("  • Multi-currency admin dashboard")
            print("=" * 40)
            print("🚀 Starting server at http://localhost:5000")
            print("👤 Admin Login: admin / a123")
            print("📧 Remember to configure email settings for verification")
            print("💱 Add exchange rate API key for currency features")
            print("=" * 40)

        except Exception as e:
            print(f"❌ Initialization error: {e}")
            print("Please check your database configuration and try again.")

    # 👇 This actually starts the server and keeps it running
    app.run(host='127.0.0.1', port=5000, debug=True)
