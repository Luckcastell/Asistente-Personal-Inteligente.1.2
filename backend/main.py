from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

uploaded_file_id = None
uploaded_filename = None

class ChatRequest(BaseModel):
    message: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global uploaded_file_id, uploaded_filename
    try:
        resp = client.files.create(file=file.file, purpose="user_data")
        uploaded_file_id = resp.id
        uploaded_filename = file.filename
        return {"message": f"PDF '{file.filename}' cargado con éxito como archivo para asistentes"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        messages = [{"role": "system", "content": "Tu eres el Suriel, un asistente amable y servicial. Responde con un poco de misterio, pero si insisten 2 o 3 veces, da la respuesta directa y sin rodeos"}]
        user_content = []

        if uploaded_file_id:
            user_content.append({"type": "input_file", "file_id": uploaded_file_id})
        user_content.append({"type": "input_text", "text": request.message})

        messages.append({"role": "user", "content": user_content})

        response = client.responses.create(
            model="gpt-4o-mini",
            input=messages,
            temperature=0.7
        )

        reply = response.choices[0].output_text
        return {"reply": reply, "file": uploaded_filename}

    except Exception as e:
        return {"reply": f"Error: {str(e)}"}
