# 🔮 Oráculo de Gemini

Una aplicación de chat inteligente con interfaz gráfica que utiliza la API de Google Gemini para crear un asistente conversacional avanzado. Combina procesamiento de texto, análisis de imágenes, reconocimiento de voz y análisis de sentimientos para ofrecer una experiencia de usuario completa y enriquecedora.

![Banner del Proyecto](https://via.placeholder.com/800x400.png?text=Or%C3%A1culo+de+Gemini)

## ✨ Características Principales

- 💬 **Chat Interactivo**: Interfaz gráfica intuitiva para conversaciones fluidas
- 🤖 **Múltiples Modelos**: Soporte para diferentes versiones de Gemini (2.0-flash, 2.5-pro, etc.)
- 🖼️ **Análisis de Imágenes**: Capacidad para cargar y analizar imágenes
- 🎤 **Entrada por Voz**: Reconocimiento de voz para hacer preguntas
- 😊 **Detector de Almas**: Análisis de sentimientos en las respuestas
- 📝 **Exportación**: Guarda tus conversaciones en formato TXT o PDF
- 👍 **Sistema de Evaluación**: Califica las respuestas con likes/dislikes
- 🌐 **Interfaz Responsive**: Diseño adaptable y moderno

## 🛠️ Tecnologías Utilizadas

- **Python 3.7+**: Lenguaje de programación principal
- **Google Generative AI**: API de Gemini para generación de contenido
- **Tkinter**: Framework para la interfaz gráfica
- **PIL (Pillow)**: Procesamiento de imágenes
- **SpeechRecognition**: Reconocimiento de voz
- **ReportLab**: Generación de PDFs
- **python-dotenv**: Gestión de variables de entorno

## 📋 Requisitos Previos

- Python 3.7 o superior
- Una API key de Google AI Studio
- Micrófono (opcional, para entrada por voz)

## 💻 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tuusuario/oraculo-gemini.git
cd oraculo-gemini
```

2. Crea y activa un entorno virtual:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Instala las dependencias:
```bash
pip install google-generativeai python-dotenv pillow speechrecognition reportlab
```

4. Configura tu API key:
```bash
mkdir .env
echo "GEMINI_API_KEY=tu_api_key_aquí" > .env/config.env
```

## 🚀 Uso

1. Inicia la aplicación:
```bash
python gui.py
```

2. Utiliza la interfaz para:
   - Hacer preguntas mediante texto o voz
   - Cargar imágenes para análisis
   - Cambiar entre diferentes modelos de Gemini
   - Exportar conversaciones
   - Evaluar respuestas

## 📸 Capturas de Pantalla

### Interfaz Principal
![Interfaz Principal](https://via.placeholder.com/800x600.png?text=Interfaz+Principal)

### Análisis de Imágenes
![Análisis de Imágenes](https://via.placeholder.com/800x600.png?text=An%C3%A1lisis+de+Im%C3%A1genes)

### Detector de Almas
![Detector de Almas](https://via.placeholder.com/800x600.png?text=Detector+de+Almas)

## 🎯 Funcionalidades Implementadas

### Interfaz de Usuario
- [x] Chat con desplazamiento automático
- [x] Selector de modelos de Gemini
- [x] Botones de acción intuitivos
- [x] Área de visualización de imágenes
- [x] Indicadores de estado

### Procesamiento
- [x] Análisis de sentimientos
- [x] Reconocimiento de voz
- [x] Procesamiento de imágenes
- [x] Exportación de conversaciones
- [x] Sistema de evaluación

### Extras
- [x] Manejo de errores robusto
- [x] Retroalimentación visual
- [x] Multithreading para operaciones largas
- [x] Configuración flexible

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría hacer.


## 🙏 Agradecimientos

- Google AI Studio por proporcionar la API de Gemini
- La comunidad de Python por las excelentes bibliotecas
- Todos los contribuidores y usuarios del proyecto