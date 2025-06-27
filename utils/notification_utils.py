import os
import json
from datetime import datetime
import streamlit as st

class NotificationManager:
    def __init__(self):
        self.notifications_file = "data/notifications.json"
        self.ensure_data_directory()
        self.load_notifications()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_notifications(self):
        """Load notifications from JSON file"""
        try:
            with open(self.notifications_file, 'r') as f:
                self.notifications = json.load(f)
        except FileNotFoundError:
            self.notifications = []
            self.save_notifications()
    
    def save_notifications(self):
        """Save notifications to JSON file"""
        with open(self.notifications_file, 'w') as f:
            json.dump(self.notifications, f, indent=2)
    
    def send_sms(self, phone_number, message):
        """Send SMS notification using Twilio"""
        try:
            # Import Twilio client
            from twilio.rest import Client
            
            # Get Twilio credentials from environment
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
            
            if not all([account_sid, auth_token, twilio_phone]):
                # Log the attempt but don't fail
                self.log_notification("SMS", phone_number, message, "failed", "Twilio credentials not configured")
                st.warning("SMS notifications not configured. Check Twilio credentials.")
                return False
            
            # Initialize Twilio client
            client = Client(account_sid, auth_token)
            
            # Send SMS
            message_obj = client.messages.create(
                body=message,
                from_=twilio_phone,
                to=phone_number
            )
            
            # Log successful notification
            self.log_notification("SMS", phone_number, message, "sent", f"SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            # Log failed notification
            self.log_notification("SMS", phone_number, message, "failed", str(e))
            st.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def send_email(self, email_address, subject, message):
        """Send email notification"""
        # This would integrate with an email service like SendGrid, AWS SES, etc.
        # For now, just log the attempt
        self.log_notification("EMAIL", email_address, f"{subject}: {message}", "simulated", "Email service not configured")
        st.info(f"Email notification logged for {email_address}")
        return True
    
    def log_notification(self, notification_type, recipient, message, status, details=""):
        """Log notification attempt"""
        notification_record = {
            "id": len(self.notifications),
            "type": notification_type,
            "recipient": recipient,
            "message": message,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "user": st.session_state.get("username", "system")
        }
        
        self.notifications.append(notification_record)
        self.save_notifications()
        
        return notification_record["id"]
    
    def create_emergency_notification(self, emergency_type, location_data, severity="high"):
        """Create standardized emergency notification"""
        timestamp = datetime.now().strftime("%I:%M %p on %B %d, %Y")
        user = st.session_state.get("username", "Emergency User")
        
        message = f"🚨 EMERGENCY ALERT\n\n"
        message += f"User: {user}\n"
        message += f"Type: {emergency_type}\n"
        message += f"Time: {timestamp}\n"
        
        if location_data:
            address = location_data.get("address", "Location not available")
            message += f"Location: {address}\n"
            
            if "lat" in location_data and "lng" in location_data:
                message += f"Coordinates: {location_data['lat']:.6f}, {location_data['lng']:.6f}\n"
        
        message += f"\nSeverity: {severity.upper()}\n"
        message += f"Please respond immediately or call emergency services."
        
        return message
    
    def send_emergency_alert(self, contacts, emergency_type, location_data, severity="high"):
        """Send emergency alert to multiple contacts"""
        message = self.create_emergency_notification(emergency_type, location_data, severity)
        results = []
        
        for contact in contacts:
            if "phone" in contact:
                success = self.send_sms(contact["phone"], message)
                results.append({
                    "contact": contact["name"],
                    "method": "SMS",
                    "phone": contact["phone"],
                    "success": success
                })
            
            if "email" in contact:
                subject = f"🚨 EMERGENCY ALERT - {emergency_type}"
                success = self.send_email(contact["email"], subject, message)
                results.append({
                    "contact": contact["name"],
                    "method": "EMAIL",
                    "email": contact["email"],
                    "success": success
                })
        
        return results
    
    def get_notifications(self, user=None, notification_type=None, limit=50):
        """Get notifications with optional filtering"""
        notifications = self.notifications.copy()
        
        # Filter by user
        if user:
            notifications = [n for n in notifications if n.get("user") == user]
        
        # Filter by type
        if notification_type:
            notifications = [n for n in notifications if n.get("type") == notification_type]
        
        # Sort by timestamp (newest first)
        notifications.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit results
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        for notification in self.notifications:
            if notification["id"] == notification_id:
                notification["read"] = True
                notification["read_at"] = datetime.now().isoformat()
                self.save_notifications()
                return True
        return False
    
    def get_unread_count(self, user=None):
        """Get count of unread notifications"""
        notifications = self.get_notifications(user=user)
        unread = [n for n in notifications if not n.get("read", False)]
        return len(unread)
    
    def create_health_reminder(self, user, reminder_type, message, schedule_time=None):
        """Create health reminder notification"""
        reminder = {
            "id": len(self.notifications),
            "type": "HEALTH_REMINDER",
            "user": user,
            "reminder_type": reminder_type,
            "message": message,
            "schedule_time": schedule_time or datetime.now().isoformat(),
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        self.notifications.append(reminder)
        self.save_notifications()
        
        return reminder["id"]
