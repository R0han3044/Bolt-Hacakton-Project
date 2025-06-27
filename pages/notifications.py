import streamlit as st
from datetime import datetime, timedelta
from utils.notification_utils import NotificationManager
from utils.auth_utils import AuthManager

def show_notifications():
    """Display notifications page"""
    st.title("🔔 Notifications & Alerts")
    st.write("Manage your health notifications, reminders, and emergency alerts.")
    
    notification_manager = NotificationManager()
    auth_manager = AuthManager()
    username = st.session_state.get('username')
    
    if not username:
        st.error("Please log in to view notifications.")
        return
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📬 All Notifications", "⚙️ Settings", "👥 Emergency Contacts", "📱 SMS Setup"])
    
    with tab1:
        show_all_notifications(notification_manager, username)
    
    with tab2:
        show_notification_settings(notification_manager, username)
    
    with tab3:
        show_emergency_contacts(auth_manager, username)
    
    with tab4:
        show_sms_setup()

def show_all_notifications(notification_manager, username):
    """Display all notifications for user"""
    st.subheader("📬 Your Notifications")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_type = st.selectbox(
            "Filter by type:",
            ["All", "SMS", "EMAIL", "HEALTH_REMINDER", "EMERGENCY"]
        )
    
    with col2:
        days_back = st.selectbox("Show notifications from:", [7, 30, 90, 365])
    
    with col3:
        show_read = st.checkbox("Include read notifications", value=True)
    
    # Get notifications
    notification_type = None if filter_type == "All" else filter_type
    notifications = notification_manager.get_notifications(
        user=username, 
        notification_type=notification_type,
        limit=50
    )
    
    # Filter by date
    cutoff_date = datetime.now() - timedelta(days=days_back)
    notifications = [
        n for n in notifications 
        if datetime.fromisoformat(n['timestamp']) >= cutoff_date
    ]
    
    # Filter by read status
    if not show_read:
        notifications = [n for n in notifications if not n.get('read', False)]
    
    if notifications:
        # Display notifications
        for notification in notifications:
            display_notification(notification, notification_manager)
        
        # Mark all as read button
        unread_count = len([n for n in notifications if not n.get('read', False)])
        if unread_count > 0:
            if st.button(f"Mark all {unread_count} notifications as read"):
                for notification in notifications:
                    if not notification.get('read', False):
                        notification_manager.mark_notification_read(notification['id'])
                st.success("All notifications marked as read!")
                st.rerun()
    
    else:
        st.info("No notifications found for the selected criteria.")
    
    # Unread count summary
    unread_count = notification_manager.get_unread_count(username)
    if unread_count > 0:
        st.info(f"You have {unread_count} unread notifications.")

def display_notification(notification, notification_manager):
    """Display individual notification"""
    timestamp = datetime.fromisoformat(notification['timestamp'])
    time_str = timestamp.strftime("%Y-%m-%d %H:%M")
    
    # Determine notification style
    is_read = notification.get('read', False)
    is_emergency = notification['type'] == 'EMERGENCY' or 'emergency' in notification.get('message', '').lower()
    
    # Create container with appropriate styling
    if is_emergency:
        container = st.error if not is_read else st.info
    elif notification['status'] == 'failed':
        container = st.warning
    else:
        container = st.success if notification['status'] == 'sent' else st.info
    
    with st.expander(
        f"{'🔴' if not is_read else '⚪'} {notification['type']} - {time_str}",
        expanded=not is_read
    ):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**Type:** {notification['type']}")
            st.write(f"**Status:** {notification['status'].title()}")
            
            if notification.get('recipient'):
                st.write(f"**Recipient:** {notification['recipient']}")
            
            st.write(f"**Message:**")
            st.write(notification['message'])
            
            if notification.get('details'):
                st.write(f"**Details:** {notification['details']}")
        
        with col2:
            st.write(f"**Time:** {time_str}")
            
            if not is_read:
                if st.button(f"Mark as read", key=f"read_{notification['id']}"):
                    notification_manager.mark_notification_read(notification['id'])
                    st.rerun()

