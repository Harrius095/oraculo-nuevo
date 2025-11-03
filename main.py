import os
import google.generativeai as genai
from dotenv import load_dotenv
import pathlib

# Cargar variables de entorno
env_path = pathlib.Path('.') / '.env' / 'config.env'
load_dotenv(env_path)

# Configurar la API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Mostrar modelos disponibles
print("Modelos disponibles:")
for m in genai.list_models():
    print(f"- {m.name}")

# Crear un modelo (usando Gemini 2.0 Flash)
model = genai.GenerativeModel('gemini-2.0-flash')

def obtener_respuesta(prompt):
    try:
        # Generar respuesta
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

def main():
    print("🔮 Bienvenido al Oráculo de Gemini 🔮")
    print("Escribe 'salir' para terminar")
    
    while True:
        # Obtener input del usuario
        prompt = input("\n❓ Tu pregunta: ")
        
        if prompt.lower() == 'salir':
            print("\n👋 ¡Hasta luego!")
            break
            
        # Obtener y mostrar la respuesta
        print("\n🤖 Respuesta:")
        respuesta = obtener_respuesta(prompt)
        print(respuesta)

if __name__ == "__main__":
    main()