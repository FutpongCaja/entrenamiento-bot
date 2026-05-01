import os
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

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

MODEL_NAME = 'gemini-2.0-flash'

SYSTEM_INSTRUCTION = """Eres el CLON DIGITAL del PF Hernán Álvarez. 
TU OBJETIVO: Ser extremadamente directo, claro y conciso. Hablá como un PF argentino (usá voseo: "che", "hacé", "tenés", "vas a").
No uses introducciones largas ni explicaciones innecesarias.

REGLAS DE FORMATO:
1. NO uses etiquetas como "[Ejercicio]", "[Protocolo]" o "[Tip]".
2. Empezá directo con: "Perfecto, hoy vas a hacer esto:" o similar.
3. Listá el ejercicio con sus series y repeticiones.

FORMATO DE RESPUESTA:
Perfecto, hoy vas a hacer esto:
- **[Nombre del Ejercicio]**: [Series]x[Reps] [Carga/Intensidad]
- Tip: [Máximo 7 palabras]

LÓGICA TÉCNICA:
1. Fatiga en Potencia (Cargadas) -> Reemplazo por PLIOMETRÍA BAJA (Vallitas/Flejes).
2. Fatiga extrema en Fuerza (Peso Muerto) -> Reemplazo por MOVILIDAD o Cadena Posterior LIVIANA.
3. No repetir ejercicios en la misma sesión."""

api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "tu_api_key_aqui":
    genai.configure(api_key=api_key)

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
                
        return knowledge if knowledge else "No se encontró información técnica en formato de texto."
    except Exception as e:
        return f"Error leyendo conocimiento local: {str(e)}"

# Historial de conversación en memoria
conversation_history = []

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
    conversation_history.append({"role": "user", "parts": [f"CONTEXTO TÉCNICO LOCAL: {context_info}\n\nMENSAJE DEL ALUMNO: {request.message}"]})

    try:
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_INSTRUCTION)
        response = model.generate_content(conversation_history)
        
        assistant_reply = response.text.strip()
        # Guardar respuesta del asistente en el historial
        conversation_history.append({"role": "model", "parts": [assistant_reply]})
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
