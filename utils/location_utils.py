import json
import os
import requests
from datetime import datetime
import streamlit as st

class LocationManager:
    def __init__(self):
        self.medical_facilities_file = "data/medical_facilities.json"
        self.ensure_data_directory()
        self.load_medical_facilities()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_medical_facilities(self):
        """Load medical facilities data"""
        try:
            with open(self.medical_facilities_file, 'r') as f:
                self.medical_facilities = json.load(f)
        except FileNotFoundError:
            # Default medical facilities data
            self.medical_facilities = {
                "hospitals": [
                    {
                        "id": "hosp_001",
                        "name": "City General Hospital",
                        "address": "123 Main St, Downtown",
                        "phone": "+1-555-0123",
                        "coordinates": {"lat": 40.7128, "lng": -74.0060},
                        "emergency_room": True,
                        "trauma_center": True,
                        "specialties": ["Emergency Medicine", "Cardiology", "Neurology"],
                        "rating": 4.5
                    },
                    {
                        "id": "hosp_002",
                        "name": "Regional Medical Center",
                        "address": "456 Oak Ave, Midtown",
                        "phone": "+1-555-0456",
                        "coordinates": {"lat": 40.7580, "lng": -73.9855},
                        "emergency_room": True,
                        "trauma_center": False,
                        "specialties": ["Emergency Medicine", "Orthopedics", "Pediatrics"],
                        "rating": 4.2
                    },
                    {
                        "id": "hosp_003",
                        "name": "University Hospital",
                        "address": "789 College Blvd, University District",
                        "phone": "+1-555-0789",
                        "coordinates": {"lat": 40.6892, "lng": -74.0445},
                        "emergency_room": True,
                        "trauma_center": True,
                        "specialties": ["Emergency Medicine", "Surgery", "Oncology"],
                        "rating": 4.7
                    }
                ],
                "pharmacies": [
                    {
                        "id": "pharm_001",
                        "name": "Downtown Pharmacy",
                        "address": "100 Main St, Downtown",
                        "phone": "+1-555-1000",
                        "coordinates": {"lat": 40.7138, "lng": -74.0070},
                        "hours": "24/7",
                        "services": ["Prescription", "Over-the-counter", "Vaccinations"]
                    },
                    {
                        "id": "pharm_002",
                        "name": "MediMart Express",
                        "address": "500 Oak Ave, Midtown",
                        "phone": "+1-555-1001",
                        "coordinates": {"lat": 40.7590, "lng": -73.9865},
                        "hours": "6 AM - 12 AM",
                        "services": ["Prescription", "Over-the-counter", "Health screenings"]
                    }
                ],
                "urgent_care": [
                    {
                        "id": "urgent_001",
                        "name": "QuickCare Clinic",
                        "address": "200 Pine St, Westside",
                        "phone": "+1-555-2000",
                        "coordinates": {"lat": 40.7200, "lng": -74.0100},
                        "hours": "8 AM - 10 PM",
                        "wait_time": "15 minutes",
                        "services": ["Minor injuries", "Illness", "X-rays"]
                    }
                ]
            }
            self.save_medical_facilities()
    
    def save_medical_facilities(self):
        """Save medical facilities to JSON file"""
        with open(self.medical_facilities_file, 'w') as f:
            json.dump(self.medical_facilities, f, indent=2)
    
    def get_current_location(self):
        """Get current user location"""
        # In a real application, this would use actual geolocation
        # For now, return a mock location or use session state
        
        if 'user_location' in st.session_state and st.session_state.user_location:
            return st.session_state.user_location
        
        # Mock location for demo purposes
        mock_location = {
            "lat": 40.7128,
            "lng": -74.0060,
            "address": "Downtown Area, New York, NY",
            "accuracy": "approximate",
            "timestamp": datetime.now().isoformat()
        }
        
        st.session_state.user_location = mock_location
        return mock_location
    
    def set_user_location(self, latitude, longitude):
        """Set user location coordinates"""
        location = {
            "lat": latitude,
            "lng": longitude,
            "timestamp": datetime.now().isoformat()
        }
        
        # Try to get address from coordinates
        address = self.reverse_geocode(latitude, longitude)
        if address:
            location["address"] = address
        
        st.session_state.user_location = location
        return location
    
    def reverse_geocode(self, lat, lng):
        """Convert coordinates to address"""
        # This would use a real geocoding service in production
        # For demo, return a mock address
        return f"Location near {lat:.4f}, {lng:.4f}"
    
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two points using Haversine formula"""
        import math
        
        R = 3959  # Earth's radius in miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def find_nearby_facilities(self, facility_type="hospitals", max_distance=10):
        """Find nearby medical facilities"""
        user_location = self.get_current_location()
        if not user_location:
            return []
        
        user_lat = user_location["lat"]
        user_lng = user_location["lng"]
        
        facilities = self.medical_facilities.get(facility_type, [])
        nearby_facilities = []
        
        for facility in facilities:
            facility_lat = facility["coordinates"]["lat"]
            facility_lng = facility["coordinates"]["lng"]
            
            distance = self.calculate_distance(user_lat, user_lng, facility_lat, facility_lng)
            
            if distance <= max_distance:
                facility_with_distance = facility.copy()
                facility_with_distance["distance"] = round(distance, 1)
                nearby_facilities.append(facility_with_distance)
        
        # Sort by distance
        nearby_facilities.sort(key=lambda x: x["distance"])
        
        return nearby_facilities
    
    def get_directions_url(self, destination_address):
        """Get Google Maps directions URL"""
        user_location = self.get_current_location()
        
        if user_location and "address" in user_location:
            origin = user_location["address"]
        else:
            origin = "Current Location"
        
        # Create Google Maps URL
        base_url = "https://www.google.com/maps/dir/"
        directions_url = f"{base_url}{origin}/{destination_address}"
        
        return directions_url
    
    def create_facility_map_data(self, facilities):
        """Create map data for facilities"""
        map_data = []
        
        user_location = self.get_current_location()
        if user_location:
            map_data.append({
                "lat": user_location["lat"],
                "lng": user_location["lng"],
                "type": "user",
                "name": "Your Location",
                "icon": "🏠",
                "color": "blue"
            })
        
        for facility in facilities:
            facility_type = "hospital" if facility.get("emergency_room") else "clinic"
            icon = "🏥" if facility_type == "hospital" else "🏪"
            color = "red" if facility.get("trauma_center") else "orange"
            
            map_data.append({
                "lat": facility["coordinates"]["lat"],
                "lng": facility["coordinates"]["lng"],
                "type": facility_type,
                "name": facility["name"],
                "address": facility["address"],
                "phone": facility["phone"],
                "distance": facility.get("distance", "N/A"),
                "icon": icon,
                "color": color
            })
        
        return map_data
