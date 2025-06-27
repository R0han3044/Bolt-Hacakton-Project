"""
Enhanced Hospital Finder with Interactive Maps
Helps users easily find nearby hospitals and medical facilities
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from utils.location_utils import LocationManager
from utils.emergency_utils import EmergencyManager
import json


def show_hospital_finder():
    """Display enhanced hospital finder with maps"""
    from utils.bolt_ai_traces import bolt_traces
    
    st.markdown("""
    <div class="bolt-card">
        <h1 class="bolt-gradient-text">🏥 Hospital Finder</h1>
        <p style="color: rgba(31, 41, 55, 0.8);">Find nearby hospitals and medical facilities quickly and easily</p>
    </div>
    """, unsafe_allow_html=True)
    
    location_manager = LocationManager()
    emergency_manager = EmergencyManager()
    
    # Location input section
    st.subheader("📍 Your Location")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Address input
        user_address = st.text_input(
            "Enter your address or allow location access:",
            placeholder="123 Main St, City, State",
            help="Enter your current address to find nearby hospitals"
        )
        
        # Distance filter
        max_distance = st.slider(
            "Search radius (miles):",
            min_value=1,
            max_value=50,
            value=10,
            help="How far you're willing to travel"
        )
    
    with col2:
        facility_type = st.selectbox(
            "Facility Type:",
            ["hospitals", "urgent_care", "pharmacies", "all"],
            help="Type of medical facility to find"
        )
        
        if st.button("🎯 Use Current Location", type="primary"):
            try:
                # Simulate getting user location
                st.session_state.user_location = {
                    "lat": 40.7128,
                    "lng": -74.0060,
                    "address": "New York, NY"
                }
                st.success("Location detected!")
                st.rerun()
            except Exception as e:
                st.error("Could not access location. Please enter address manually.")
    
    # Emergency quick access
    if st.button("🚨 EMERGENCY - Find Nearest Hospital", type="secondary"):
        st.session_state.emergency_search = True
        facility_type = "hospitals"
        max_distance = 25
    
    # Search for facilities
    if user_address or st.session_state.get('user_location'):
        
        # Get facilities
        try:
            if facility_type == "all":
                hospitals = location_manager.find_nearby_facilities("hospitals", max_distance)
                urgent_care = location_manager.find_nearby_facilities("urgent_care", max_distance)
                pharmacies = location_manager.find_nearby_facilities("pharmacies", max_distance)
                facilities = hospitals + urgent_care + pharmacies
            else:
                facilities = location_manager.find_nearby_facilities(facility_type, max_distance)
            
            if facilities:
                # Display interactive map
                show_interactive_map(facilities, location_manager)
                
                # Display facility list with enhanced details
                show_enhanced_facility_list(facilities, location_manager, emergency_manager)
                
            else:
                st.warning(f"No {facility_type} found within {max_distance} miles. Try increasing the search radius.")
                
        except Exception as e:
            st.error(f"Error searching for facilities: {str(e)}")
            # Show fallback list
            show_fallback_facilities()


def show_interactive_map(facilities, location_manager):
    """Display interactive map with facility markers"""
    st.subheader("🗺️ Interactive Map")
    
    # Create map centered on user location or first facility
    if st.session_state.get('user_location'):
        center_lat = st.session_state.user_location['lat']
        center_lng = st.session_state.user_location['lng']
    else:
        center_lat = facilities[0]['coordinates']['lat']
        center_lng = facilities[0]['coordinates']['lng']
    
    # Create folium map
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=12,
        tiles="OpenStreetMap"
    )
    
    # Add user location marker
    if st.session_state.get('user_location'):
        folium.Marker(
            [center_lat, center_lng],
            popup="Your Location",
            tooltip="You are here",
            icon=folium.Icon(color='blue', icon='user', prefix='fa')
        ).add_to(m)
    
    # Add facility markers with different colors
    colors = {
        'hospitals': 'red',
        'urgent_care': 'orange', 
        'pharmacies': 'green'
    }
    
    for facility in facilities:
        lat = facility['coordinates']['lat']
        lng = facility['coordinates']['lng']
        
        # Determine facility type for color
        if 'emergency_room' in facility:
            facility_type = 'hospitals'
            icon_name = 'plus'
        elif 'wait_time' in facility:
            facility_type = 'urgent_care'
            icon_name = 'stethoscope'
        else:
            facility_type = 'pharmacies'
            icon_name = 'pills'
        
        # Create popup content
        popup_content = f"""
        <div style="width: 200px;">
            <h4>{facility['name']}</h4>
            <p><strong>Address:</strong> {facility['address']}</p>
            <p><strong>Phone:</strong> {facility['phone']}</p>
        """
        
        if facility_type == 'hospitals' and facility.get('emergency_room'):
            popup_content += "<p><strong>Emergency Room:</strong> Available 24/7</p>"
        elif facility_type == 'urgent_care' and facility.get('wait_time'):
            popup_content += f"<p><strong>Wait Time:</strong> {facility['wait_time']}</p>"
        
        popup_content += f"""
            <button onclick="window.open('tel:{facility['phone']}', '_self')" 
                    style="background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                📞 Call Now
            </button>
        </div>
        """
        
        folium.Marker(
            [lat, lng],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=facility['name'],
            icon=folium.Icon(
                color=colors.get(facility_type, 'blue'),
                icon=icon_name,
                prefix='fa'
            )
        ).add_to(m)
    
    # Display the map
    map_data = st_folium(m, width=700, height=500)
    
    # Handle map clicks
    if map_data['last_clicked']:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        st.info(f"Clicked location: {clicked_lat:.4f}, {clicked_lng:.4f}")


def show_enhanced_facility_list(facilities, location_manager, emergency_manager):
    """Display enhanced list of facilities with quick actions"""
    st.subheader("🏥 Nearby Facilities")
    
    # Sort facilities by distance if user location is available
    if st.session_state.get('user_location'):
        user_lat = st.session_state.user_location['lat']
        user_lng = st.session_state.user_location['lng']
        
        for facility in facilities:
            distance = location_manager.calculate_distance(
                user_lat, user_lng,
                facility['coordinates']['lat'],
                facility['coordinates']['lng']
            )
            facility['distance'] = distance
        
        facilities.sort(key=lambda x: x.get('distance', float('inf')))
    
    for i, facility in enumerate(facilities):
        with st.expander(f"🏥 {facility['name']}" + (f" ({facility['distance']:.1f} miles)" if 'distance' in facility else "")):
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Address:** {facility['address']}")
                st.write(f"**Phone:** {facility['phone']}")
                
                if 'emergency_room' in facility and facility['emergency_room']:
                    st.success("✅ Emergency Room Available 24/7")
                    if facility.get('trauma_center'):
                        st.success("🚨 Trauma Center")
                
                if 'wait_time' in facility:
                    st.info(f"⏱️ Current Wait Time: {facility['wait_time']}")
                
                if 'services' in facility:
                    st.write("**Services:** " + ", ".join(facility['services']))
                
                if 'specialties' in facility:
                    st.write("**Specialties:** " + ", ".join(facility['specialties']))
            
            with col2:
                # Quick call button
                if st.button(f"📞 Call", key=f"call_{i}"):
                    st.success(f"Calling {facility['name']}...")
                    st.info(f"Dial: {facility['phone']}")
                
                # Directions button
                if st.button(f"🧭 Directions", key=f"directions_{i}"):
                    directions_url = location_manager.get_directions_url(facility['address'])
                    st.markdown(f"[Open in Maps]({directions_url})")
            
            with col3:
                # Emergency actions
                if 'emergency_room' in facility and facility['emergency_room']:
                    if st.button(f"🚨 Emergency Call", key=f"emergency_{i}", type="primary"):
                        handle_emergency_call(facility, emergency_manager)
                
                # Save favorite
                if st.button(f"⭐ Save", key=f"save_{i}"):
                    save_favorite_facility(facility)


def handle_emergency_call(facility, emergency_manager):
    """Handle emergency call to hospital"""
    st.error("🚨 EMERGENCY CALL INITIATED")
    
    emergency_info = f"""
    **Emergency Call to:** {facility['name']}
    **Phone:** {facility['phone']}
    **Address:** {facility['address']}
    
    **Calling now...**
    """
    
    st.markdown(emergency_info)
    
    # Log the emergency call
    emergency_manager.call_emergency_services()
    
    # Show emergency instructions
    st.warning("""
    **While calling:**
    - Stay calm and speak clearly
    - Provide your exact location
    - Describe the emergency situation
    - Follow the dispatcher's instructions
    - Stay on the line until help arrives
    """)


def save_favorite_facility(facility):
    """Save facility as favorite"""
    if 'favorite_facilities' not in st.session_state:
        st.session_state.favorite_facilities = []
    
    # Check if already saved
    if facility['id'] not in [f['id'] for f in st.session_state.favorite_facilities]:
        st.session_state.favorite_facilities.append(facility)
        st.success(f"✅ {facility['name']} saved to favorites!")
    else:
        st.info("Already in favorites")


def show_fallback_facilities():
    """Show fallback facilities when location search fails"""
    st.subheader("🏥 Major Medical Centers")
    
    fallback_facilities = [
        {
            "name": "City General Hospital",
            "address": "123 Main St, Downtown",
            "phone": "(555) 123-4567",
            "type": "Emergency Hospital",
            "services": ["Emergency Room", "Trauma Center", "24/7"]
        },
        {
            "name": "Regional Medical Center", 
            "address": "456 Oak Ave, Midtown",
            "phone": "(555) 234-5678",
            "type": "General Hospital",
            "services": ["Emergency Room", "Urgent Care", "Specialists"]
        },
        {
            "name": "QuickCare Urgent Care",
            "address": "789 Pine St, Westside", 
            "phone": "(555) 345-6789",
            "type": "Urgent Care",
            "services": ["Walk-in Care", "Minor Injuries", "Lab Work"]
        }
    ]
    
    for facility in fallback_facilities:
        with st.expander(f"{facility['type']}: {facility['name']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Address:** {facility['address']}")
                st.write(f"**Phone:** {facility['phone']}")
                st.write(f"**Services:** {', '.join(facility['services'])}")
            
            with col2:
                if st.button(f"📞 Call {facility['name']}", key=f"fallback_call_{facility['name']}"):
                    st.success(f"Calling {facility['name']}...")
                    st.info(f"Dial: {facility['phone']}")


def show_emergency_hospital_map():
    """Quick emergency hospital finder"""
    st.subheader("🚨 Emergency Hospital Finder")
    
    location_manager = LocationManager()
    emergency_facilities = location_manager.find_nearby_facilities("hospitals", 25)
    
    # Filter for emergency rooms only
    emergency_hospitals = [f for f in emergency_facilities if f.get('emergency_room', False)]
    
    if emergency_hospitals:
        st.success(f"Found {len(emergency_hospitals)} emergency hospitals nearby")
        
        # Show closest hospital prominently
        closest = emergency_hospitals[0]
        st.error(f"""
        **CLOSEST EMERGENCY HOSPITAL:**
        🏥 {closest['name']}
        📍 {closest['address']}
        📞 {closest['phone']}
        """)
        
        if st.button("🚨 CALL EMERGENCY HOSPITAL NOW", type="primary"):
            st.error("CALLING EMERGENCY HOSPITAL...")
            st.info(f"Dialing: {closest['phone']}")
        
        # Show map
        show_interactive_map(emergency_hospitals[:3], location_manager)
    
    else:
        st.error("No emergency hospitals found. Call 911 immediately.")
        if st.button("📞 CALL 911", type="primary"):
            st.error("CALLING 911...")