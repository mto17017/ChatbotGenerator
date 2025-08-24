import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # This should be the URL of the chatbot frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API Configuration
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=gemini_api_key)

# Load data
try:
    df = pd.read_csv("data.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=['product type', 'product name', 'description', 'price'])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        You are a helpful chatbot for a business. Your knowledge base is the following CSV data:
        {df.to_string(index=False)}

        A user has asked: "{request.message}"

        Based on the data, provide a helpful and friendly response.
        If the question is not related to the data, politely say that you cannot answer.
        """
        response = model.generate_content(prompt)
        return ChatResponse(reply=response.text)
    except Exception as e:
        print(f"Error in chat endpoint: {e}") # This will go to chatbot_error.txt
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
