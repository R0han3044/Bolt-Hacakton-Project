"""
AI Model Integration for HealthAssist - Hugging Face Models
Supports multiple modern medical AI models for healthcare assistance
"""

import requests
import os
import json
from typing import Dict, List, Optional
import streamlit as st


class HuggingFaceModelManager:
    """Manages Hugging Face model integrations for healthcare AI"""
    
    def __init__(self):
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Available medical models
        self.models = {
            "medical_chat": {
                "name": "microsoft/DialoGPT-medium",
                "description": "Conversational AI for medical discussions",
                "endpoint": f"{self.base_url}/microsoft/DialoGPT-medium"
            },
            "medical_qa": {
                "name": "deepset/roberta-base-squad2",
                "description": "Medical question answering model",
                "endpoint": f"{self.base_url}/deepset/roberta-base-squad2"
            },
            "symptom_classifier": {
                "name": "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
                "description": "Medical text classification and analysis",
                "endpoint": f"{self.base_url}/microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
            },
            "general_chat": {
                "name": "microsoft/DialoGPT-large",
                "description": "General purpose conversational AI",
                "endpoint": f"{self.base_url}/microsoft/DialoGPT-large"
            }
        }
        
        self.fallback_responses = self._load_fallback_responses()
    
    def _load_fallback_responses(self) -> Dict:
        """Load fallback responses for when API is unavailable"""
        return {
            "emergency": {
                "chest_pain": "⚠️ **EMERGENCY**: Chest pain can be serious. Call 911 or go to the nearest emergency room immediately. Do not drive yourself.",
                "difficulty_breathing": "⚠️ **EMERGENCY**: Difficulty breathing requires immediate medical attention. Call 911 now.",
                "severe_bleeding": "⚠️ **EMERGENCY**: Apply pressure to the wound and call 911 immediately. Elevate the injured area if possible.",
                "unconscious": "⚠️ **EMERGENCY**: Check for breathing and pulse. Call 911 immediately. Begin CPR if trained.",
                "stroke_symptoms": "⚠️ **EMERGENCY**: Signs of stroke require immediate attention. Call 911 - time is critical for treatment."
            },
            "general_medical": [
                "I understand you have a health concern. For specific medical advice, please consult with a healthcare professional.",
                "Thank you for sharing your symptoms. While I can provide general information, please see a doctor for proper diagnosis.",
                "Your health is important. Please discuss these symptoms with your healthcare provider for personalized advice.",
                "I can offer general health information, but for your specific situation, professional medical consultation is recommended."
            ],
            "wellness": [
                "Maintaining good health involves regular exercise, balanced nutrition, adequate sleep, and stress management.",
                "Preventive care is key to good health. Regular checkups with your doctor can help catch issues early.",
                "A healthy lifestyle includes staying hydrated, eating nutritious foods, and getting 7-9 hours of sleep nightly.",
                "Mental health is as important as physical health. Don't hesitate to seek support when needed."
            ]
        }
    
    def is_available(self) -> bool:
        """Check if Hugging Face API is available"""
        try:
            # Test with a simple request
            response = requests.get(
                f"{self.base_url}/microsoft/DialoGPT-medium",
                headers={"Authorization": f"Bearer {self.api_token}"} if self.api_token else {},
                timeout=5
            )
            return response.status_code in [200, 503]  # 503 means model is loading
        except:
            return False
    
    def query_model(self, model_key: str, inputs: str, parameters: Optional[Dict] = None) -> Dict:
        """Query a specific Hugging Face model"""
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not available")
        
        model = self.models[model_key]
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        payload = {"inputs": inputs}
        if parameters:
            payload["parameters"] = parameters
        
        try:
            response = requests.post(
                model["endpoint"],
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 503:
                return {"success": False, "error": "Model is loading, please try again in a moment"}
            else:
                return {"success": False, "error": f"API Error: {response.status_code}"}
                
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def generate_medical_response(self, user_message: str, context: Optional[str] = None) -> str:
        """Generate medical response using available AI models"""
        
        # First try Hugging Face API
        if self.is_available():
            try:
                # Use medical chat model for conversational responses
                result = self.query_model(
                    "medical_chat", 
                    user_message,
                    {"max_length": 200, "temperature": 0.7}
                )
                
                if result["success"]:
                    response_data = result["data"]
                    if isinstance(response_data, list) and len(response_data) > 0:
                        generated_text = response_data[0].get("generated_text", "")
                        if generated_text:
                            return self._format_medical_response(generated_text)
                
            except Exception as e:
                st.warning(f"AI model temporarily unavailable: {str(e)}")
        
        # Fallback to rule-based responses
        return self._generate_fallback_response(user_message)
    
    def _format_medical_response(self, generated_text: str) -> str:
        """Format and validate AI-generated medical response"""
        # Clean up the response
        response = generated_text.strip()
        
        # Add medical disclaimer
        disclaimer = "\n\n**Important**: This is general information only. Please consult with a healthcare professional for personalized medical advice."
        
        # Ensure response is appropriate length
        if len(response) > 500:
            response = response[:497] + "..."
        
        return response + disclaimer
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate response using rule-based system when AI is unavailable"""
        message_lower = user_message.lower()
        
        # Check for emergency keywords
        emergency_keywords = {
            "chest pain": "chest_pain",
            "heart attack": "chest_pain",
            "can't breathe": "difficulty_breathing",
            "difficulty breathing": "difficulty_breathing",
            "bleeding": "severe_bleeding",
            "unconscious": "unconscious",
            "stroke": "stroke_symptoms",
            "seizure": "unconscious"
        }
        
        for keyword, emergency_type in emergency_keywords.items():
            if keyword in message_lower:
                return self.fallback_responses["emergency"][emergency_type]
        
        # Check for wellness topics
        wellness_keywords = ["wellness", "healthy", "tips", "lifestyle", "prevention"]
        if any(keyword in message_lower for keyword in wellness_keywords):
            import random
            return random.choice(self.fallback_responses["wellness"])
        
        # General medical response
        import random
        return random.choice(self.fallback_responses["general_medical"])
    
    def analyze_symptom_severity(self, symptoms: str) -> Dict:
        """Analyze symptom severity using AI models"""
        
        # Critical symptoms that always require emergency response
        critical_symptoms = [
            "chest pain", "heart attack", "can't breathe", "difficulty breathing",
            "severe bleeding", "unconscious", "stroke", "seizure", "overdose"
        ]
        
        symptoms_lower = symptoms.lower()
        
        # Check for critical symptoms
        for symptom in critical_symptoms:
            if symptom in symptoms_lower:
                return {
                    "severity": "critical",
                    "requires_emergency": True,
                    "confidence": 0.95,
                    "recommendation": "Seek immediate emergency medical attention"
                }
        
        # Use AI model for more nuanced analysis if available
        if self.is_available():
            try:
                # This would use a specialized medical classification model
                # For now, we'll use rule-based analysis
                pass
            except:
                pass
        
        # Moderate severity keywords
        moderate_keywords = [
            "severe pain", "high fever", "persistent vomiting", 
            "severe headache", "vision problems", "severe allergic"
        ]
        
        for keyword in moderate_keywords:
            if keyword in symptoms_lower:
                return {
                    "severity": "moderate",
                    "requires_emergency": False,
                    "confidence": 0.7,
                    "recommendation": "Consider urgent care or contact your doctor today"
                }
        
        # Default to mild severity
        return {
            "severity": "mild",
            "requires_emergency": False,
            "confidence": 0.6,
            "recommendation": "Monitor symptoms and consult healthcare provider if they worsen"
        }
    
    def get_model_status(self) -> Dict:
        """Get status of all available models"""
        status = {
            "api_available": self.is_available(),
            "api_token_configured": bool(self.api_token),
            "models": {}
        }
        
        for key, model in self.models.items():
            status["models"][key] = {
                "name": model["name"],
                "description": model["description"],
                "status": "available" if status["api_available"] else "fallback_mode"
            }
        
        return status


# Global model manager instance
model_manager = HuggingFaceModelManager()