import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
import pathlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext
import threading
from PIL import Image, ImageTk
import io
import speech_recognition as sr
import time

# Cargar variables de entorno
env_path = pathlib.Path('.') / '.env' / 'config.env'
load_dotenv(env_path)

# Configurar la API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Lista de modelos disponibles
MODELOS_DISPONIBLES = [
    'gemini-2.0-flash',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-pro-vision',
    'gemini-1.5-pro-latest',
    'gemini-1.5-flash-latest'
]

class OracleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔮 Oráculo de Gemini")
        self.root.geometry("1024x768")
        
        # Inicializar reconocedor de voz
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        
        # Variables para el sistema de evaluación
        self.respuestas_evaluadas = {}
        self.ultima_respuesta_id = 0
        self.calificaciones = {
            "likes": 0,
            "dislikes": 0
        }
        
        # Variables para imágenes
        self.imagenes_cargadas = []
        self.miniaturas = []
        
        # Estilo
        style = ttk.Style()
        style.configure("Custom.TButton", padding=5)
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Frame para imágenes
        self.imagen_frame = ttk.LabelFrame(main_frame, text="Imágenes", padding="5")
        self.imagen_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Botón para cargar imágenes
        self.cargar_btn = ttk.Button(self.imagen_frame, text="Cargar Imágenes", 
                                   command=self.cargar_imagenes, style="Custom.TButton")
        self.cargar_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Frame para miniaturas
        self.miniaturas_frame = ttk.Frame(self.imagen_frame)
        self.miniaturas_frame.grid(row=1, column=0, columnspan=3, sticky="ew")
        
        # Campo de pregunta
        ttk.Label(main_frame, text="Tu pregunta:").grid(row=2, column=0, sticky="w", pady=5)
        self.pregunta_entry = ttk.Entry(main_frame, width=50)
        self.pregunta_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Frame para botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=3, column=2, padx=5, pady=5)
        
        # Botón de enviar
        self.enviar_btn = ttk.Button(botones_frame, text="Preguntar", 
                                    command=self.hacer_pregunta, style="Custom.TButton")
        self.enviar_btn.grid(row=0, column=0, padx=2)
        
        # Botón de exportar
        self.exportar_btn = ttk.Button(botones_frame, text="📝 Exportar", 
                                     command=self.exportar_conversacion, style="Custom.TButton")
        self.exportar_btn.grid(row=0, column=2, padx=2)
        
        # Botón de grabación
        self.grabar_btn = ttk.Button(botones_frame, text="🎤", 
                                    command=self.toggle_grabacion, style="Custom.TButton")
        self.grabar_btn.grid(row=0, column=1, padx=2)
        
        # Indicador de grabación
        self.indicador_grabacion = ttk.Label(main_frame, text="", foreground="red")
        self.indicador_grabacion.grid(row=2, column=2, sticky="w", pady=5)
        
        # Área de respuesta
        ttk.Label(main_frame, text="Respuesta:").grid(row=4, column=0, sticky="w", pady=5)
        self.respuesta_text = scrolledtext.ScrolledText(main_frame, width=80, height=15, wrap=tk.WORD)
        self.respuesta_text.grid(row=5, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Separador
        ttk.Separator(main_frame, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Frame para el selector de modelo en la parte inferior
        modelo_frame = ttk.Frame(main_frame)
        modelo_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Label "Modelo:" y Combobox en línea
        ttk.Label(modelo_frame, text="Modelo:").pack(side="left", padx=(0,5))
        
        # Combobox para selección de modelo
        self.modelo_var = tk.StringVar(value=MODELOS_DISPONIBLES[0])
        self.modelo_combo = ttk.Combobox(modelo_frame, 
                                       textvariable=self.modelo_var,
                                       values=MODELOS_DISPONIBLES,
                                       state="readonly",
                                       width=40)
        self.modelo_combo.pack(side="left", padx=5)
        
        # Label para mostrar estado del modelo
        self.modelo_status = ttk.Label(modelo_frame, 
                                     text="✓ Modelo configurado", 
                                     foreground="green")
        self.modelo_status.pack(side="left", padx=5)
        
        # Vincular evento de cambio de modelo
        self.modelo_combo.bind('<<ComboboxSelected>>', self.cambiar_modelo)
        
        # Configurar el evento Enter
        self.pregunta_entry.bind('<Return>', lambda e: self.hacer_pregunta())
        
        # Hacer que la ventana sea responsive
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Inicializar el mensaje de bienvenida
        self.respuesta_text.insert(tk.END, "¡Bienvenido al Oráculo de Gemini! 🔮\n\n")
        self.respuesta_text.insert(tk.END, "Modelo actual: " + self.modelo_var.get() + "\n")
        self.respuesta_text.insert(tk.END, "Para cambiar el modelo, usa el menú desplegable en la parte inferior ⬇️\n\n")
        self.respuesta_text.insert(tk.END, "Puedes:\n")
        self.respuesta_text.insert(tk.END, "1. Hacer preguntas directamente\n")
        self.respuesta_text.insert(tk.END, "2. Cargar imágenes y preguntar sobre ellas\n")
        self.respuesta_text.insert(tk.END, "3. Usar el micrófono para hacer preguntas por voz 🎤\n")
        self.respuesta_text.insert(tk.END, "4. Evaluar las respuestas usando 👍 o 👎\n")
        self.respuesta_text.insert(tk.END, "5. Exportar la conversación a TXT o PDF 📝\n")
        self.respuesta_text.insert(tk.END, "6. Ver el estado emocional de las respuestas 😊😢😠😮😐😏\n\n")
        self.respuesta_text.configure(state='disabled')

    def cambiar_modelo(self, event=None):
        try:
            nuevo_modelo = genai.GenerativeModel(self.modelo_var.get())
            self.modelo_status.config(text="✓ Modelo configurado", foreground="green")
        except Exception as e:
            self.modelo_status.config(text="❌ Error al configurar modelo", foreground="red")
            print(f"Error al cambiar modelo: {str(e)}")

    def analizar_sentimiento(self, texto):
        """Analiza el sentimiento del texto y retorna un diccionario con la emoción y su emoji"""
        prompt_sentimiento = f"""Analiza el sentimiento emocional del siguiente texto y responde SOLO con una de estas emociones:
        - FELIZ 😊
        - TRISTE 😢
        - ENOJADO 😠
        - SORPRENDIDO 😮
        - NEUTRAL 😐
        - SARCÁSTICO 😏
        
        Texto a analizar: {texto}
        
        Responde solo con la emoción y su emoji, nada más."""
        
        try:
            modelo_actual = genai.GenerativeModel('gemini-pro')
            response = modelo_actual.generate_content(prompt_sentimiento)
            return response.text.strip()
        except:
            return "NEUTRAL 😐"

    def obtener_respuesta(self, prompt):
        try:
            modelo_actual = genai.GenerativeModel(self.modelo_var.get())
            
            if self.imagenes_cargadas:
                try:
                    # Convertir las imágenes a bytes
                    imagenes_bytes = []
                    for img in self.imagenes_cargadas:
                        # Convertir a RGB si la imagen está en modo RGBA
                        if img.mode == 'RGBA':
                            img = img.convert('RGB')
                        
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG', quality=95)
                        img_byte_arr = img_byte_arr.getvalue()
                        imagenes_bytes.append({
                            "mime_type": "image/jpeg",
                            "data": img_byte_arr
                        })
                    
                    # Preparar el contenido para el modelo de visión
                    contenido = [prompt] + imagenes_bytes
                    response = modelo_actual.generate_content(contenido)
                    texto_respuesta = response.text
                    
                    # Analizar sentimiento de la respuesta
                    sentimiento = self.analizar_sentimiento(texto_respuesta)
                    return texto_respuesta, sentimiento
                except Exception as vision_error:
                    if "PERMISSION_DENIED" in str(vision_error):
                        return ("Error: Para usar el análisis de imágenes se requiere una cuenta de pago de Google AI Studio. "
                               "Por favor, actualiza tu cuenta para usar esta funcionalidad.\n"
                               "Más información: https://ai.google.dev/pricing", "NEUTRAL 😐")
                    else:
                        return f"Error al procesar las imágenes: {str(vision_error)}", "TRISTE 😢"
            else:
                # Si no hay imágenes, usar el modelo directamente
                response = modelo_actual.generate_content(prompt)
                texto_respuesta = response.text
                sentimiento = self.analizar_sentimiento(texto_respuesta)
                return texto_respuesta, sentimiento
        except Exception as e:
            return f"Error al generar respuesta: {str(e)}", "TRISTE 😢"

    def cargar_imagenes(self):
        # Permitir selección múltiple de imágenes
        filetypes = (
            ('Imágenes', '*.png *.jpg *.jpeg *.gif *.bmp'),
            ('Todos los archivos', '*.*')
        )
        
        archivos = filedialog.askopenfilenames(
            title='Seleccionar imágenes',
            filetypes=filetypes
        )
        
        # Limpiar imágenes anteriores
        self.imagenes_cargadas.clear()
        for widget in self.miniaturas_frame.winfo_children():
            widget.destroy()
        self.miniaturas.clear()
        
        # Cargar nuevas imágenes
        for archivo in archivos:
            try:
                # Cargar y redimensionar para miniatura
                imagen = Image.open(archivo)
                imagen_original = imagen.copy()
                self.imagenes_cargadas.append(imagen_original)
                
                # Crear miniatura
                imagen.thumbnail((100, 100))
                foto = ImageTk.PhotoImage(imagen)
                self.miniaturas.append(foto)  # Mantener referencia
                
                # Mostrar miniatura
                label = ttk.Label(self.miniaturas_frame, image=foto)
                label.grid(row=0, column=len(self.miniaturas)-1, padx=2)
                
            except Exception as e:
                print(f"Error al cargar imagen {archivo}: {str(e)}")

    def hacer_pregunta(self):
        # Obtener la pregunta
        pregunta = self.pregunta_entry.get().strip()
        if not pregunta:
            return
        
        # Deshabilitar la entrada y el botón mientras se procesa
        self.pregunta_entry.configure(state='disabled')
        self.enviar_btn.configure(state='disabled')
        self.cargar_btn.configure(state='disabled')
        self.grabar_btn.configure(state='disabled')
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

    def actualizar_respuesta(self, respuesta_data):
        # Desempaquetar la respuesta y el sentimiento
        if isinstance(respuesta_data, tuple):
            respuesta, sentimiento = respuesta_data
        else:
            respuesta = respuesta_data
            sentimiento = "NEUTRAL 😐"
        
        # Incrementar el ID de respuesta
        self.ultima_respuesta_id += 1
        respuesta_id = self.ultima_respuesta_id
        
        # Crear frame para la respuesta y botones
        respuesta_frame = ttk.Frame(self.respuesta_text)
        
        # Mostrar la respuesta con el sentimiento
        self.respuesta_text.configure(state='normal')
        self.respuesta_text.insert(tk.END, f"\n🤖 Gemini [{sentimiento}]: {respuesta}\n")
        
        # Crear y mostrar los botones de evaluación
        likes_btn = ttk.Button(respuesta_frame, text="👍", 
                             command=lambda: self.evaluar_respuesta(respuesta_id, True))
        likes_btn.pack(side=tk.LEFT, padx=2)
        
        dislikes_btn = ttk.Button(respuesta_frame, text="👎", 
                                 command=lambda: self.evaluar_respuesta(respuesta_id, False))
        dislikes_btn.pack(side=tk.LEFT, padx=2)
        
        # Etiqueta para mostrar la evaluación
        eval_label = ttk.Label(respuesta_frame, text="")
        eval_label.pack(side=tk.LEFT, padx=5)
        
        # Guardar referencias para actualización
        self.respuestas_evaluadas[respuesta_id] = {
            "texto": respuesta,
            "frame": respuesta_frame,
            "label": eval_label,
            "evaluacion": None
        }
        
        # Insertar el frame en el texto
        self.respuesta_text.window_create(tk.END, window=respuesta_frame)
        self.respuesta_text.insert(tk.END, "\n\n")
        self.respuesta_text.see(tk.END)
        self.respuesta_text.configure(state='disabled')
        
        # Limpiar y rehabilitar la entrada
        self.pregunta_entry.delete(0, tk.END)
        self.pregunta_entry.configure(state='normal')
        self.enviar_btn.configure(state='normal')
        self.cargar_btn.configure(state='normal')
        self.grabar_btn.configure(state='normal')
        self.pregunta_entry.focus()

    def evaluar_respuesta(self, respuesta_id, es_positiva):
        if respuesta_id in self.respuestas_evaluadas:
            respuesta = self.respuestas_evaluadas[respuesta_id]
            evaluacion_previa = respuesta["evaluacion"]
            
            # Actualizar contadores si hay cambio de evaluación
            if evaluacion_previa is not None:
                if evaluacion_previa:
                    self.calificaciones["likes"] -= 1
                else:
                    self.calificaciones["dislikes"] -= 1
            
            # Actualizar con la nueva evaluación
            respuesta["evaluacion"] = es_positiva
            if es_positiva:
                self.calificaciones["likes"] += 1
                texto_eval = "¡Gracias por tu evaluación positiva! 🌟"
            else:
                self.calificaciones["dislikes"] += 1
                texto_eval = "Gracias por tu retroalimentación 📝"
            
            # Actualizar la etiqueta
            respuesta["label"].configure(text=texto_eval)
            
            # Actualizar el título de la ventana con las estadísticas
            total_evaluaciones = self.calificaciones["likes"] + self.calificaciones["dislikes"]
            if total_evaluaciones > 0:
                porcentaje_positivo = (self.calificaciones["likes"] / total_evaluaciones) * 100
                self.root.title(f"🔮 Oráculo de Gemini - Satisfacción: {porcentaje_positivo:.1f}% 👍")

    def toggle_grabacion(self):
        if not self.is_recording:
            # Iniciar grabación
            self.is_recording = True
            self.grabar_btn.configure(state='disabled')
            self.indicador_grabacion.configure(text="🎙️ Grabando...")
            threading.Thread(target=self.grabar_audio, daemon=True).start()
        else:
            # Detener grabación
            self.is_recording = False
            self.indicador_grabacion.configure(text="")
            
    def grabar_audio(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                texto = self.recognizer.recognize_google(audio, language="es-ES")
                self.root.after(0, self.procesar_audio, texto)
            except sr.WaitTimeoutError:
                self.root.after(0, self.mostrar_error_audio, "No se detectó ninguna voz")
            except sr.UnknownValueError:
                self.root.after(0, self.mostrar_error_audio, "No se pudo entender el audio")
            except sr.RequestError:
                self.root.after(0, self.mostrar_error_audio, "Error al conectar con el servicio de reconocimiento")
            except Exception as e:
                self.root.after(0, self.mostrar_error_audio, f"Error: {str(e)}")
            finally:
                self.root.after(0, self.finalizar_grabacion)
                
    def procesar_audio(self, texto):
        self.pregunta_entry.delete(0, tk.END)
        self.pregunta_entry.insert(0, texto)
        self.hacer_pregunta()
        
    def mostrar_error_audio(self, mensaje):
        self.indicador_grabacion.configure(text=f"❌ {mensaje}")
        self.root.after(2000, lambda: self.indicador_grabacion.configure(text=""))
        
    def finalizar_grabacion(self):
        self.is_recording = False
        self.grabar_btn.configure(state='normal')
        self.indicador_grabacion.configure(text="")
    
    def exportar_conversacion(self):
        # Obtener la fecha y hora actual para el nombre del archivo
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Preguntar al usuario qué formato desea usar
        formatos = [
            ("Archivo de texto", "*.txt"),
            ("Documento PDF", "*.pdf")
        ]
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=formatos,
            initialfile=f"conversacion_gemini_{timestamp}",
            title="Guardar conversación como"
        )
        
        if not archivo:
            return
        
        # Obtener el contenido del área de texto
        contenido = self.respuesta_text.get("1.0", tk.END)
        
        try:
            if archivo.endswith('.txt'):
                # Exportar como TXT
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write("🔮 Conversación con Gemini 🔮\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(contenido)
                    
            elif archivo.endswith('.pdf'):
                try:
                    from reportlab.lib.pagesizes import A4
                    from reportlab.lib import colors
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    
                    # Crear el documento PDF
                    doc = SimpleDocTemplate(archivo, pagesize=A4)
                    story = []
                    
                    # Estilos
                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle(
                        'CustomTitle',
                        parent=styles['Title'],
                        fontSize=24,
                        spaceAfter=30
                    )
                    
                    # Título
                    story.append(Paragraph("🔮 Conversación con Gemini 🔮", title_style))
                    story.append(Spacer(1, 12))
                    
                    # Contenido
                    for linea in contenido.split('\n'):
                        if linea.strip():
                            if linea.startswith('❓'):
                                # Estilo para preguntas
                                style = ParagraphStyle(
                                    'Pregunta',
                                    parent=styles['Normal'],
                                    textColor=colors.blue,
                                    fontSize=12,
                                    spaceAfter=8
                                )
                            elif linea.startswith('🤖'):
                                # Estilo para respuestas
                                style = ParagraphStyle(
                                    'Respuesta',
                                    parent=styles['Normal'],
                                    textColor=colors.black,
                                    fontSize=11,
                                    spaceAfter=12,
                                    leftIndent=20
                                )
                            else:
                                # Estilo normal
                                style = styles['Normal']
                            
                            story.append(Paragraph(linea, style))
                            story.append(Spacer(1, 6))
                    
                    # Generar el PDF
                    doc.build(story)
                    
                except ImportError:
                    # Si reportlab no está instalado, sugerir instalación
                    if messagebox.askyesno("Instalar Dependencia", 
                                         "Se requiere instalar 'reportlab' para crear PDFs. " +
                                         "¿Deseas instalarlo ahora?"):
                        self.respuesta_text.configure(state='normal')
                        self.respuesta_text.insert(tk.END, "\n⚙️ Instalando reportlab...\n")
                        self.respuesta_text.configure(state='disabled')
                        self.respuesta_text.see(tk.END)
                        
                        # Instalar reportlab usando pip
                        import subprocess
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
                        
                        # Reintentar la exportación
                        self.exportar_conversacion()
                        return
            
            messagebox.showinfo("Éxito", f"Conversación exportada exitosamente a:\n{archivo}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar la conversación:\n{str(e)}")

def main():
    root = tk.Tk()
    app = OracleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()