def show_notification_settings(notification_manager, username):
    """Display notification settings"""
    st.subheader("⚙️ Notification Settings")
    
    # Health reminders
    st.write("**Health Reminders**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        medication_reminders = st.checkbox("Medication reminders", value=True)
        appointment_reminders = st.checkbox("Appointment reminders", value=True)
        vitals_reminders = st.checkbox("Vital signs check reminders", value=False)
    
    with col2:
        wellness_tips = st.checkbox("Daily wellness tips", value=False)
        emergency_alerts = st.checkbox("Emergency alerts", value=True)
        system_notifications = st.checkbox("System notifications", value=True)
    
    # Reminder frequency
    st.write("**Reminder Frequency**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        medication_freq = st.selectbox("Medication reminders:", ["Daily", "Twice daily", "Weekly", "As needed"])
        vitals_freq = st.selectbox("Vitals check reminders:", ["Daily", "Weekly", "Monthly", "Never"])
    
    with col2:
        wellness_freq = st.selectbox("Wellness tips:", ["Daily", "Weekly", "Monthly", "Never"])
        checkup_freq = st.selectbox("Checkup reminders:", ["Monthly", "Quarterly", "Annually", "Never"])
    
    # Create sample reminders
    st.write("**Quick Setup**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Create Medication Reminder"):
            message = "Time to take your medication! Don't forget to log it in your health dashboard."
            notification_manager.create_health_reminder(username, "medication", message)
            st.success("Medication reminder created!")
    
    with col2:
        if st.button("Create Vitals Reminder"):
            message = "Weekly vitals check: Please record your blood pressure, weight, and temperature."
            notification_manager.create_health_reminder(username, "vitals", message)
            st.success("Vitals reminder created!")
    
    with col3:
        if st.button("Create Wellness Tip"):
            message = "Wellness tip: Drink at least 8 glasses of water today for optimal hydration!"
            notification_manager.create_health_reminder(username, "wellness", message)
            st.success("Wellness reminder created!")
    
    # Save settings
    if st.button("Save Settings", type="primary"):
        # In a real app, these settings would be saved to user preferences
        st.success("✅ Notification settings saved!")

def show_emergency_contacts(auth_manager, username):
    """Display and manage emergency contacts"""
    st.subheader("👥 Emergency Contacts")
    st.write("These contacts will be notified in case of medical emergencies.")
    
    # Get current emergency contacts
    contacts = auth_manager.get_emergency_contacts(username)
    
    # Display current contacts
    if contacts:
        st.write("**Current Emergency Contacts:**")
        
        for i, contact in enumerate(contacts):
            with st.expander(f"{contact['name']} - {contact['relationship']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Name:** {contact['name']}")
                    st.write(f"**Phone:** {contact['phone']}")
                    st.write(f"**Relationship:** {contact['relationship']}")
                    
                    if contact.get('email'):
                        st.write(f"**Email:** {contact['email']}")
                
                with col2:
                    if st.button(f"Remove", key=f"remove_{i}"):
                        if auth_manager.remove_emergency_contact(username, i):
                            st.success("Contact removed!")
                            st.rerun()
                        else:
                            st.error("Failed to remove contact.")
    else:
        st.info("No emergency contacts configured.")
    
    # Add new contact form
    st.write("**Add New Emergency Contact:**")
    
    with st.form("add_emergency_contact"):
        col1, col2 = st.columns(2)
        
        with col1:
            contact_name = st.text_input("Name*")
            contact_phone = st.text_input("Phone Number* (include country code)", placeholder="+1234567890")
        
        with col2:
            relationship = st.selectbox("Relationship*", [
                "Spouse/Partner", "Parent", "Child", "Sibling", 
                "Friend", "Caregiver", "Doctor", "Other"
            ])
            contact_email = st.text_input("Email (optional)")
        
        submitted = st.form_submit_button("Add Contact", type="primary")
        
        if submitted:
            if not contact_name or not contact_phone:
                st.error("Name and phone number are required.")
            else:
                new_contact = {
                    "name": contact_name,
                    "phone": contact_phone,
                    "relationship": relationship,
                    "email": contact_email if contact_email else None
                }
                
                if auth_manager.add_emergency_contact(username, new_contact):
                    st.success("✅ Emergency contact added!")
                    st.rerun()
                else:
                    st.error("Failed to add emergency contact.")
    
    # Test emergency notification
    if contacts:
        st.write("**Test Emergency Notification:**")
        if st.button("🧪 Send Test Alert", help="Send a test emergency alert to all contacts"):
            from utils.notification_utils import NotificationManager
            notification_manager = NotificationManager()
            
            test_message = f"TEST ALERT: This is a test emergency notification from HealthAssist AI for user {username}. Please disregard - this is only a test."
            
            results = notification_manager.send_emergency_alert(
                contacts, 
                "Test Alert", 
                {"address": "Test Location"}, 
                "test"
            )
            
            for result in results:
                if result['success']:
                    st.success(f"✅ Test alert sent to {result['contact']} via {result['method']}")
                else:
                    st.error(f"❌ Failed to send test alert to {result['contact']}")

def show_sms_setup():
    """Display SMS setup information"""
    st.subheader("📱 SMS Notification Setup")
    
    st.write("SMS notifications are powered by Twilio for reliable emergency alerts.")
    
    # Check if Twilio is configured
    import os
    twilio_configured = all([
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN"),
        os.getenv("TWILIO_PHONE_NUMBER")
    ])
    
    if twilio_configured:
        st.success("✅ SMS notifications are configured and ready!")
        st.write("Your emergency alerts will be sent via SMS to your configured contacts.")
    else:
        st.warning("⚠️ SMS notifications are not fully configured.")
        st.write("To enable SMS notifications, the following environment variables need to be set:")
        
        st.code("""
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
        """)
        
        st.write("**How to set up Twilio SMS:**")
        st.write("1. Sign up for a free Twilio account at https://www.twilio.com/")
        st.write("2. Get your Account SID and Auth Token from the Twilio Console")
        st.write("3. Purchase or get a free Twilio phone number")
        st.write("4. Set the environment variables in your deployment")
    
    # SMS best practices
    with st.expander("📋 SMS Best Practices"):
        st.write("**For Emergency Contacts:**")
        st.write("• Include country code in phone numbers (e.g., +1234567890)")
        st.write("• Verify phone numbers can receive SMS messages")
        st.write("• Test emergency alerts periodically")
        st.write("• Keep contact information up to date")
        
        st.write("**Message Limits:**")
        st.write("• Emergency messages are prioritized")
        st.write("• Standard SMS character limits apply (160 characters)")
        st.write("• Long messages may be split into multiple SMS")
    
    # Test SMS functionality
    if twilio_configured:
        st.write("**Test SMS Functionality:**")
        
        with st.form("test_sms"):
            test_phone = st.text_input("Test phone number (with country code):", placeholder="+1234567890")
            test_message = st.text_area("Test message:", value="This is a test SMS from HealthAssist AI.")
            
            if st.form_submit_button("Send Test SMS"):
                if test_phone and test_message:
                    from utils.notification_utils import NotificationManager
                    notification_manager = NotificationManager()
                    
                    success = notification_manager.send_sms(test_phone, test_message)
                    
                    if success:
                        st.success("✅ Test SMS sent successfully!")
                    else:
                        st.error("❌ Failed to send test SMS. Check phone number and try again.")
                else:
                    st.error("Please enter both phone number and message.")
