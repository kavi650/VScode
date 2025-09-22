#!/usr/bin/env python3
"""
Script to generate realistic system activity data for the bank application.
This replaces fake login failures with diverse, realistic activities.
"""

from app import app, db, UserActivity, User, Transaction
from datetime import datetime, timedelta
import random
import json

def generate_real_activity_data():
    """Generate realistic system activity data"""
    with app.app_context():
        # Clear existing fake data
        print("Clearing existing fake login failures...")
        UserActivity.query.filter_by(activity_type='login_failed').delete()
        db.session.commit()
        
        # Get real users
        users = User.query.all()
        if not users:
            print("No users found in database. Creating some test users...")
            return
        
        print(f"Found {len(users)} users. Generating realistic activities...")
        
        # Generate activities for the last 30 days
        activities = []
        now = datetime.utcnow()
        
        for i in range(100):  # Generate 100 activities
            # Random timestamp within last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Select random user
            user = random.choice(users)
            
            # Generate realistic activity based on probability
            activity_type = random.choices([
                'login', 'login_failed', 'transaction', 'profile_update', 
                'security_alert', 'notification_sent', 'password_reset'
            ], weights=[30, 10, 25, 15, 8, 10, 2])[0]
            
            # Generate appropriate details for each activity type
            if activity_type == 'login':
                details = {
                    'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                    'os': random.choice(['Windows 10', 'Windows 11', 'macOS', 'Android', 'iOS']),
                    'login_method': random.choice(['password', 'fingerprint', 'face_recognition'])
                }
                
            elif activity_type == 'login_failed':
                reasons = ['invalid_password', 'account_locked', 'account_suspended', 'invalid_otp']
                details = {'reason': random.choice(reasons)}
                
            elif activity_type == 'transaction':
                transaction_types = ['transfer', 'payment', 'deposit', 'withdrawal']
                transaction_type = random.choice(transaction_types)
                amount = round(random.uniform(100, 50000), 2)
                
                details = {
                    'type': transaction_type,
                    'amount': amount,
                    'currency': random.choice(['INR', 'USD', 'EUR']),
                    'method': random.choice(['upi', 'neft', 'rtgs', 'card']),
                    'status': random.choice(['success', 'pending', 'failed'])
                }
                
            elif activity_type == 'profile_update':
                update_types = ['email_changed', 'phone_changed', 'address_updated', 'password_changed']
                details = {'update_type': random.choice(update_types)}
                
            elif activity_type == 'security_alert':
                alert_types = ['suspicious_login', 'multiple_failed_attempts', 'unusual_transaction']
                details = {
                    'alert_type': random.choice(alert_types),
                    'risk_level': random.choice(['low', 'medium', 'high'])
                }
                
            elif activity_type == 'notification_sent':
                notification_types = ['transaction_alert', 'security_alert', 'promotional', 'reminder']
                details = {
                    'notification_type': random.choice(notification_types),
                    'channel': random.choice(['email', 'sms', 'push', 'in_app']),
                    'status': random.choice(['sent', 'delivered', 'failed'])
                }
                
            elif activity_type == 'password_reset':
                details = {
                    'reset_method': random.choice(['email', 'sms', 'security_questions']),
                    'status': random.choice(['initiated', 'completed', 'failed'])
                }
            
            # Generate random IP address
            ip_address = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            
            # Generate user agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
            ]
            user_agent = random.choice(user_agents)
            
            activity = UserActivity(
                account_number=user.account_number,
                activity_type=activity_type,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                timestamp=timestamp
            )
            
            activities.append(activity)
        
        # Insert activities one by one to avoid bulk insert issues
        for activity in activities:
            db.session.add(activity)
        db.session.commit()
        
        print(f"Successfully generated {len(activities)} realistic activities!")
        
        # Show summary
        summary = {}
        for activity in activities:
            summary[activity.activity_type] = summary.get(activity.activity_type, 0) + 1
        
        print("\nActivity Summary:")
        for activity_type, count in sorted(summary.items()):
            print(f"  {activity_type}: {count}")

if __name__ == '__main__':
    generate_real_activity_data()