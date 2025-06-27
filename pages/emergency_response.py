import streamlit as st
import folium
from datetime import datetime
from utils.emergency_utils import EmergencyManager
from utils.location_utils import LocationManager
from utils.notification_utils import NotificationManager
from utils.auth_utils import AuthManager

def show_emergency_response():
    """Display comprehensive emergency response interface"""
    st.title("🚨 Emergency Response Center")
    
    # Initialize managers
    emergency_manager = EmergencyManager()
    location_manager = LocationManager()
    notification_manager = NotificationManager()
    auth_manager = AuthManager()
    
    # Emergency status banner
    if st.session_state.get('emergency_mode', False):
        st.error("🚨 **EMERGENCY MODE ACTIVE** - Critical situation detected!")
        show_active_emergency_controls(emergency_manager, location_manager)
    else:
        st.info("Emergency response system ready. Use this page for medical emergencies and urgent care needs.")
    
    # Quick emergency actions at top
    show_emergency_quick_actions(emergency_manager, location_manager)
    
    st.markdown("---")
    
    # Main emergency tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚑 Emergency Services", 
        "🗺️ Emergency Map", 
        "🏥 Find Care", 
        "📋 First Aid", 
        "📞 Emergency Contacts"
    ])
    
    with tab1:
        show_emergency_services(emergency_manager, location_manager)
    
    with tab2:
        show_emergency_map(location_manager)
    
    with tab3:
        show_find_care(location_manager)
    
    with tab4:
        show_first_aid_guide(emergency_manager)
    
    with tab5:
        show_emergency_contacts_tab(auth_manager, notification_manager)

def show_active_emergency_controls(emergency_manager, location_manager):
    """Show active emergency controls when in emergency mode"""
    st.subheader("🚨 IMMEDIATE EMERGENCY ACTIONS")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚑 CALL 911", type="primary", key="main_911"):
            emergency_manager.call_emergency_services()
            st.success("Emergency services contacted!")
    
    with col2:
        if st.button("📍 SHARE LOCATION", type="secondary", key="main_location"):
            location_manager.get_current_location()
            emergency_manager.share_location()
            st.success("Location shared with emergency services!")
    
    with col3:
        if st.button("📞 NOTIFY CONTACTS", type="secondary", key="main_notify"):
            emergency_manager.notify_emergency_contacts("Emergency mode activated - immediate assistance needed")
            st.success("Emergency contacts notified!")
    
    with col4:
        if st.button("❌ EXIT EMERGENCY", help="Only if emergency is resolved"):
            st.session_state.emergency_mode = False
            st.success("Emergency mode deactivated")
            st.rerun()
    
    # Show current location if available
    location = location_manager.get_current_location()
    if location:
        st.info(f"📍 Current Location: {location.get('address', 'Location detected')}")

def show_emergency_quick_actions(emergency_manager, location_manager):
    """Show quick emergency action buttons"""
    st.subheader("⚡ Quick Emergency Actions")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🚑\nCall 911", key="quick_911"):
            emergency_manager.call_emergency_services()
    
    with col2:
        if st.button("🏥\nNearest Hospital", key="quick_hospital"):
            show_nearest_hospital(location_manager)
    
    with col3:
        if st.button("💊\nPoison Control", key="quick_poison"):
            show_poison_control_info()
    
    with col4:
        if st.button("🩹\nFirst Aid", key="quick_first_aid"):
            st.session_state.quick_first_aid = True
    
    with col5:
        if st.button("📞\nEmergency Contact", key="quick_contact"):
            show_quick_emergency_contacts()

