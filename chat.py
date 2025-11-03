import os
import google.generativeai as genai
from dotenv import load_dotenv
import pathlib
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import threading

# Cargar variables de entorno
env_path = pathlib.Path('.') / '.env' / 'config.env'
load_dotenv(env_path)

# Configurar la API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Crear modelo de chat
chat_model = genai.GenerativeModel('gemini-2.0-flash')

class OracleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔮 Oráculo de Gemini")
        self.root.geometry("600x400")
        
        # Estilo
        style = ttk.Style()
        style.configure("Custom.TButton", padding=5)
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Campo de pregunta
        ttk.Label(main_frame, text="Tu pregunta:").grid(row=0, column=0, sticky="w", pady=5)
        self.pregunta_entry = ttk.Entry(main_frame, width=50)
        self.pregunta_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Botón de enviar
        self.enviar_btn = ttk.Button(main_frame, text="Preguntar", 
                                    command=self.hacer_pregunta, style="Custom.TButton")
        self.enviar_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Área de respuesta
        ttk.Label(main_frame, text="Respuesta:").grid(row=2, column=0, sticky="w", pady=5)
        self.respuesta_text = scrolledtext.ScrolledText(main_frame, width=60, height=15, wrap=tk.WORD)
        self.respuesta_text.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Configurar el evento Enter
        self.pregunta_entry.bind('<Return>', lambda e: self.hacer_pregunta())
        
        # Hacer que la ventana sea responsive
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Inicializar el mensaje de bienvenida
        self.respuesta_text.insert(tk.END, "¡Bienvenido al Oráculo de Gemini! 🔮\n")
        self.respuesta_text.insert(tk.END, "Haz tus preguntas y obtén respuestas instantáneas.\n\n")
        self.respuesta_text.configure(state='disabled')

    def obtener_respuesta(self, prompt):
        try:
            response = chat_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error al generar respuesta: {str(e)}"

    def hacer_pregunta(self):
        # Obtener la pregunta
        pregunta = self.pregunta_entry.get().strip()
        if not pregunta:
            return
        
        # Deshabilitar la entrada y el botón mientras se procesa
        self.pregunta_entry.configure(state='disabled')
        self.enviar_btn.configure(state='disabled')
        self.respuesta_text.configure(state='normal')
        
        # Mostrar la pregunta en el área de respuesta
        self.respuesta_text.insert(tk.END, f"\n❓ Tú: {pregunta}\n")
        self.respuesta_text.see(tk.END)
        
        # Función para procesar la respuesta en un hilo separado
        def procesar_respuesta():
            respuesta = self.obtener_respuesta(pregunta)
            
            # Actualizar la GUI en el hilo principal
            self.root.after(0, self.actualizar_respuesta, respuesta)
        
        # Iniciar el procesamiento en un hilo separado
        threading.Thread(target=procesar_respuesta, daemon=True).start()

    def actualizar_respuesta(self, respuesta):
        # Mostrar la respuesta
        self.respuesta_text.insert(tk.END, f"\n🤖 Gemini: {respuesta}\n\n")
        self.respuesta_text.see(tk.END)
        
        # Limpiar y rehabilitar la entrada
        self.pregunta_entry.delete(0, tk.END)
        self.pregunta_entry.configure(state='normal')
        self.enviar_btn.configure(state='normal')
        self.respuesta_text.configure(state='disabled')
        self.pregunta_entry.focus()

def main():
    root = tk.Tk()
    app = OracleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()