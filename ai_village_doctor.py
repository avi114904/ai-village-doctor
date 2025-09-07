# ai_village_doctor_openai.py
import gradio as gr
import time
import random
import datetime
import json
import matplotlib.pyplot as plt
import io
import base64
import openai  # OpenAI library
from typing import List, Dict

# Initialize OpenAI (you'll need an API key)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI library not available. Using enhanced mock responses.")

class OpenAIDoctor:
    def __init__(self, use_openai=True):
        self.use_openai = use_openai and OPENAI_AVAILABLE
        self.community_data = {
            "consultations_provided": 0,
            "emergency_preventions": 0,
            "common_conditions": {}
        }
        
        if self.use_openai:
            # You'll need to set your OpenAI API key
            # openai.api_key = "your-api-key-here"  # Set this securely!
            print("OpenAI integration enabled")
        else:
            print("Using enhanced mock responses without OpenAI")
    
    def generate_response(self, prompt):
        self.community_data["consultations_provided"] += 1
        
        # Check for emergencies first
        emergency_keywords = ['chest pain', 'can\'t breathe', 'difficulty breathing', 'severe pain', 
                             'unconscious', 'heavy bleeding', 'heart attack', 'stroke', 'choking']
        prompt_lower = prompt.lower()
        
        if any(emergency in prompt_lower for emergency in emergency_keywords):
            self.community_data["emergency_preventions"] += 1
            return self.emergency_response(prompt)
        
        if self.use_openai:
            try:
                return self.openai_response(prompt)
            except Exception as e:
                print(f"OpenAI error: {e}")
                return self.mock_response(prompt)
        else:
            return self.mock_response(prompt)
    
    def openai_response(self, prompt):
        """Get response from OpenAI model"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if available
                messages=[
                    {"role": "system", "content": """You are an AI medical assistant for rural villages with limited healthcare access. 
                    Provide helpful, practical medical advice. Always include:
                    1. Potential causes in simple terms
                    2. Home care suggestions with available resources
                    3. Clear warning signs when to seek real medical help
                    4. Prevention tips
                    
                    Always clarify you're not a real doctor. Be empathetic and consider limited resources."""},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I apologize, I'm having trouble accessing my medical knowledge right now. Please try again or consult a healthcare professional. Error: {str(e)}"
    
    def emergency_response(self, prompt):
        return f"""🚨 **EMERGENCY ALERT** 🚨

Based on your description of '{prompt}', this may be a medical emergency.

**IMMEDIATE ACTION REQUIRED:**
• 📞 Call local emergency services NOW
• 🚑 Don't drive yourself to hospital
• 📋 Stay on the line with operator

**Emergency contacts:**
• National Emergency: 112 or 911
• Local hospital: [Nearest Healthcare Facility]
• Ambulance: 108 (in many regions)

⚠️ **CRITICAL LIMITATION:** I cannot handle emergencies. Please seek immediate human medical help."""

    def mock_response(self, prompt):
        """Enhanced mock responses when OpenAI isn't available"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['fever', 'temperature', 'hot']):
            return self.format_response(
                "Fever",
                "Infections, inflammation, or environmental factors",
                "• Rest and hydrate with water/electrolytes\n• Use damp cloth on forehead\n• Monitor temperature",
                "• Temperature above 103°F\n• Lasting more than 3 days\n• Difficulty breathing",
                "• Practice good hygiene\n• Wash hands regularly"
            )
        
        elif any(word in prompt_lower for word in ['headache', 'head', 'ache']):
            return self.format_response(
                "Headache",
                "Tension, dehydration, lack of sleep, or eye strain",
                "• Rest in quiet, dark room\n• Cool compress\n• Stay hydrated",
                "• Severe sudden headache\n• Head injury\n• Vision changes",
                "• Regular sleep patterns\n• Stress management"
            )
        
        # Add more conditions as needed...
        
        else:
            return """Thank you for describing your symptoms. 

I recommend monitoring your condition and consulting a healthcare professional for proper diagnosis. 

For immediate concerns, please contact local medical services."""

    def format_response(self, condition, causes, home_care, warnings, prevention):
        return f"""**{condition.upper()} GUIDANCE**

📋 **Possible Causes:** {causes}

🏠 **Home Care:** {home_care}

⚠️ **Seek Medical Help If:** {warnings}

🛡️ **Prevention:** {prevention}

---
🔬 **Remember:** I provide general information only. Always consult healthcare professionals for medical care."""

# Create doctor instance
doctor = OpenAIDoctor(use_openai=False)  # Set to True if you have OpenAI API key

# Create the interface
with gr.Blocks(title="AI Village Doctor with OpenAI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏥 AI Village Doctor Pro")
    gr.Markdown("### Enhanced with AI Medical Knowledge")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("#### 📋 Common Symptoms")
            gr.Examples(
                examples=[
                    ["I have fever and body aches"],
                    ["I have a severe headache"],
                    ["Persistent cough and congestion"],
                    ["Skin rash with itching"],
                    ["Stomach pain with diarrhea"]
                ],
                inputs=gr.Textbox(),
                label="Try these examples"
            )
            
            gr.Markdown("#### 📊 Statistics")
            stats = gr.Markdown("**Consultations:** 0\n**Emergencies Detected:** 0")
            
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="Medical Guidance Chat", 
                height=400,
                type="messages"
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Describe your symptoms", 
                    placeholder="Example: I've had fever for 2 days...",
                    lines=2
                )
            
            with gr.Row():
                submit_btn = gr.Button("Get Medical Guidance", variant="primary")
                clear = gr.Button("Clear Chat")
    
    def respond(message, chat_history):
        response = doctor.generate_response(message)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": response})
        
        # Update stats
        stats_text = f"**Consultations:** {doctor.community_data['consultations_provided']}\n"
        stats_text += f"**Emergencies Detected:** {doctor.community_data['emergency_preventions']}"
        
        return "", chat_history, stats_text

    def clear_chat():
        return [], "**Consultations:** 0\n**Emergencies Detected:** 0"

    msg.submit(respond, [msg, chatbot], [msg, chatbot, stats])
    submit_btn.click(respond, [msg, chatbot], [msg, chatbot, stats])
    clear.click(clear_chat, None, [chatbot, stats])

if __name__ == "__main__":
    print("Starting AI Village Doctor with OpenAI...")
    print("Open http://localhost:7860")
    
    if not OPENAI_AVAILABLE:
        print("Note: OpenAI library not installed. Using enhanced mock responses.")
        print("To use OpenAI: pip install openai")
    
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
