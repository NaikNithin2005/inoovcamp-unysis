from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow frontend to communicate with backend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow ALL origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserProfile(BaseModel):
    academics: str
    interests: list[str]
    strengths: list[str]
    budget: float

@app.get("/")
def read_root():
    return {"status": "Backend is running"}

import google.generativeai as genai
import json

# Configure Gemini
genai.configure(api_key="AIzaSyBKiC78EV2OGE_gVcr6pxvBMW6ZyX6jA9s")

# Debug: List available models
try:
    print("Available Models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

model = genai.GenerativeModel('gemini-2.5-flash')

@app.post("/generate-roadmap")
async def generate_career_path(user: UserProfile):
    print(f"Generating roadmap for: {user.academics}, Interests: {user.interests}")
    
    prompt = f"""
    Act as a Career Path Simulator. 
    User Profile:
    - Academics: {user.academics}
    - Interests: {', '.join(user.interests)}
    - Strengths: {', '.join(user.strengths)}
    - Budget: ${user.budget}

    Generate a personalized 4-year career roadmap.
    1. Roadmap: 4 milestones (one per year) with estimated cost.
    2. Success Probability: Based on alignment of strengths/academics with interests (0-100).
    3. Salary Projection: Projected salary for 4 years (growing).
    4. Skill Gap: 2-3 skills they need to learn based on interests but missing from strengths.

    Return ONLY raw JSON (no markdown formatting, no code blocks) in this structure:
    {{
        "roadmap": [
            {{"year": 1, "milestone": "string", "cost": number}},
            {{"year": 2, "milestone": "string", "cost": number}},
            {{"year": 3, "milestone": "string", "cost": number}},
            {{"year": 4, "milestone": "string", "cost": number}}
        ],
        "success_probability": number, 
        "salary_projection": [number, number, number, number], 
        "skill_gap": ["string", "string"] 
    }}
    """

    try:
        response = model.generate_content(prompt)
        # cleanup if model returns markdown ticks
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data
    except Exception as e:
        import traceback
        print(f"AI Error: {e}")
        print(traceback.format_exc()) # Print full stack trace
        # Fallback if AI fails
        return {
            "roadmap": [{"year": 1, "milestone": f"Error: {str(e)}", "cost": 0}],
            "success_probability": 0,
            "salary_projection": [0,0,0,0],
            "skill_gap": ["Error"]
        }

