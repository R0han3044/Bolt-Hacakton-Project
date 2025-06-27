import streamlit as st
from datetime import datetime
from utils.emergency_utils import EmergencyManager

def show_chat_page():
    """Display AI chat interface"""
    from utils.bolt_ai_traces import bolt_traces
    
    # Add Bolt.new styling
    st.markdown("""
    <div class="bolt-card">
        <h1 class="bolt-gradient-text">💬 AI Health Assistant</h1>
        <p style="color: rgba(255,255,255,0.8);">Powered by Bolt.new AI • Advanced medical guidance and support</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency detection manager
    emergency_manager = EmergencyManager()
    
    # Initialize chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat interface
    st.subheader("Chat History")
    
    # Display chat history with Bolt.new styling
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="bolt-card" style="background: rgba(99, 102, 241, 0.1); border-left: 4px solid #6366f1;">
                    <strong>👤 You ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bolt-card" style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981;">
                    <strong>🤖 Bolt AI Assistant ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.subheader("Send Message")
    
    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_area("Type your health question or describe your symptoms:", height=100)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            send_button = st.form_submit_button("Send", type="primary")
        with col2:
            emergency_button = st.form_submit_button("🚨 EMERGENCY", type="secondary")
        
        if send_button and user_message:
            # Add user message to chat history
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': timestamp
            })
            
            # Check for emergency keywords
            severity_assessment = emergency_manager.assess_symptom_severity(user_message)
            
            # Generate AI response
            ai_response = generate_ai_response(user_message, severity_assessment)
            
            # Add AI response to chat history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': ai_response,
                'timestamp': timestamp
            })
            
            # Check if emergency mode should be activated
            if severity_assessment['is_emergency']:
                st.session_state.emergency_mode = True
                emergency_manager.activate_emergency_mode(severity_assessment)
                st.error("🚨 EMERGENCY DETECTED - Switching to emergency mode!")
            
            st.rerun()
        
        if emergency_button:
            st.session_state.emergency_mode = True
            st.rerun()
    
    # Quick health topics
    st.subheader("Quick Health Topics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💊 Medication Questions"):
            quick_message = "I have questions about my medications and potential side effects."
            add_quick_message(quick_message)
    
    with col2:
        if st.button("🤒 Symptom Check"):
            quick_message = "I'm experiencing some symptoms and would like guidance."
            add_quick_message(quick_message)
    
    with col3:
        if st.button("🏃 Wellness Tips"):
            quick_message = "I'd like some general wellness and health tips."
            add_quick_message(quick_message)
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

def add_quick_message(message):
    """Add quick message to chat"""
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.chat_history.append({
        'role': 'user',
        'content': message,
        'timestamp': timestamp
    })
    
    # Generate AI response
    ai_response = generate_ai_response(message)
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': ai_response,
        'timestamp': timestamp
    })
    
    st.rerun()

def generate_ai_response(user_message, severity_assessment=None):
    """Generate AI response using Hugging Face models"""
    from utils.ai_models import model_manager
    
    # Check if AI models are loaded
    if hasattr(st.session_state, 'model_manager') and st.session_state.model_manager:
        try:
            # Use the AI model for response generation
            ai_response = st.session_state.model_manager.generate_medical_response(user_message)
            if ai_response:
                return ai_response
        except Exception as e:
            st.warning(f"AI model temporarily unavailable: {str(e)}")
    
    # Fallback to rule-based responses if AI is not available
    
    message_lower = user_message.lower()
    
    # Emergency responses
    if severity_assessment and severity_assessment['is_emergency']:
        recommendation = severity_assessment['recommendation']
        response = f"⚠️ **{recommendation['level']} MEDICAL SITUATION DETECTED**\n\n"
        response += f"**Immediate Action Required:** {recommendation['action']}\n\n"
        response += f"{recommendation['message']}\n\n"
        response += "**Detected concerning symptoms:**\n"
        for condition in severity_assessment['detected_conditions']:
            response += f"- {condition['condition'].replace('_', ' ').title()} (severity: {condition['severity']})\n"
        response += "\n**Please seek immediate medical attention. Do not delay care for serious symptoms.**"
        return response
    
    # Symptom-related responses
    if any(word in message_lower for word in ['pain', 'hurt', 'ache', 'symptom', 'sick', 'feel']):
        response = "I understand you're experiencing some discomfort. Can you describe:\n\n"
        response += "• **Location**: Where exactly do you feel the pain/symptom?\n"
        response += "• **Severity**: On a scale of 1-10, how would you rate it?\n"
        response += "• **Duration**: How long have you been experiencing this?\n"
        response += "• **Triggers**: What makes it better or worse?\n\n"
        response += "**Important**: If you're experiencing severe pain, difficulty breathing, chest pain, or other serious symptoms, please seek immediate medical attention or call emergency services."
        return response
    
    # Medication responses
    if any(word in message_lower for word in ['medication', 'medicine', 'drug', 'pill', 'prescription']):
        response = "I can provide general information about medications, but please remember:\n\n"
        response += "• **Always consult your healthcare provider** before starting, stopping, or changing medications\n"
        response += "• **Check with your pharmacist** about drug interactions\n"
        response += "• **Read medication labels carefully** and follow instructions\n"
        response += "• **Report side effects** to your doctor\n\n"
        response += "What specific medication questions do you have? I can provide general information to help you have an informed discussion with your healthcare provider."
        return response
    
    # Wellness responses
    if any(word in message_lower for word in ['wellness', 'health', 'tips', 'advice', 'lifestyle']):
        response = "Here are some general wellness tips for maintaining good health:\n\n"
        response += "**🏃 Physical Activity**: Aim for 150 minutes of moderate exercise per week\n"
        response += "**🥗 Nutrition**: Eat a balanced diet with plenty of fruits and vegetables\n"
        response += "**😴 Sleep**: Get 7-9 hours of quality sleep each night\n"
        response += "**💧 Hydration**: Drink plenty of water throughout the day\n"
        response += "**🧘 Stress Management**: Practice stress-reduction techniques like meditation\n"
        response += "**👩‍⚕️ Regular Checkups**: See your healthcare provider for preventive care\n\n"
        response += "Is there a specific aspect of wellness you'd like to know more about?"
        return response
    
    # General health response
    response = "Thank you for your message. As an AI health assistant, I can provide general health information and guidance, but I cannot replace professional medical advice.\n\n"
    response += "**How I can help:**\n"
    response += "• General health information and education\n"
    response += "• Symptom assessment and guidance on when to seek care\n"
    response += "• Wellness tips and lifestyle recommendations\n"
    response += "• Medication information (general)\n\n"
    response += "**When to seek immediate care:**\n"
    response += "• Chest pain or difficulty breathing\n"
    response += "• Severe pain or sudden onset symptoms\n"
    response += "• Signs of stroke (face drooping, arm weakness, speech difficulty)\n"
    response += "• Severe allergic reactions\n"
    response += "• Any life-threatening emergency\n\n"
    response += "Could you please provide more details about your health question or concern?"
    
    return response
