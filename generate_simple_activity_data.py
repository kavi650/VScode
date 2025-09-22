#!/usr/bin/env python3
"""
Simple script to generate realistic system activity data
"""

import random
from datetime import datetime, timedelta
from app import app, db, User, UserActivity

def generate_simple_activities():
    """Generate simple realistic activity data"""
    
    with app.app_context():
        # Get existing users
        users = User.query.all()
        if not users:
            print("No users found in database")
            return
        
        print(f"Found {len(users)} users")
        for user in users:
            print(f"  Account: {user.account_number}, Name: {user.name}")
        
        # Clear existing fake activities first
        UserActivity.query.delete()
        db.session.commit()
        print("Cleared existing activities")
        
        # Activity types
        activity_types = ['login', 'login_failed', 'transaction', 'profile_update', 'notification_sent', 'security_alert']
        
        # Generate 50 realistic activities
        for i in range(50):
            try:
                # Random user
                user = random.choice(users)
                
                # Random timestamp within last 30 days
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 24)
                minutes_ago = random.randint(0, 60)
                timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                
                # Random IP address
                ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                
                # Random user agent
                user_agent = random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
                ])
                
                # Activity type and details
                activity_type = random.choice(activity_types)
                
                if activity_type == 'login':
                    details = {
                        "browser": random.choice(["Chrome", "Firefox", "Safari"]),
                        "os": random.choice(["Windows 11", "macOS", "Android"]),
                        "login_method": random.choice(["password", "fingerprint"]),
                        "location": random.choice(["New York, USA", "London, UK", "Tokyo, Japan"])
                    }
                elif activity_type == 'login_failed':
                    details = {
                        "reason": random.choice(["invalid_password", "account_locked", "account_suspended"]),
                        "attempts": random.randint(1, 3)
                    }
                elif activity_type == 'transaction':
                    details = {
                        "amount": round(random.uniform(100, 5000), 2),
                        "currency": random.choice(["USD", "EUR"]),
                        "recipient": f"ACC{random.randint(10000000, 99999999)}",
                        "status": random.choice(["completed", "pending"])
                    }
                elif activity_type == 'profile_update':
                    details = {
                        "update_type": random.choice(["email_changed", "phone_changed", "address_updated"]),
                        "verified": random.choice([True, False])
                    }
                elif activity_type == 'notification_sent':
                    details = {
                        "notification_type": random.choice(["transaction_alert", "security_alert"]),
                        "channel": random.choice(["email", "sms"]),
                        "status": random.choice(["delivered", "failed"])
                    }
                else:  # security_alert
                    details = {
                        "alert_type": random.choice(["suspicious_login", "multiple_failed_attempts"]),
                        "severity": random.choice(["medium", "high"])
                    }
                
                # Create activity
                activity = UserActivity(
                    account_number=user.account_number,
                    activity_type=activity_type,
                    ip_address=ip,
                    user_agent=user_agent,
                    details=details,
                    timestamp=timestamp
                )
                
                db.session.add(activity)
                db.session.commit()
                
                print(f"Added activity {i+1}: {activity_type} for account {user.account_number}")
                
            except Exception as e:
                print(f"Error adding activity {i+1}: {e}")
                db.session.rollback()
                continue
        
        print(f"Successfully generated activities!")

if __name__ == "__main__":
    generate_simple_activities()