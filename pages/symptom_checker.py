import streamlit as st
from datetime import datetime
from utils.emergency_utils import EmergencyManager
from utils.location_utils import LocationManager
from utils.health_data import HealthDataManager

def show_symptom_checker():
    """Enhanced symptom checker with emergency detection"""
    st.title("🔍 Advanced Symptom Checker")
    st.write("Describe your symptoms for AI-powered assessment and emergency detection.")
    
    # Initialize managers
    emergency_manager = EmergencyManager()
    location_manager = LocationManager()
    health_manager = HealthDataManager()
    
    # Quick Emergency Access
    st.error("🚨 **EMERGENCY?** If you're experiencing a life-threatening emergency, call 911 immediately!")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚑 CALL 911 NOW", type="primary"):
            emergency_manager.call_emergency_services()
    with col2:
        if st.button("📍 FIND NEAREST HOSPITAL", type="secondary"):
            show_nearby_hospitals()
    
    st.markdown("---")
    
    # Symptom Input Form
    with st.form("symptom_form"):
        st.subheader("Describe Your Symptoms")
        
        # Primary symptoms
        primary_symptoms = st.text_area(
            "What symptoms are you experiencing?",
            placeholder="Describe your main symptoms in detail...",
            height=100
        )
        
        # Symptom details
        col1, col2 = st.columns(2)
        
        with col1:
            severity = st.select_slider(
                "Pain/Discomfort Level (1-10)",
                options=list(range(1, 11)),
                value=5,
                help="1 = Mild, 10 = Severe/Unbearable"
            )
            
            duration = st.selectbox(
                "How long have you had these symptoms?",
                ["Less than 1 hour", "1-6 hours", "6-24 hours", "1-3 days", "3-7 days", "More than 1 week"]
            )
        
        with col2:
            onset = st.selectbox(
                "How did symptoms start?",
                ["Sudden/Rapid", "Gradual", "After activity", "After eating", "While resting", "Other"]
            )
            
            triggers = st.multiselect(
                "What makes symptoms worse?",
                ["Movement", "Rest", "Eating", "Stress", "Weather", "Time of day", "Nothing specific"]
            )
        
        # Additional information
        additional_info = st.text_area(
            "Additional Information",
            placeholder="Any other relevant details, medical history, current medications, etc.",
            height=80
        )
        
        # Current location for emergency services
        location_consent = st.checkbox(
            "Share my location for emergency services if needed",
            help="This helps emergency responders find you quickly if critical symptoms are detected"
        )
        
        # Submit button
        analyze_button = st.form_submit_button("🔍 Analyze Symptoms", type="primary")
        
        if analyze_button and primary_symptoms:
            analyze_symptoms(
                primary_symptoms, severity, duration, onset, triggers, 
                additional_info, location_consent, emergency_manager, health_manager
            )

def analyze_symptoms(primary_symptoms, severity, duration, onset, triggers, additional_info, location_consent, emergency_manager, health_manager):
    """Analyze symptoms and provide recommendations"""
    
    # Combine all symptom information
    full_symptom_description = f"{primary_symptoms}. Severity: {severity}/10. Duration: {duration}. Onset: {onset}. "
    if triggers:
        full_symptom_description += f"Triggers: {', '.join(triggers)}. "
    if additional_info:
        full_symptom_description += f"Additional info: {additional_info}"
    
    # Assess severity and emergency status
    severity_assessment = emergency_manager.assess_symptom_severity(full_symptom_description, additional_info)
    
    # Display results
    display_symptom_analysis(severity_assessment, primary_symptoms, severity, emergency_manager)
    
    # Handle emergency situations
    if severity_assessment['is_emergency']:
        handle_emergency_situation(severity_assessment, location_consent, emergency_manager)
    
    # Save symptom record
    if st.session_state.get('username'):
        save_symptom_record(full_symptom_description, severity_assessment, health_manager)

