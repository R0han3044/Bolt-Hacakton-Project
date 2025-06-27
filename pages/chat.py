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
                <div class="bolt-card" style="background: rgba(37, 99, 235, 0.1); border-left: 4px solid #2563eb; color: #1f2937;">
                    <strong>👤 You ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bolt-card" style="background: rgba(5, 150, 105, 0.1); border-left: 4px solid #059669; color: #1f2937;">
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
                
                # Show emergency hospital calling options
                show_emergency_hospital_calling(emergency_manager)
            
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


def show_emergency_hospital_calling(emergency_manager):
    """Show emergency hospital calling interface when dangerous symptoms detected"""
    from utils.location_utils import LocationManager
    
    st.error("🚨 DANGEROUS SYMPTOMS DETECTED - IMMEDIATE MEDICAL ATTENTION REQUIRED")
    
    location_manager = LocationManager()
    
    # Get nearest hospitals
    try:
        hospitals = location_manager.find_nearby_facilities("hospitals", 15)
        emergency_hospitals = [h for h in hospitals if h.get('emergency_room', False)]
        
        if emergency_hospitals:
            closest_hospital = emergency_hospitals[0]
            
            st.markdown(f"""
            <div class="bolt-card" style="background: rgba(220, 38, 38, 0.1); border-left: 4px solid #dc2626;">
                <h3 style="color: #dc2626;">🏥 NEAREST EMERGENCY HOSPITAL</h3>
                <p><strong>Name:</strong> {closest_hospital['name']}</p>
                <p><strong>Address:</strong> {closest_hospital['address']}</p>
                <p><strong>Phone:</strong> {closest_hospital['phone']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🚨 CALL HOSPITAL NOW", type="primary", key="emergency_call_hospital"):
                    st.error(f"CALLING {closest_hospital['name']}...")
                    st.info(f"Dial: {closest_hospital['phone']}")
                    emergency_manager.call_emergency_services()
            
            with col2:
                if st.button("📞 CALL 911", type="secondary", key="emergency_call_911"):
                    st.error("CALLING 911...")
                    st.info("Emergency services contacted")
                    emergency_manager.call_emergency_services()
            
            with col3:
                if st.button("🗺️ SHOW MAP", key="emergency_show_map"):
                    show_emergency_map_quick(emergency_hospitals[:3])
        
        else:
            # No hospitals found, show 911 option
            st.error("No nearby hospitals found - CALL 911 IMMEDIATELY")
            if st.button("📞 CALL 911 NOW", type="primary", key="emergency_911_only"):
                st.error("CALLING 911...")
                emergency_manager.call_emergency_services()
    
    except Exception as e:
        st.error("Error finding hospitals - CALL 911 IMMEDIATELY")
        if st.button("📞 CALL 911", type="primary", key="emergency_fallback_911"):
            st.error("CALLING 911...")
            emergency_manager.call_emergency_services()
    
    # Emergency instructions
    st.warning("""
    **EMERGENCY INSTRUCTIONS:**
    - Stay calm and call for help immediately
    - If symptoms worsen, call 911
    - Do not drive yourself to the hospital
    - Have someone stay with you if possible
    - Follow any instructions from medical professionals
    """)


def show_emergency_map_quick(hospitals):
    """Show quick emergency map"""
    import folium
    from streamlit_folium import st_folium
    
    st.subheader("🗺️ Emergency Hospitals Near You")
    
    # Create simple emergency map
    if hospitals:
        center_lat = hospitals[0]['coordinates']['lat']
        center_lng = hospitals[0]['coordinates']['lng']
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=13,
            tiles="OpenStreetMap"
        )
        
        for hospital in hospitals:
            folium.Marker(
                [hospital['coordinates']['lat'], hospital['coordinates']['lng']],
                popup=f"""
                <div>
                    <h4>{hospital['name']}</h4>
                    <p>{hospital['address']}</p>
                    <p>📞 {hospital['phone']}</p>
                    <button onclick="window.open('tel:{hospital['phone']}', '_self')" 
                            style="background: #dc2626; color: white; border: none; padding: 8px; border-radius: 4px;">
                        🚨 EMERGENCY CALL
                    </button>
                </div>
                """,
                tooltip=f"🚨 {hospital['name']} - EMERGENCY",
                icon=folium.Icon(color='red', icon='plus', prefix='fa')
            ).add_to(m)
        
        st_folium(m, width=700, height=400)
