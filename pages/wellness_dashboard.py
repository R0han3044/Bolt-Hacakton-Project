import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from utils.health_data import HealthDataManager

def show_wellness_dashboard():
    """Display wellness dashboard with health analytics"""
    st.title("📊 Wellness Dashboard")
    st.write("Track your health metrics and get personalized insights.")
    
    health_manager = HealthDataManager()
    username = st.session_state.get('username')
    
    if not username:
        st.error("Please log in to view your wellness dashboard.")
        return
    
    # Health Score Overview
    show_health_score_overview(health_manager, username)
    
    # Health Metrics
    show_health_metrics(health_manager, username)
    
    # Wellness Insights
    show_wellness_insights(health_manager, username)
    
    # Health Trends
    show_health_trends(health_manager, username)
    
    # Quick Actions
    show_quick_actions(health_manager, username)

def show_health_score_overview(health_manager, username):
    """Display overall health score"""
    st.subheader("🎯 Your Health Score")
    
    health_score = health_manager.calculate_health_score(username)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Health score gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = health_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Health Score"},
            delta = {'reference': 100},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': get_health_color(health_score)},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Current Score", f"{health_score}/100")
        
        if health_score >= 90:
            st.success("Excellent Health! 🌟")
        elif health_score >= 70:
            st.warning("Good Health ✅")
        else:
            st.error("Needs Attention ⚠️")
    
    with col3:
        # Health trend (simplified)
        trend = "↗️" if health_score > 75 else "↘️" if health_score < 60 else "➡️"
        st.metric("Trend", trend)
        
        last_checkup = "2 weeks ago"  # This would come from actual data
        st.metric("Last Checkup", last_checkup)

def get_health_color(score):
    """Get color based on health score"""
    if score >= 90:
        return "green"
    elif score >= 70:
        return "yellow"
    else:
        return "red"

def show_health_metrics(health_manager, username):
    """Display key health metrics"""
    st.subheader("📈 Key Health Metrics")
    
    # Get recent vital signs
    vital_signs = health_manager.get_vital_signs(username, days=7)
    
    if vital_signs:
        # Get latest vital signs
        latest = vital_signs[0]['data']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            bp_sys = latest.get('blood_pressure_systolic', 'N/A')
            bp_dia = latest.get('blood_pressure_diastolic', 'N/A')
            st.metric("Blood Pressure", f"{bp_sys}/{bp_dia}")
        
        with col2:
            heart_rate = latest.get('heart_rate', 'N/A')
            st.metric("Heart Rate", f"{heart_rate} bpm")
        
        with col3:
            temperature = latest.get('temperature', 'N/A')
            st.metric("Temperature", f"{temperature}°F")
        
        with col4:
            weight = latest.get('weight', 'N/A')
            st.metric("Weight", f"{weight} lbs")
    
    else:
        st.info("No recent vital signs recorded. Add some data to see your metrics!")
        
        # Quick data entry
        with st.expander("➕ Add Vital Signs"):
            with st.form("vital_signs_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    bp_sys = st.number_input("Systolic BP", min_value=70, max_value=200, value=120)
                    bp_dia = st.number_input("Diastolic BP", min_value=40, max_value=120, value=80)
                    heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=70)
                
                with col2:
                    temperature = st.number_input("Temperature (°F)", min_value=95.0, max_value=110.0, value=98.6)
                    weight = st.number_input("Weight (lbs)", min_value=50, max_value=500, value=150)
                
                if st.form_submit_button("Save Vital Signs"):
                    vital_data = {
                        "blood_pressure_systolic": bp_sys,
                        "blood_pressure_diastolic": bp_dia,
                        "heart_rate": heart_rate,
                        "temperature": temperature,
                        "weight": weight
                    }
                    
                    health_manager.add_health_record(username, "vital_signs", vital_data)
                    st.success("✅ Vital signs saved!")
                    st.rerun()

def show_wellness_insights(health_manager, username):
    """Display personalized wellness insights"""
    st.subheader("💡 Personalized Insights")
    
    insights = health_manager.generate_wellness_insights(username)
    
    if insights:
        for insight in insights:
            if insight['type'] == 'positive':
                st.success(f"**{insight['title']}**: {insight['message']}")
            elif insight['type'] == 'warning':
                st.warning(f"**{insight['title']}**: {insight['message']}")
            elif insight['type'] == 'danger':
                st.error(f"**{insight['title']}**: {insight['message']}")
            else:
                st.info(f"**{insight['title']}**: {insight['message']}")
    else:
        st.info("Add more health data to get personalized insights!")

