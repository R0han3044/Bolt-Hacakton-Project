import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.health_data import HealthDataManager
from utils.auth_utils import AuthManager

def show_patient_management():
    """Display patient management interface for doctors and admins"""
    st.title("👥 Patient Management")
    st.write("Manage patient records, view health data, and track patient progress.")
    
    # Check user permissions
    if st.session_state.user_role not in ['admin', 'doctor']:
        st.error("Access denied. This section is for healthcare providers only.")
        return
    
    health_manager = HealthDataManager()
    auth_manager = AuthManager()
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Patient List", "👤 Patient Details", "➕ Add Patient", "📊 Analytics"])
    
    with tab1:
        show_patient_list(health_manager)
    
    with tab2:
        show_patient_details(health_manager)
    
    with tab3:
        show_add_patient(health_manager)
    
    with tab4:
        show_patient_analytics(health_manager)

def show_patient_list(health_manager):
    """Display list of all patients"""
    st.subheader("📋 Patient Directory")
    
    patients = health_manager.get_all_patients()
    
    if patients:
        # Create patient DataFrame
        patient_data = []
        for patient_id, patient_info in patients.items():
            last_visit = get_last_visit(health_manager, patient_id)
            health_score = health_manager.calculate_health_score(patient_id)
            
            patient_data.append({
                "ID": patient_id,
                "Name": f"{patient_info.get('first_name', '')} {patient_info.get('last_name', '')}",
                "Age": patient_info.get('age', 'N/A'),
                "Gender": patient_info.get('gender', 'N/A'),
                "Last Visit": last_visit,
                "Health Score": f"{health_score}/100",
                "Status": get_patient_status(health_score)
            })
        
        df = pd.DataFrame(patient_data)
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search patients by name or ID:")
        with col2:
            status_filter = st.selectbox("Filter by status:", ["All", "Excellent", "Good", "Needs Attention"])
        
        # Apply filters
        if search_term:
            df = df[df['Name'].str.contains(search_term, case=False, na=False) | 
                   df['ID'].str.contains(search_term, case=False, na=False)]
        
        if status_filter != "All":
            df = df[df['Status'] == status_filter]
        
        # Display patient table
        if not df.empty:
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "Health Score": st.column_config.ProgressColumn(
                        "Health Score",
                        help="Overall health score",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
            
            # Patient selection for details
            selected_patient = st.selectbox(
                "Select patient for details:",
                options=[""] + df['ID'].tolist(),
                format_func=lambda x: f"{x} - {df[df['ID']==x]['Name'].iloc[0]}" if x and x in df['ID'].values else "Select a patient..."
            )
            
            if selected_patient:
                st.session_state.selected_patient_id = selected_patient
        else:
            st.info("No patients found matching your criteria.")
    
    else:
        st.info("No patients registered yet.")

def show_patient_details(health_manager):
    """Display detailed patient information"""
    st.subheader("👤 Patient Details")
    
    selected_patient_id = st.session_state.get('selected_patient_id')
    
    if not selected_patient_id:
        st.info("Select a patient from the Patient List tab to view details.")
        return
    
    patient = health_manager.get_patient(selected_patient_id)
    
    if not patient:
        st.error("Patient not found.")
        return
    
    # Patient basic info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Name:** {patient.get('first_name', '')} {patient.get('last_name', '')}")
        st.write(f"**Patient ID:** {selected_patient_id}")
        st.write(f"**Age:** {patient.get('age', 'N/A')}")
        st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
        st.write(f"**Phone:** {patient.get('phone', 'N/A')}")
        st.write(f"**Email:** {patient.get('email', 'N/A')}")
    
    with col2:
        health_score = health_manager.calculate_health_score(selected_patient_id)
        st.metric("Health Score", f"{health_score}/100")
        status = get_patient_status(health_score)
        
        if status == "Excellent":
            st.success(f"Status: {status}")
        elif status == "Good":
            st.warning(f"Status: {status}")
        else:
            st.error(f"Status: {status}")
    
    # Medical history tabs
    hist_tab1, hist_tab2, hist_tab3, hist_tab4 = st.tabs(["🩺 Vital Signs", "🤒 Symptoms", "💊 Medications", "📋 All Records"])
    
    with hist_tab1:
        show_patient_vitals(health_manager, selected_patient_id)
    
    with hist_tab2:
        show_patient_symptoms(health_manager, selected_patient_id)
    
    with hist_tab3:
        show_patient_medications(health_manager, selected_patient_id)
    
    with hist_tab4:
        show_all_patient_records(health_manager, selected_patient_id)

def show_patient_vitals(health_manager, patient_id):
    """Show patient vital signs history"""
    st.write("**Recent Vital Signs**")
    
    vitals = health_manager.get_vital_signs(patient_id, days=30)
    
    if vitals:
        vital_data = []
        for record in vitals:
            data = record['data']
            vital_data.append({
                "Date": datetime.fromisoformat(record['timestamp']).strftime("%Y-%m-%d %H:%M"),
                "BP (sys/dia)": f"{data.get('blood_pressure_systolic', 'N/A')}/{data.get('blood_pressure_diastolic', 'N/A')}",
                "Heart Rate": f"{data.get('heart_rate', 'N/A')} bpm",
                "Temperature": f"{data.get('temperature', 'N/A')}°F",
                "Weight": f"{data.get('weight', 'N/A')} lbs"
            })
        
        df = pd.DataFrame(vital_data)
        st.dataframe(df, use_container_width=True)
        
        # Alert for concerning vitals
        latest = vitals[0]['data']
        alerts = []
        
        if latest.get('blood_pressure_systolic', 0) > 140:
            alerts.append("⚠️ High systolic blood pressure")
        if latest.get('heart_rate', 0) > 100:
            alerts.append("⚠️ Elevated heart rate")
        if latest.get('temperature', 0) > 100.4:
            alerts.append("⚠️ Fever detected")
        
        if alerts:
            st.error("**Alerts:**")
            for alert in alerts:
                st.write(alert)
    
    else:
        st.info("No vital signs recorded for this patient.")

def show_patient_symptoms(health_manager, patient_id):
    """Show patient symptoms history"""
    st.write("**Recent Symptoms**")
    
    symptoms = health_manager.get_symptoms_history(patient_id, days=30)
    
    if symptoms:
        for symptom in symptoms:
            with st.expander(f"Symptoms - {datetime.fromisoformat(symptom['timestamp']).strftime('%Y-%m-%d %H:%M')}"):
                data = symptom['data']
                st.write(f"**Description:** {data.get('symptoms', 'N/A')}")
                
                if 'severity' in data:
                    st.write(f"**Severity:** {data['severity']}/10")
                
                if data.get('is_emergency'):
                    st.error("🚨 Emergency-level symptoms detected")
                
                if 'recommendation' in data:
                    rec = data['recommendation']
                    st.write(f"**Recommendation:** {rec.get('action', 'N/A')}")
    
    else:
        st.info("No symptoms recorded for this patient.")

def show_patient_medications(health_manager, patient_id):
    """Show patient medication history"""
    st.write("**Medication Records**")
    
    medications = health_manager.get_health_records(patient_id, "medication", limit=20)
    
    if medications:
        med_data = []
        for record in medications:
            data = record['data']
            med_data.append({
                "Date": datetime.fromisoformat(record['timestamp']).strftime("%Y-%m-%d"),
                "Medication": data.get('medication', 'N/A'),
                "Dosage": data.get('dosage', 'N/A'),
                "Time": data.get('time_taken', 'N/A')
            })
        
        df = pd.DataFrame(med_data)
        st.dataframe(df, use_container_width=True)
    
    else:
        st.info("No medication records for this patient.")

def show_all_patient_records(health_manager, patient_id):
    """Show all patient records"""
    st.write("**Complete Medical Records**")
    
    all_records = health_manager.get_health_records(patient_id, limit=50)
    
    if all_records:
        for record in all_records:
            with st.expander(f"{record['type'].title()} - {datetime.fromisoformat(record['timestamp']).strftime('%Y-%m-%d %H:%M')}"):
                st.json(record['data'])
    
    else:
        st.info("No medical records found for this patient.")

def show_add_patient(health_manager):
    """Form to add new patient"""
    st.subheader("➕ Add New Patient")
    
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name*", max_chars=50)
            last_name = st.text_input("Last Name*", max_chars=50)
            age = st.number_input("Age", min_value=0, max_value=150, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
        
        with col2:
            phone = st.text_input("Phone Number")
            email = st.text_input("Email Address")
            emergency_contact = st.text_input("Emergency Contact Name")
            emergency_phone = st.text_input("Emergency Contact Phone")
        
        # Medical information
        st.subheader("Medical Information")
        medical_conditions = st.text_area("Known Medical Conditions", height=100)
        allergies = st.text_area("Allergies", height=100)
        medications = st.text_area("Current Medications", height=100)
        
        submitted = st.form_submit_button("Add Patient", type="primary")
        
        if submitted:
            if not first_name or not last_name:
                st.error("First name and last name are required.")
            else:
                # Generate patient ID
                patient_id = f"PAT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                patient_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "age": age,
                    "gender": gender,
                    "phone": phone,
                    "email": email,
                    "emergency_contact": emergency_contact,
                    "emergency_phone": emergency_phone,
                    "medical_conditions": medical_conditions,
                    "allergies": allergies,
                    "current_medications": medications
                }
                
                health_manager.add_patient(patient_id, patient_data)
                st.success(f"✅ Patient added successfully! Patient ID: {patient_id}")

def show_patient_analytics(health_manager):
    """Show patient analytics and statistics"""
    st.subheader("📊 Patient Analytics")
    
    patients = health_manager.get_all_patients()
    
    if not patients:
        st.info("No patients to analyze.")
        return
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", len(patients))
    
    with col2:
        # Calculate average health score
        health_scores = [health_manager.calculate_health_score(pid) for pid in patients.keys()]
        avg_score = sum(health_scores) / len(health_scores) if health_scores else 0
        st.metric("Avg Health Score", f"{avg_score:.1f}/100")
    
    with col3:
        # Count patients needing attention
        needs_attention = sum(1 for score in health_scores if score < 70)
        st.metric("Needs Attention", needs_attention)
    
    with col4:
        # Count high-risk patients
        high_risk = sum(1 for score in health_scores if score < 50)
        st.metric("High Risk", high_risk)
    
    # Demographics
    st.subheader("Demographics")
    
    # Age distribution
    ages = [p.get('age', 0) for p in patients.values() if isinstance(p.get('age'), int)]
    if ages:
        import plotly.express as px
        
        age_groups = []
        for age in ages:
            if age < 18:
                age_groups.append("Under 18")
            elif age < 30:
                age_groups.append("18-29")
            elif age < 50:
                age_groups.append("30-49")
            elif age < 65:
                age_groups.append("50-64")
            else:
                age_groups.append("65+")
        
        age_df = pd.DataFrame({"Age Group": age_groups})
        age_counts = age_df["Age Group"].value_counts()
        
        fig = px.pie(values=age_counts.values, names=age_counts.index, title="Age Distribution")
        st.plotly_chart(fig, use_container_width=True)

def get_last_visit(health_manager, patient_id):
    """Get last visit date for patient"""
    records = health_manager.get_health_records(patient_id, limit=1)
    if records:
        return datetime.fromisoformat(records[0]['timestamp']).strftime("%Y-%m-%d")
    return "Never"

def get_patient_status(health_score):
    """Get patient status based on health score"""
    if health_score >= 90:
        return "Excellent"
    elif health_score >= 70:
        return "Good"
    else:
        return "Needs Attention"
