import streamlit as st

# Set page configuration first before any other Streamlit commands
st.set_page_config(
    page_title="HealthAssist AI - Emergency Ready",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import json
from datetime import datetime
import sys

# Import utility modules
from utils.auth_utils import AuthManager
from utils.health_data import HealthDataManager
from utils.emergency_utils import EmergencyManager
from utils.bolt_ai_traces import bolt_traces

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'model_loaded' not in st.session_state:
        st.session_state.model_loaded = False
    if 'model_manager' not in st.session_state:
        st.session_state.model_manager = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'emergency_mode' not in st.session_state:
        st.session_state.emergency_mode = False
    if 'user_location' not in st.session_state:
        st.session_state.user_location = None

def check_colab_environment():
    """Check if running in Google Colab and setup accordingly"""
    try:
        import google.colab
        st.info("Running in Google Colab environment detected")
        
        # Check if ngrok is configured
        try:
            from pyngrok import ngrok
            active_tunnels = ngrok.get_tunnels()
            if not active_tunnels:
                st.warning("No ngrok tunnel detected. You may need to set up ngrok for external access.")
        except:
            st.warning("Ngrok not configured. External access may be limited.")
            
        return True
    except ImportError:
        return False

def display_system_info():
    """Display system information"""
    with st.expander("System Information"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Environment:**")
            st.write(f"Python: {sys.version.split()[0]}")
            st.write("Running on CPU")
        
        with col2:
            st.write("**AI Model Status:**")
            if st.session_state.model_loaded:
                st.success("Hugging Face Models Ready")
            else:
                st.info("AI Models Available for Loading")
            
            st.write("**Authentication:**")
            if st.session_state.authenticated:
                st.success(f"Logged in as: {st.session_state.username}")
            else:
                st.error("Not authenticated")

def emergency_banner():
    """Display emergency banner if in emergency mode"""
    if st.session_state.emergency_mode:
        st.error("🚨 EMERGENCY MODE ACTIVE - Critical symptoms detected!")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🚑 CALL AMBULANCE", type="primary"):
                emergency_manager = EmergencyManager()
                emergency_manager.call_emergency_services()
        with col2:
            if st.button("📍 SHARE LOCATION", type="secondary"):
                emergency_manager = EmergencyManager()
                emergency_manager.share_location()
        with col3:
            if st.button("❌ EXIT EMERGENCY", help="Only if symptoms have improved"):
                st.session_state.emergency_mode = False
                st.rerun()

def login_page():
    """Display login page"""
    # Inject Bolt.new styling
    bolt_traces.inject_bolt_style()
    
    # Show Bolt.new style header
    bolt_traces.show_bolt_header()
    
    # Check if running in Colab
    is_colab = check_colab_environment()
    
    # Show AI development trace
    bolt_traces.show_ai_development_trace()
    
    # Display system info
    display_system_info()
    
    # Show development phases
    bolt_traces.show_development_phases()
    
    st.markdown("---")
    
    # Login form
    with st.form("login_form"):
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            auth_manager = AuthManager()
            if auth_manager.authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_role = auth_manager.get_user_role(username)
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    # Default accounts info
    with st.expander("📋 Demo Accounts"):
        st.write("**Available Demo Accounts:**")
        st.write("- Admin: `admin` / `admin123`")
        st.write("- Doctor: `doctor` / `doctor123`")
        st.write("- Patient: `patient` / `patient123`")
    
    # Emergency access
    st.markdown("---")
    st.subheader("🚨 Emergency Access")
    if st.button("🆘 EMERGENCY - SKIP LOGIN", type="primary"):
        st.session_state.authenticated = True
        st.session_state.username = "emergency_user"
        st.session_state.user_role = "emergency"
        st.session_state.emergency_mode = True
        st.rerun()
    
    # Model loading section
    st.markdown("---")
    st.subheader("🤖 AI Healthcare Assistant")
    
    if not st.session_state.model_loaded:
        if st.button("🚀 Initialize AI Models", type="primary"):
            load_model()
    else:
        st.success("✅ Hugging Face AI models are ready!")
        if st.button("🔄 Reload Models"):
            st.session_state.model_loaded = False
            st.session_state.model_manager = None
            st.rerun()

def load_model():
    """Initialize AI models with Bolt.new development experience"""
    from utils.ai_models import model_manager
    
    # Show Bolt.new style AI generation simulation
    bolt_traces.simulate_ai_generation("AI Healthcare Models")
    
    # Show terminal-style commands
    bolt_commands = [
        "bolt init healthcare-ai-project",
        "bolt add huggingface-models",
        "bolt deploy medical-assistant",
        "bolt optimize performance"
    ]
    bolt_traces.show_bolt_terminal(bolt_commands)
    
    # Load actual models
    model_status = model_manager.get_model_status()
    st.session_state.model_loaded = True
    st.session_state.model_manager = model_manager
    
    if model_status["api_available"]:
        st.success("⚡ Bolt AI models deployed successfully!")
        if not model_status["api_token_configured"]:
            st.info("💡 Add HUGGINGFACE_API_TOKEN for enhanced Bolt AI features")
    else:
        st.warning("⚠️ Bolt AI running in fallback mode - add API token for full features")
    
    # Show development metrics
    bolt_traces.show_bolt_metrics()

def main_app():
    """Main application interface"""
    # Import page modules here to avoid early Streamlit calls
    import pages.chat as chat_page
    import pages.symptom_checker as symptom_page
    import pages.wellness_dashboard as wellness_page
    import pages.patient_management as patient_page
    import pages.notifications as notifications_page
    import pages.emergency_response as emergency_page
    
    # Emergency banner at top
    emergency_banner()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏥 HealthAssist AI")
        st.write(f"Welcome, {st.session_state.username}!")
        if st.session_state.user_role != "emergency":
            st.write(f"Role: {st.session_state.user_role.title()}")
        else:
            st.write("**Emergency Access Mode**")
        
        # Emergency button in sidebar
        if not st.session_state.emergency_mode:
            if st.button("🆘 EMERGENCY", type="primary", help="Activate emergency mode"):
                st.session_state.emergency_mode = True
                st.rerun()
        
        # Model status
        if st.session_state.model_loaded:
            st.success("🤖 AI Model Ready")
        else:
            st.error("🤖 AI Model Not Loaded")
            if st.button("Load Model"):
                load_model()
        
        st.markdown("---")
        
        # Navigation
        pages = {
            "🚨 Emergency Response": "emergency",
            "💬 AI Chat": "chat",
            "🔍 Symptom Checker": "symptom_checker",
            "📊 Wellness Dashboard": "wellness",
            "👥 Patient Management": "patients",
            "🔔 Notifications": "notifications"
        }
        
        # Filter pages based on user role
        if st.session_state.user_role == "patient":
            # Patients can't access patient management
            pages = {k: v for k, v in pages.items() if v != "patients"}
        elif st.session_state.user_role == "emergency":
            # Emergency users only see emergency and symptom checker
            pages = {
                "🚨 Emergency Response": "emergency",
                "🔍 Symptom Checker": "symptom_checker"
            }
        
        # Default to emergency page if in emergency mode
        if st.session_state.emergency_mode:
            selected_page = "🚨 Emergency Response"
        else:
            selected_page = st.selectbox("Navigate to:", list(pages.keys()))
        
        page_key = pages[selected_page]
        
        st.markdown("---")
        
        # Bolt AI Suggestions
        with st.expander("⚡ Bolt AI Suggestions"):
            if st.button("💡 Optimize Health Analysis"):
                st.info("Bolt AI: Enhanced symptom patterns detected")
            if st.button("🚀 Add Real-time Monitoring"):
                st.info("Bolt AI: Implementing live health tracking...")
            if st.button("📱 Mobile Optimization"):
                st.info("Bolt AI: Creating responsive mobile interface...")
        
        # System info
        with st.expander("System Info"):
            st.write("⚡ Powered by Bolt.new AI")
            st.write("Running on CPU")
            st.write("Emergency services ready")
            if st.session_state.user_location:
                st.write(f"Location: {st.session_state.user_location}")
        
        # Logout
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.emergency_mode = False
            st.rerun()
    
    # Main content area
    if page_key == "emergency":
        emergency_page.show_emergency_response()
    elif page_key == "chat":
        chat_page.show_chat_page()
    elif page_key == "symptom_checker":
        symptom_page.show_symptom_checker()
    elif page_key == "wellness":
        wellness_page.show_wellness_dashboard()
    elif page_key == "patients":
        patient_page.show_patient_management()
    elif page_key == "notifications":
        notifications_page.show_notifications()

def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
    else:
        # Inject Bolt styling for authenticated users too
        bolt_traces.inject_bolt_style()
        main_app()
    
    # Add Bolt.new footer
    bolt_traces.add_bolt_footer()

if __name__ == "__main__":
    main()