def show_emergency_services(emergency_manager, location_manager):
    """Show emergency services section"""
    st.subheader("🚑 Emergency Services")
    
    # Emergency hotlines
    st.write("**Emergency Hotlines (US):**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("🚑 **Emergency Services:** 911")
        st.write("☎️ **Non-Emergency Police:** Call local number")
        st.write("🔥 **Fire Department:** 911")
        st.write("🚨 **Ambulance:** 911")
    
    with col2:
        st.write("☠️ **Poison Control:** 1-800-222-1222")
        st.write("🧠 **Suicide Prevention:** 988")
        st.write("👤 **Domestic Violence:** 1-800-799-7233")
        st.write("🆘 **Crisis Text Line:** Text HOME to 741741")
    
    st.markdown("---")
    
    # Symptom-based emergency assessment
    st.write("**Quick Symptom Assessment:**")
    
    with st.form("emergency_symptom_check"):
        symptoms = st.text_area(
            "Describe current symptoms or emergency situation:",
            placeholder="Describe what's happening right now...",
            height=100
        )
        
        urgency = st.radio(
            "How urgent is this situation?",
            ["Life-threatening emergency", "Very urgent", "Urgent", "Can wait for care"]
        )
        
        assess_button = st.form_submit_button("🔍 Assess Emergency Level", type="primary")
        
        if assess_button and symptoms:
            assessment = emergency_manager.assess_symptom_severity(symptoms, urgency)
            display_emergency_assessment(assessment, emergency_manager)

def display_emergency_assessment(assessment, emergency_manager):
    """Display emergency assessment results"""
    recommendation = assessment['recommendation']
    
    if recommendation['level'] in ['CRITICAL', 'URGENT']:
        st.error(f"🚨 **{recommendation['level']} EMERGENCY**")
        st.error(f"**Action Required:** {recommendation['action']}")
        st.error(recommendation['message'])
        
        # Auto-activate emergency mode for critical situations
        if recommendation['level'] == 'CRITICAL':
            st.session_state.emergency_mode = True
            st.error("🚨 **EMERGENCY MODE ACTIVATED AUTOMATICALLY**")
        
        # Show immediate actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚑 CALL 911 NOW", type="primary"):
                emergency_manager.call_emergency_services()
        with col2:
            if st.button("📞 ALERT CONTACTS", type="secondary"):
                emergency_manager.notify_emergency_contacts(f"Emergency assessment: {recommendation['level']}")
    
    elif recommendation['level'] == 'CONCERNING':
        st.warning(f"⚠️ **{recommendation['level']}**")
        st.warning(f"**Recommended:** {recommendation['action']}")
        st.warning(recommendation['message'])
    
    else:
        st.info(f"ℹ️ **{recommendation['level']}**")
        st.info(f"**Recommended:** {recommendation['action']}")
        st.info(recommendation['message'])
    
    # Show first aid instructions if applicable
    if assessment['detected_conditions']:
        condition = assessment['detected_conditions'][0]['condition']
        instructions = emergency_manager.get_emergency_instructions(condition)
        
        st.subheader("🩹 Immediate First Aid Instructions")
        for i, instruction in enumerate(instructions, 1):
            st.write(f"{i}. {instruction}")

def show_emergency_map(location_manager):
    """Show interactive emergency map"""
    st.subheader("🗺️ Emergency Facilities Map")
    
    # Get user location
    location = location_manager.get_current_location()
    
    if not location:
        st.error("Unable to get your location. Please enable location services.")
        return
    
    # Get nearby facilities
    hospitals = location_manager.find_nearby_facilities("hospitals", max_distance=25)
    pharmacies = location_manager.find_nearby_facilities("pharmacies", max_distance=10)
    urgent_care = location_manager.find_nearby_facilities("urgent_care", max_distance=15)
    
    # Create map
    try:
        # Create folium map centered on user location
        m = folium.Map(
            location=[location['lat'], location['lng']],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Add user location marker
        folium.Marker(
            [location['lat'], location['lng']],
            popup=folium.Popup("📍 Your Current Location", max_width=200),
            tooltip="You are here",
            icon=folium.Icon(color='blue', icon='home', prefix='fa')
        ).add_to(m)
        
        # Add hospital markers
        for hospital in hospitals:
            coords = hospital['coordinates']
            color = 'red' if hospital.get('trauma_center') else 'orange'
            
            popup_html = f"""
            <div style="width: 250px;">
                <h4>🏥 {hospital['name']}</h4>
                <p><strong>Address:</strong> {hospital['address']}</p>
                <p><strong>Phone:</strong> {hospital['phone']}</p>
                <p><strong>Distance:</strong> {hospital['distance']} miles</p>
                {'<p style="color: red;"><strong>✅ TRAUMA CENTER</strong></p>' if hospital.get('trauma_center') else ''}
                {'<p style="color: green;"><strong>✅ 24/7 EMERGENCY</strong></p>' if hospital.get('emergency_room') else ''}
            </div>
            """
            
            folium.Marker(
                [coords['lat'], coords['lng']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"🏥 {hospital['name']} ({hospital['distance']} mi)",
                icon=folium.Icon(color=color, icon='plus', prefix='fa')
            ).add_to(m)
        
        # Add pharmacy markers
        for pharmacy in pharmacies:
            coords = pharmacy['coordinates']
            
            popup_html = f"""
            <div style="width: 200px;">
                <h4>💊 {pharmacy['name']}</h4>
                <p><strong>Address:</strong> {pharmacy['address']}</p>
                <p><strong>Phone:</strong> {pharmacy['phone']}</p>
                <p><strong>Distance:</strong> {pharmacy['distance']} miles</p>
                <p><strong>Hours:</strong> {pharmacy.get('hours', 'Call for hours')}</p>
            </div>
            """
            
            folium.Marker(
                [coords['lat'], coords['lng']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"💊 {pharmacy['name']} ({pharmacy['distance']} mi)",
                icon=folium.Icon(color='green', icon='plus-square', prefix='fa')
            ).add_to(m)
        
        # Add urgent care markers
        for clinic in urgent_care:
            coords = clinic['coordinates']
            
            popup_html = f"""
            <div style="width: 200px;">
                <h4>🏪 {clinic['name']}</h4>
                <p><strong>Address:</strong> {clinic['address']}</p>
                <p><strong>Phone:</strong> {clinic['phone']}</p>
                <p><strong>Distance:</strong> {clinic['distance']} miles</p>
                <p><strong>Wait Time:</strong> {clinic.get('wait_time', 'Call for info')}</p>
            </div>
            """
            
            folium.Marker(
                [coords['lat'], coords['lng']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"🏪 {clinic['name']} ({clinic['distance']} mi)",
                icon=folium.Icon(color='purple', icon='clinic-medical', prefix='fa')
            ).add_to(m)
        
        # Display map using st.components for better integration
        st.markdown("**Legend:** 🏠 Your Location | 🏥 Hospitals | 💊 Pharmacies | 🏪 Urgent Care")
        
        # Since we can't directly use streamlit-folium, we'll show the map data in a table format
        st.write("**Emergency Facilities Near You:**")
        
        all_facilities = []
        
        # Add hospitals
        for hospital in hospitals:
            all_facilities.append({
                "Type": "🏥 Hospital",
                "Name": hospital['name'],
                "Distance": f"{hospital['distance']} miles",
                "Address": hospital['address'],
                "Phone": hospital['phone'],
                "Special": "🚨 Trauma Center" if hospital.get('trauma_center') else "Emergency Room"
            })
        
        # Add urgent care
        for clinic in urgent_care:
            all_facilities.append({
                "Type": "🏪 Urgent Care",
                "Name": clinic['name'],
                "Distance": f"{clinic['distance']} miles",
                "Address": clinic['address'],
                "Phone": clinic['phone'],
                "Special": f"Wait: {clinic.get('wait_time', 'Unknown')}"
            })
        
        # Add pharmacies
        for pharmacy in pharmacies:
            all_facilities.append({
                "Type": "💊 Pharmacy",
                "Name": pharmacy['name'],
                "Distance": f"{pharmacy['distance']} miles",
                "Address": pharmacy['address'],
                "Phone": pharmacy['phone'],
                "Special": pharmacy.get('hours', 'Call for hours')
            })
        
        # Sort by distance
        all_facilities.sort(key=lambda x: float(x['Distance'].split()[0]))
        
        # Display facilities
        for facility in all_facilities:
            with st.expander(f"{facility['Type']} {facility['Name']} - {facility['Distance']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Address:** {facility['Address']}")
                    st.write(f"**Phone:** {facility['Phone']}")
                    st.write(f"**Info:** {facility['Special']}")
                with col2:
                    directions_url = location_manager.get_directions_url(facility['Address'])
                    st.link_button("🗺️ Directions", directions_url)
        
    except Exception as e:
        st.error(f"Unable to load map: {str(e)}")
        st.info("Showing facility list instead:")
        show_facility_list(hospitals + pharmacies + urgent_care)

def show_facility_list(facilities):
    """Show facilities as a list when map fails"""
    for facility in facilities:
        with st.expander(f"{facility['name']} - {facility['distance']} miles"):
            st.write(f"**Address:** {facility['address']}")
            st.write(f"**Phone:** {facility['phone']}")
            if facility.get('emergency_room'):
                st.success("✅ Emergency Room Available")
            if facility.get('trauma_center'):
                st.error("🚨 Trauma Center")

def show_find_care(location_manager):
    """Show find care options"""
    st.subheader("🏥 Find Medical Care")
    
    # Care type selector
    care_type = st.radio(
        "What type of care do you need?",
        ["🚨 Emergency Care", "🏥 Hospital", "🏪 Urgent Care", "💊 Pharmacy", "👩‍⚕️ Doctor"]
    )
    
    if care_type == "🚨 Emergency Care":
        st.error("**For life-threatening emergencies, call 911 immediately!**")
        
        hospitals = location_manager.find_nearby_facilities("hospitals", max_distance=25)
        emergency_hospitals = [h for h in hospitals if h.get('emergency_room')]
        
        if emergency_hospitals:
            st.write("**Nearest Emergency Rooms:**")
            for hospital in emergency_hospitals[:3]:
                show_facility_card(hospital, location_manager, is_emergency=True)
        
    elif care_type == "🏥 Hospital":
        hospitals = location_manager.find_nearby_facilities("hospitals", max_distance=25)
        st.write(f"**Found {len(hospitals)} hospitals near you:**")
        for hospital in hospitals:
            show_facility_card(hospital, location_manager)
    
    elif care_type == "🏪 Urgent Care":
        urgent_care = location_manager.find_nearby_facilities("urgent_care", max_distance=15)
        st.write(f"**Found {len(urgent_care)} urgent care facilities near you:**")
        for clinic in urgent_care:
            show_facility_card(clinic, location_manager)
    
    elif care_type == "💊 Pharmacy":
        pharmacies = location_manager.find_nearby_facilities("pharmacies", max_distance=10)
        st.write(f"**Found {len(pharmacies)} pharmacies near you:**")
        for pharmacy in pharmacies:
            show_facility_card(pharmacy, location_manager)
    
    else:  # Doctor
        st.info("Doctor search would integrate with healthcare provider directories.")
        st.write("**Common ways to find a doctor:**")
        st.write("• Contact your insurance provider")
        st.write("• Use your health insurance website/app")
        st.write("• Ask for referrals from current doctors")
        st.write("• Check hospital physician directories")

def show_facility_card(facility, location_manager, is_emergency=False):
    """Show individual facility card"""
    with st.container():
        if is_emergency:
            st.error(f"🚨 **{facility['name']}** - {facility['distance']} miles")
        else:
            st.write(f"**{facility['name']}** - {facility['distance']} miles")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"📍 {facility['address']}")
            st.write(f"📞 {facility['phone']}")
            
            if facility.get('emergency_room'):
                st.success("✅ Emergency Room")
            if facility.get('trauma_center'):
                st.error("🚨 Trauma Center")
            if facility.get('wait_time'):
                st.info(f"⏱️ Wait Time: {facility['wait_time']}")
        
        with col2:
            directions_url = location_manager.get_directions_url(facility['address'])
            st.link_button("🗺️ Directions", directions_url)
        
        with col3:
            st.write(f"📞 {facility['phone']}")
        
        st.markdown("---")

def show_first_aid_guide(emergency_manager):
    """Show first aid guide"""
    st.subheader("🩹 First Aid Quick Reference")
    
    # Quick reference cards
    if st.session_state.get('quick_first_aid'):
        st.info("🆘 **Quick First Aid Reference** - Select a situation below:")
        del st.session_state.quick_first_aid
    
    # First aid categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💔 Heart Attack / Chest Pain"):
            show_first_aid_instructions("chest_pain", emergency_manager)
    
    with col2:
        if st.button("🫁 Difficulty Breathing"):
            show_first_aid_instructions("difficulty_breathing", emergency_manager)
    
    with col3:
        if st.button("🩸 Severe Bleeding"):
            show_first_aid_instructions("severe_bleeding", emergency_manager)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧠 Stroke Symptoms"):
            show_first_aid_instructions("stroke_symptoms", emergency_manager)
    
    with col2:
        if st.button("🤢 Allergic Reaction"):
            show_first_aid_instructions("allergic_reaction", emergency_manager)
    
    with col3:
        if st.button("🔥 Burns"):
            show_first_aid_instructions("severe_burn", emergency_manager)
    
    # CPR Instructions
    with st.expander("🫀 CPR Instructions"):
        st.write("**Adult CPR Steps:**")
        st.write("1. **Check responsiveness** - Tap shoulders, shout 'Are you okay?'")
        st.write("2. **Call 911** - Or have someone else call")
        st.write("3. **Position hands** - Center of chest, between nipples")
        st.write("4. **Push hard and fast** - At least 2 inches deep, 100-120 compressions per minute")
        st.write("5. **Allow complete chest recoil** between compressions")
        st.write("6. **Continue until help arrives** or person starts breathing")
        
        st.error("⚠️ **Only perform CPR if you are trained. Improper CPR can cause injury.**")

def show_first_aid_instructions(condition, emergency_manager):
    """Show specific first aid instructions"""
    instructions = emergency_manager.get_emergency_instructions(condition)
    
    st.subheader(f"🩹 First Aid: {condition.replace('_', ' ').title()}")
    
    for i, instruction in enumerate(instructions, 1):
        st.write(f"**{i}.** {instruction}")
    
    st.error("⚠️ **These are emergency first aid steps. Always call 911 for serious medical emergencies.**")

def show_emergency_contacts_tab(auth_manager, notification_manager):
    """Show emergency contacts management"""
    st.subheader("📞 Emergency Contacts")
    
    username = st.session_state.get('username')
    if not username:
        st.error("Please log in to manage emergency contacts.")
        return
    
    # Get current contacts
    contacts = auth_manager.get_emergency_contacts(username)
    
    if contacts:
        st.write("**Your Emergency Contacts:**")
        
        for i, contact in enumerate(contacts):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{contact['name']}** - {contact['relationship']}")
                    st.write(f"📞 {contact['phone']}")
                    if contact.get('email'):
                        st.write(f"📧 {contact['email']}")
                
                with col2:
                    if st.button(f"📞 Call", key=f"call_{i}"):
                        st.info(f"Calling {contact['name']} at {contact['phone']}")
                        # In real implementation, this would integrate with phone system
                
                with col3:
                    if st.button(f"📱 SMS", key=f"sms_{i}"):
                        send_emergency_sms(contact, notification_manager)
                
                st.markdown("---")
        
        # Quick notify all button
        if st.button("📢 NOTIFY ALL CONTACTS", type="primary"):
            message = f"Emergency Alert: {username} needs immediate assistance. This is an automated emergency notification from HealthAssist AI."
            results = notification_manager.send_emergency_alert(
                contacts, 
                "Emergency Alert", 
                {"address": "User location"}, 
                "high"
            )
            
            for result in results:
                if result['success']:
                    st.success(f"✅ Notified {result['contact']}")
                else:
                    st.error(f"❌ Failed to notify {result['contact']}")
    
    else:
        st.warning("⚠️ No emergency contacts configured!")
        st.write("Add emergency contacts in the Notifications page to enable emergency alerts.")

def send_emergency_sms(contact, notification_manager):
    """Send emergency SMS to specific contact"""
    message = f"🚨 EMERGENCY: This is an urgent message from HealthAssist AI. {st.session_state.get('username', 'User')} may need immediate assistance. Please respond or call them directly."
    
    success = notification_manager.send_sms(contact['phone'], message)
    
    if success:
        st.success(f"✅ Emergency SMS sent to {contact['name']}")
    else:
        st.error(f"❌ Failed to send SMS to {contact['name']}")

def show_nearest_hospital(location_manager):
    """Show nearest hospital information"""
    hospitals = location_manager.find_nearby_facilities("hospitals", max_distance=25)
    
    if hospitals:
        nearest = hospitals[0]
        st.success(f"🏥 **Nearest Hospital:** {nearest['name']}")
        st.write(f"📍 **Address:** {nearest['address']}")
        st.write(f"📞 **Phone:** {nearest['phone']}")
        st.write(f"📏 **Distance:** {nearest['distance']} miles")
        
        if nearest.get('emergency_room'):
            st.success("✅ Emergency Room Available")
        if nearest.get('trauma_center'):
            st.error("🚨 Trauma Center Available")
        
        directions_url = location_manager.get_directions_url(nearest['address'])
        st.link_button("🗺️ Get Directions", directions_url)
    else:
        st.error("Unable to find nearby hospitals. Call 911 for emergency assistance.")

def show_poison_control_info():
    """Show poison control information"""
    st.error("☠️ **POISON CONTROL EMERGENCY**")
    st.write("**Call Poison Control immediately:**")
    st.write("☎️ **1-800-222-1222** (24/7 hotline)")
    st.write("🌐 **Online:** poison.org")
    
    st.write("**For severe poisoning symptoms, also call 911:**")
    st.write("• Difficulty breathing")
    st.write("• Unconsciousness")
    st.write("• Severe vomiting")
    st.write("• Seizures")
    st.write("• Severe burns in mouth/throat")

def show_quick_emergency_contacts():
    """Show quick emergency contacts"""
    username = st.session_state.get('username')
    if username:
        auth_manager = AuthManager()
        contacts = auth_manager.get_emergency_contacts(username)
        
        if contacts:
            st.write("**Quick Contact Your Emergency Contacts:**")
            for contact in contacts:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{contact['name']}** - {contact['phone']}")
                with col2:
                    st.write(f"📞 {contact['phone']}")
        else:
            st.warning("No emergency contacts configured!")
    else:
        st.info("Log in to access your emergency contacts.")