def display_symptom_analysis(severity_assessment, primary_symptoms, severity_level, emergency_manager):
    """Display the symptom analysis results"""
    
    recommendation = severity_assessment['recommendation']
    
    # Display severity alert
    if recommendation['level'] == "CRITICAL":
        st.error(f"🚨 **{recommendation['level']}** - {recommendation['message']}")
    elif recommendation['level'] == "URGENT":
        st.error(f"⚠️ **{recommendation['level']}** - {recommendation['message']}")
    elif recommendation['level'] == "CONCERNING":
        st.warning(f"⚠️ **{recommendation['level']}** - {recommendation['message']}")
    else:
        st.info(f"ℹ️ **{recommendation['level']}** - {recommendation['message']}")
    
    # Recommended action
    st.subheader(f"**Recommended Action: {recommendation['action']}**")
    
    # Detailed analysis
    with st.expander("📊 Detailed Analysis"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Severity Score", f"{severity_assessment['severity_score']}/10")
            st.metric("User-Reported Pain Level", f"{severity_level}/10")
        
        with col2:
            st.write("**Detected Conditions:**")
            if severity_assessment['detected_conditions']:
                for condition in severity_assessment['detected_conditions']:
                    st.write(f"• {condition['condition'].replace('_', ' ').title()}")
            else:
                st.write("• No specific emergency conditions detected")
    
    # First aid instructions if applicable
    if severity_assessment['detected_conditions']:
        st.subheader("🩹 First Aid Instructions")
        primary_condition = severity_assessment['detected_conditions'][0]['condition']
        instructions = emergency_manager.get_emergency_instructions(primary_condition)
        
        for i, instruction in enumerate(instructions, 1):
            st.write(f"{instruction}")

def handle_emergency_situation(severity_assessment, location_consent, emergency_manager):
    """Handle emergency situation with immediate actions"""
    
    st.error("🚨 **EMERGENCY SITUATION DETECTED**")
    
    # Activate emergency mode
    st.session_state.emergency_mode = True
    emergency_manager.activate_emergency_mode(severity_assessment)
    
    # Emergency action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚑 CALL 911", type="primary", key="emergency_911"):
            emergency_manager.call_emergency_services()
    
    with col2:
        if st.button("📞 NOTIFY CONTACTS", type="secondary", key="emergency_contacts"):
            emergency_manager.notify_emergency_contacts("Critical symptoms detected via symptom checker")
    
    with col3:
        if st.button("🏥 FIND HOSPITALS", type="secondary", key="emergency_hospitals"):
            show_nearby_hospitals()
    
    # Location sharing
    if location_consent:
        st.info("📍 Your location is ready to be shared with emergency services.")
        if st.button("📍 SHARE LOCATION NOW", key="share_location"):
            emergency_manager.share_location()

def show_nearby_hospitals():
    """Show nearby hospitals and emergency facilities"""
    st.subheader("🏥 Nearby Emergency Facilities")
    
    location_manager = LocationManager()
    emergency_manager = EmergencyManager()
    
    # Get nearby hospitals
    hospitals = location_manager.find_nearby_facilities("hospitals", max_distance=25)
    
    if hospitals:
        for hospital in hospitals:
            with st.expander(f"🏥 {hospital['name']} - {hospital['distance']} miles"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Address:** {hospital['address']}")
                    st.write(f"**Phone:** {hospital['phone']}")
                    st.write(f"**Distance:** {hospital['distance']} miles")
                    
                    if hospital.get('emergency_room'):
                        st.success("✅ Emergency Room Available")
                    if hospital.get('trauma_center'):
                        st.success("✅ Trauma Center")
                
                with col2:
                    # Get directions button
                    directions_url = location_manager.get_directions_url(hospital['address'])
                    st.link_button("🗺️ Get Directions", directions_url)
                    
                    # Call hospital button
                    st.write(f"📞 Call: {hospital['phone']}")
    else:
        st.warning("No hospitals found nearby. Please contact 911 for emergency assistance.")
    
    # Show map if possible
    show_emergency_map(hospitals)

def show_emergency_map(facilities):
    """Show emergency facilities on a map"""
    try:
        import folium
        from streamlit_folium import st_folium
        
        location_manager = LocationManager()
        user_location = location_manager.get_current_location()
        
        if user_location:
            # Create map centered on user location
            m = folium.Map(
                location=[user_location['lat'], user_location['lng']],
                zoom_start=12
            )
            
            # Add user location marker
            folium.Marker(
                [user_location['lat'], user_location['lng']],
                popup="Your Location",
                tooltip="You are here",
                icon=folium.Icon(color='blue', icon='home')
            ).add_to(m)
            
            # Add hospital markers
            for facility in facilities:
                color = 'red' if facility.get('trauma_center') else 'orange'
                icon = 'plus' if facility.get('emergency_room') else 'info-sign'
                
                popup_text = f"""
                <b>{facility['name']}</b><br>
                {facility['address']}<br>
                📞 {facility['phone']}<br>
                📍 {facility['distance']} miles away
                """
                
                folium.Marker(
                    [facility['coordinates']['lat'], facility['coordinates']['lng']],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=facility['name'],
                    icon=folium.Icon(color=color, icon=icon)
                ).add_to(m)
            
            # Display map
            st.subheader("🗺️ Emergency Facilities Map")
            st_folium(m, width=700, height=400)
        
    except ImportError:
        st.info("Map functionality requires additional packages. Showing list view only.")

def save_symptom_record(symptoms, severity_assessment, health_manager):
    """Save symptom record to user's health data"""
    try:
        username = st.session_state.get('username')
        if username:
            symptom_data = {
                "symptoms": symptoms,
                "severity_score": severity_assessment['severity_score'],
                "is_emergency": severity_assessment['is_emergency'],
                "recommendation": severity_assessment['recommendation'],
                "detected_conditions": severity_assessment['detected_conditions']
            }
            
            health_manager.add_health_record(username, "symptoms", symptom_data)
            st.success("✅ Symptom record saved to your health profile.")
    
    except Exception as e:
        st.error(f"Failed to save symptom record: {str(e)}")

def show_symptom_history():
    """Show user's symptom history"""
    if st.session_state.get('username'):
        health_manager = HealthDataManager()
        symptoms = health_manager.get_symptoms_history(st.session_state.username, days=30)
        
        if symptoms:
            st.subheader("📋 Recent Symptom History")
            
            for symptom in symptoms:
                with st.expander(f"Symptoms on {symptom['timestamp'][:10]}"):
                    st.write(symptom['data']['symptoms'])
                    
                    if symptom['data']['is_emergency']:
                        st.error("🚨 Emergency-level symptoms detected")
                    
                    st.write(f"**Severity Score:** {symptom['data']['severity_score']}/10")
                    st.write(f"**Recommendation:** {symptom['data']['recommendation']['action']}")
        else:
            st.info("No recent symptom records found.")
