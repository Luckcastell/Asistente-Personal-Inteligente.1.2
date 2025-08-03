
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
conversation_files = []

@app.post("/upload/")
async def upload_file(file: UploadFile):
    with open(file.filename, "wb") as f:
        f.write(await file.read())

    uploaded_file = client.files.create(file=open(file.filename, "rb"), purpose="assistants")
    conversation_files.append(uploaded_file.id)

    return {"message": "Archivo subido", "file_id": uploaded_file.id}

@app.post("/chat/")
async def chat(message: str = Form(...)):
    assistant = client.beta.assistants.create(
        name="PDF Assistant",
        instructions="Eres un asistente que analiza los archivos cargados y responde preguntas sobre ellos.",
        model="gpt-4o-mini",
        tools=[{"type": "file_search"}]
    )

    thread = client.beta.threads.create()

    attachments = [{"file_id": fid, "tools": [{"type": "file_search"}]} for fid in conversation_files]

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=[{"type": "input_text", "text": message}],
        attachments=attachments
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value if messages.data else "No hay respuesta"

    return {"response": reply}
