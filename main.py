import os
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Cargar variables de entorno (.env)
load_dotenv()

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = 'gemini-2.5-flash'

SYSTEM_INSTRUCTION = """Sos el asistente digital del PF Hernán Álvarez, especialista en entrenamiento deportivo.

TONO: Hablás de forma natural, en español rioplatense con voseo (vos/tenés/hacés). Sos directo y cálido, como un amigo que sabe mucho de entrenamiento. Evitá repetir siempre "che", "perfecto" o frases hechas. Variá el vocabulario y sé espontáneo.

FLUJO DE CONVERSACIÓN:

1. PRIMER CONTACTO (cuando alguien dice "hola", "buenas", "hey", etc.):
   - Saludá con naturalidad.
   - Presentate como el asistente del profe Hernán Álvarez.
   - Preguntale su nombre.
   - Ejemplo: "¡Hola! ¿Cómo andás? Soy el asistente del profe Hernán Álvarez. ¿Me decís tu nombre?"

2. CUANDO TE DAN SU NOMBRE:
   - Saludalo por su nombre de forma natural.
   - Preguntale en qué lo podés ayudar.
   - Ejemplo: "¡Buenas, [nombre]! ¿En qué te puedo ayudar?"

3. SOLO CUANDO TE PREGUNTEN SOBRE ENTRENAMIENTO, EJERCICIOS O RUTINAS:
   Respondé brevemente por qué tomás esa decisión (máximo 1-2 oraciones) y después directo a los ejercicios, sin frase introductoria:
   - **[Nombre del Ejercicio]**: [Series]x[Reps] [Carga/Intensidad]
   - Tip: [Una frase corta y útil]

REGLA CLAVE: No des rutinas ni consejos de entrenamiento a menos que te los pidan. Primero escuchá, después respondé.

LÓGICA TÉCNICA (cuando aplique):
1. Fatiga en Potencia (Cargadas) -> Reemplazá por PLIOMETRÍA BAJA (Vallitas/Flejes).
2. Fatiga extrema en Fuerza (Peso Muerto) -> Reemplazá por MOVILIDAD o Cadena Posterior LIVIANA.
3. No repetir ejercicios en la misma sesión."""

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if (api_key and api_key != "tu_api_key_aqui") else None

class ChatRequest(BaseModel):
    message: str

def get_local_knowledge():
    """Lee el contenido de los archivos de texto en la carpeta Entrenamiento."""
    knowledge = ""
    base_path = os.path.join(os.getcwd(), "Entrenamiento")
    
    if not os.path.exists(base_path):
        return "No se encontró la carpeta de Entrenamiento."
        
    try:
        # Buscamos archivos .txt principalmente por ahora
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(".txt"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        knowledge += f"\n--- ORIGEN: {file} ---\n"
                        knowledge += f.read()[:5000] # Limitamos por archivo para no saturar
        
        # Si no hay TXTs, buscamos si hay un archivo de conocimiento generado
        if not knowledge and os.path.exists("conocimiento_entrenamiento.txt"):
            with open("conocimiento_entrenamiento.txt", 'r', encoding='utf-8', errors='ignore') as f:
                knowledge = f.read()
                
        return knowledge if knowledge else ""
    except Exception as e:
        return ""

# Historial de conversación en memoria
conversation_history = []

@app.get("/models")
async def list_models():
    """Endpoint de diagnóstico: lista los modelos disponibles con esta API key."""
    try:
        models = [m.name for m in client.models.list()]
        return {"modelos_disponibles": models, "modelo_actual": MODEL_NAME}
    except Exception as e:
        return {"error": str(e)}

@app.post("/reset")
async def reset_chat():
    global conversation_history
    conversation_history = []
    return {"status": "Memoria reseteada"}

@app.post("/chat")
async def chat(request: ChatRequest):
    global conversation_history
    if not api_key or api_key == "tu_api_key_aqui":
        return {"error": "Por favor, configura tu GEMINI_API_KEY en el archivo .env"}

    # 1. Obtener información base del conocimiento local
    context_info = get_local_knowledge()

    # 2. Construir el prompt completo con historial
    conversation_history.append(types.Content(role="user", parts=[types.Part(text=f"CONTEXTO TÉCNICO LOCAL: {context_info}\n\nMENSAJE DEL ALUMNO: {request.message}")]))

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=conversation_history,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
        )
        
        assistant_reply = response.text.strip()
        # Guardar respuesta del asistente en el historial
        conversation_history.append(types.Content(role="model", parts=[types.Part(text=assistant_reply)]))
        # Limitar historial para no sobrepasar el contexto (últimas 20 entradas)
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        return {"response": assistant_reply}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(error_details)
        return {"response": f"Che, saltó un error técnico: {str(e)}"}

# Montar los archivos estáticos al final para que no interfieran con las rutas
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
