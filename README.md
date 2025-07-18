# Bolt Hackathon Project
# 🚨 EmergencyHelper – Bolt Hackathon Project

EmergencyHelper is a smart, AI-powered health and emergency assistance platform designed to help users during critical situations. Built with Streamlit and integrated health monitoring modules, it ensures emergency readiness, wellness tracking, and rapid response – all in one place.

## 🌟 Key Features

- 🩺 **Health Monitoring Dashboard**  
  Track vital signs and daily health parameters with an intuitive UI.

- ⚡ **Emergency Mode**  
  One-tap activation to notify emergency contacts and responders instantly.

- 🔐 **Role-Based Access**  
  Secure login for different users – Patient, Doctor, Admin, and Emergency Responder.

- 🧠 **AI Health Assistant**  
  Smart assistant to guide users through common health queries and first aid steps.

- 📅 **Reminders System**  
  Stay on top of medication, hydration, exercise, and routine checkups.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite / PostgreSQL (configurable)
- **Authentication**: Custom JWT-based auth system
- **Deployment**: GitHub + Streamlit Cloud / EC2

## 🚀 How to Run Locally

```bash
git clone https://github.com/R0han3044/Bolt-Hacakton-Project.git
cd Bolt-Hacakton-Project
pip install -r requirements.txt
streamlit run app.py

#📁 Project Structure
EmergencyHelper/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── pages/
├── utils/
│   ├── auth_utils.py
│   ├── db.py
│   └── health_data.py

#💡 Inspiration
This project was created for the Bolt Hackathon 2025 to build AI-driven emergency tech that saves lives and improves personal healthcare tracking.

#📜 License
This project is licensed under the MIT License. Feel free to use, modify, and share!