def show_health_trends(health_manager, username):
    """Display health trends over time"""
    st.subheader("📉 Health Trends")
    
    vital_signs = health_manager.get_vital_signs(username, days=30)
    
    if len(vital_signs) >= 3:
        # Prepare data for plotting
        dates = []
        bp_sys = []
        bp_dia = []
        heart_rates = []
        
        for record in reversed(vital_signs):  # Reverse to get chronological order
            dates.append(datetime.fromisoformat(record['timestamp']).date())
            bp_sys.append(record['data'].get('blood_pressure_systolic', None))
            bp_dia.append(record['data'].get('blood_pressure_diastolic', None))
            heart_rates.append(record['data'].get('heart_rate', None))
        
        # Create DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Systolic BP': bp_sys,
            'Diastolic BP': bp_dia,
            'Heart Rate': heart_rates
        })
        
        # Plot trends
        tab1, tab2 = st.tabs(["Blood Pressure", "Heart Rate"])
        
        with tab1:
            fig = px.line(df, x='Date', y=['Systolic BP', 'Diastolic BP'], 
                         title="Blood Pressure Trends")
            fig.add_hline(y=140, line_dash="dash", line_color="red", 
                         annotation_text="High Systolic (140)")
            fig.add_hline(y=90, line_dash="dash", line_color="orange", 
                         annotation_text="High Diastolic (90)")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = px.line(df, x='Date', y='Heart Rate', 
                         title="Heart Rate Trends")
            fig.add_hline(y=100, line_dash="dash", line_color="red", 
                         annotation_text="High (100 bpm)")
            fig.add_hline(y=60, line_dash="dash", line_color="orange", 
                         annotation_text="Low (60 bpm)")
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("Record more vital signs over time to see trends!")

def show_quick_actions(health_manager, username):
    """Display quick action buttons"""
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Log Symptoms"):
            st.session_state.quick_action = "symptoms"
            st.rerun()
    
    with col2:
        if st.button("💊 Track Medication"):
            st.session_state.quick_action = "medication"
            st.rerun()
    
    with col3:
        if st.button("🏃 Log Exercise"):
            st.session_state.quick_action = "exercise"
            st.rerun()
    
    with col4:
        if st.button("🩺 Schedule Checkup"):
            st.session_state.quick_action = "checkup"
            st.rerun()
    
    # Handle quick actions
    if hasattr(st.session_state, 'quick_action'):
        handle_quick_action(st.session_state.quick_action, health_manager, username)

def handle_quick_action(action, health_manager, username):
    """Handle quick action selections"""
    
    if action == "symptoms":
        with st.form("quick_symptoms"):
            st.subheader("🤒 Quick Symptom Log")
            symptoms = st.text_area("Describe your symptoms:")
            severity = st.slider("Severity (1-10)", 1, 10, 5)
            
            if st.form_submit_button("Log Symptoms"):
                symptom_data = {
                    "symptoms": symptoms,
                    "severity": severity,
                    "quick_entry": True
                }
                health_manager.add_health_record(username, "symptoms", symptom_data)
                st.success("✅ Symptoms logged!")
                del st.session_state.quick_action
                st.rerun()
    
    elif action == "medication":
        with st.form("quick_medication"):
            st.subheader("💊 Medication Tracking")
            medication = st.text_input("Medication name:")
            dosage = st.text_input("Dosage:")
            time_taken = st.time_input("Time taken:")
            
            if st.form_submit_button("Log Medication"):
                med_data = {
                    "medication": medication,
                    "dosage": dosage,
                    "time_taken": str(time_taken),
                    "quick_entry": True
                }
                health_manager.add_health_record(username, "medication", med_data)
                st.success("✅ Medication logged!")
                del st.session_state.quick_action
                st.rerun()
    
    elif action == "exercise":
        with st.form("quick_exercise"):
            st.subheader("🏃 Exercise Log")
            exercise_type = st.selectbox("Type:", ["Walking", "Running", "Cycling", "Gym", "Swimming", "Other"])
            duration = st.number_input("Duration (minutes):", min_value=1, value=30)
            intensity = st.selectbox("Intensity:", ["Light", "Moderate", "Vigorous"])
            
            if st.form_submit_button("Log Exercise"):
                exercise_data = {
                    "type": exercise_type,
                    "duration": duration,
                    "intensity": intensity,
                    "quick_entry": True
                }
                health_manager.add_health_record(username, "exercise", exercise_data)
                st.success("✅ Exercise logged!")
                del st.session_state.quick_action
                st.rerun()
    
    elif action == "checkup":
        st.subheader("🩺 Schedule Checkup")
        st.info("This would integrate with a scheduling system to book appointments.")
        st.write("**Recommended checkup frequency:**")
        st.write("• Annual physical exam")
        st.write("• Dental cleaning every 6 months")
        st.write("• Eye exam every 1-2 years")
        st.write("• Preventive screenings as recommended by age")
        
        if st.button("Close"):
            del st.session_state.quick_action
            st.rerun()
