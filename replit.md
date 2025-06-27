# HealthAssist AI - Emergency Ready

## Overview

HealthAssist AI is a comprehensive healthcare assistant platform built with Streamlit, designed to provide AI-powered medical guidance, emergency response, and patient management capabilities. The application serves multiple user roles (admin, doctor, patient) with role-based access control and integrates various healthcare functionalities including symptom checking, wellness tracking, and emergency response systems.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with multi-page navigation
- **UI Design**: Wide layout with expandable sidebar and role-based interface
- **Visualization**: Plotly for health analytics and Folium for emergency mapping
- **Theme**: Custom healthcare-focused color scheme (red primary, white background)

### Backend Architecture
- **Language**: Python 3.11+
- **Data Storage**: JSON-based file system for user data, health records, and configurations
- **Authentication**: Custom hash-based authentication with role management
- **Session Management**: Streamlit session state for user persistence

### Data Storage Solutions
- **File Structure**: Organized JSON files in `/data` directory
  - `users.json`: User authentication and profile data
  - `patients.json`: Patient medical records
  - `health_records.json`: Health metrics and history
  - `medical_facilities.json`: Hospital and clinic information
  - `emergency_contacts.json`: Emergency contact management
  - `notifications.json`: System notifications and alerts

## Key Components

### Authentication System (`utils/auth_utils.py`)
- Hash-based password authentication using SHA-256
- Role-based access control (admin, doctor, patient)
- Default user creation with predefined credentials
- Session state management for user persistence

### Health Data Management (`utils/health_data.py`)
- Patient record management with CRUD operations
- Health metrics tracking and calculation
- JSON-based data persistence
- Health score calculation algorithms

### Emergency Response (`utils/emergency_utils.py`)
- Automated emergency detection based on symptom severity
- Emergency contact notification system
- Integration with location services for nearest hospitals
- Critical symptom keyword matching and scoring

### Location Services (`utils/location_utils.py`)
- Medical facility database management
- Geographic coordinate system for hospital locations
- Emergency service location lookup
- Map integration for visual hospital finder

### Notification System (`utils/notification_utils.py`)
- SMS integration via Twilio API
- Email notification capabilities
- Emergency alert broadcasting
- Notification history and management

### AI Integration (`utils/ai_models.py`)
- Hugging Face API integration for medical AI models
- Multiple specialized models: medical chat, Q&A, symptom classification
- Intelligent fallback system for offline functionality
- Enhanced symptom severity assessment using AI
- Configurable model selection and API management

### Page Components
- **Chat Interface**: AI-powered medical conversation system with Hugging Face models
- **Emergency Response**: Comprehensive emergency handling with maps
- **Symptom Checker**: Interactive symptom analysis tool with AI enhancement
- **Wellness Dashboard**: Health analytics and visualization
- **Patient Management**: Healthcare provider interface
- **Notifications**: Alert and reminder management

## Data Flow

1. **User Authentication**: Login → Role verification → Session establishment
2. **Health Data Input**: Symptom entry → Emergency assessment → AI analysis
3. **Emergency Detection**: Keyword matching → Severity scoring → Alert generation
4. **Location Services**: User location → Hospital lookup → Map visualization
5. **Notification Pipeline**: Event trigger → Contact retrieval → Message delivery

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework and UI components
- **Plotly**: Interactive data visualization and health charts
- **Folium**: Map visualization for emergency services
- **Pandas**: Data manipulation and health analytics
- **NumPy**: Numerical computations for health metrics

### Communication Services
- **Twilio**: SMS notification service for emergency alerts
- **SMTP**: Email delivery system for notifications
- **Hugging Face API**: AI model inference for medical assistance

### Development Tools
- **uv**: Dependency management and package resolution
- **Replit**: Cloud development and deployment platform

## Deployment Strategy

### Replit Cloud Deployment
- **Runtime**: Python 3.11 with Nix package management
- **Port Configuration**: Streamlit server on port 5000
- **Auto-scaling**: Configured for automatic scaling based on demand
- **Workflow**: Parallel execution with health monitoring

### Google Colab Alternative
- **Environment**: GPU-enabled runtime (T4 recommended)
- **Tunnel**: ngrok for public URL access
- **Model Integration**: Support for AI model deployment
- **Jupyter Notebook**: Complete deployment notebook provided

### Local Development
- **Dependencies**: uv lock file for consistent environments
- **Configuration**: Streamlit config with healthcare theme
- **Data Directory**: Automatic creation of data persistence layer

## Changelog
- June 27, 2025: Replaced IBM Granite model with Hugging Face AI models
  - Added modern AI integration through Hugging Face API
  - Implemented fallback responses for offline functionality
  - Enhanced symptom severity assessment with AI assistance
  - Updated UI to reflect new AI model system
- June 27, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.