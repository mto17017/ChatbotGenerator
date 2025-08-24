import os
import shutil
import subprocess
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API Configuration
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=gemini_api_key)

# Port management for generated chatbots
next_port = 8001

class UrlRequest(BaseModel):
    url: str

def scrape_website(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {e}")

def generate_csv_from_text(text: str) -> str:
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Based on the following text from a website, please create a structured dataset in CSV format.
    The CSV must have exactly these four columns: 'product type', 'product name', 'description', 'price'.
    Ensure that each field is enclosed in double quotes if it contains commas or newlines.
    Extract relevant product information from the text.

    Text:
    {text}

    CSV Output:
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating CSV from text: {e}")

def create_and_run_chatbot(project_name: str, csv_data: str) -> int:
    global next_port
    template_dir = "/Users/tanzidontika/Documents/CHATBOTV2/chatbot-generator/chatbot-template"
    new_project_dir = f"/Users/tanzidontika/Documents/CHATBOTV2/{project_name}"

    if os.path.exists(new_project_dir):
        shutil.rmtree(new_project_dir)
    
    shutil.copytree(template_dir, new_project_dir)

    csv_path = os.path.join(new_project_dir, "chatbot-backend", "data.csv")
    with open(csv_path, "w") as f:
        f.write(csv_data)

    # Write GEMINI_API_KEY to the new chatbot's .env file
    chatbot_env_path = os.path.join(new_project_dir, "chatbot-backend", ".env")
    with open(chatbot_env_path, "w") as f:
        f.write(f"GEMINI_API_KEY={gemini_api_key}\n")

    backend_dir = os.path.join(new_project_dir, "chatbot-backend")
    port = next_port
    next_port += 1
    
    main_py_path = os.path.join(backend_dir, "main.py")
    with open(main_py_path, "r+") as f:
        content = f.read()
        f.seek(0)
        f.write(content.replace("port=8001", f"port={port}"))

    log_file = open(os.path.join(new_project_dir, "chatbot_log.txt"), "w")
    error_file = open(os.path.join(new_project_dir, "chatbot_error.txt"), "w")
    
    # Assuming python3.12 is used, as per user's environment
    python_executable = "python3.12"
    
    subprocess.Popen(
        [python_executable, "main.py"],
        cwd=backend_dir,
        stdout=log_file,
        stderr=error_file
    )
    return port

@app.post("/generate-from-url")
async def generate_from_url(request: UrlRequest):
    try:
        text_content = scrape_website(request.url)
        csv_content = generate_csv_from_text(text_content)
        project_name = f"chatbot_{request.url.split('//')[1].split('/')[0].replace('.', '_')}"
        port = create_and_run_chatbot(project_name, csv_content)
        return {"message": f"Chatbot '{project_name}' generated successfully!", "port": port}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.options("/generate-from-csv")
async def options_generate_from_csv():
    return {"message": "OK"}

@app.post("/generate-from-csv")
async def generate_from_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")
    try:
        csv_data = await file.read()
        project_name = f"chatbot_{file.filename.replace('.csv', '')}"
        port = create_and_run_chatbot(project_name, csv_data.decode("utf-8"))
        return {"message": f"Chatbot '{project_name}' generated successfully!", "port": port}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)