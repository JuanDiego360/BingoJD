# Bingo JD - Sistema de Bingo con Integración WhatsApp

Una aplicación de bingo moderna y completa desarrollada en Python que permite gestionar jugadores, generar cartones únicos y enviarlos automáticamente por WhatsApp. Incluye una interfaz gráfica intuitiva y un sistema de verificación de bingo con síntesis de voz.

## Características Principales

- 🎮 Interfaz gráfica amigable construida con Tkinter
- 🎲 Generación de cartones únicos de bingo
- 🖼️ Conversión de cartones a imágenes PNG
- 📦 Compresión automática de imágenes en archivos ZIP
- 📱 Envío automático de cartones por WhatsApp
- 🔊 Síntesis de voz para cantar los números
- ✅ Sistema de verificación de cartones ganadores
- 👥 Gestión completa de jugadores
- 🔄 Estado de envío y verificación de cartones
- 🔍 Seguimiento del estado de generación de imágenes

## Requisitos del Sistema

### Software Base
- Python 3.12.3 o superior
- WhatsApp Web (para el envío de cartones)
- Ubuntu (o distribución Linux similar)
- Navegador web compatible con WhatsApp Web

### Dependencias del Sistema
```bash
# Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk sox libsox-fmt-mp3 espeak
```

### Configuración de la Síntesis de Voz
1. Instalar gtts-cli:
```bash
pip install gTTS
```

2. Agregar la función de síntesis de voz a tu `.zshrc` ó `.bashrc`:
```bash
# Abrir el archivo .zshrc ó .bashrc
nano ~/.zshrc

# Añadir la siguiente función
function hablar() {
  gtts-cli -l es -t com "$1" | play -q -t mp3 - tempo 1
}

# Guardar y recargar el archivo
source ~/.zshrc
```

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/JuanDiego360/BingoJD.git
cd bingo
```

2. Crear y activar un entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instalar las dependencias de Python:
```bash
pip install -r requirements.txt
```

## Estructura del Proyecto

```
bingo/
├── aplicacion_bingo.py    # Aplicación principal y GUI
├── generador_cartones.py  # Generador de cartones únicos
├── convertidor_imag.py    # Conversor de cartones a imágenes
├── whatsapp_sender.py     # Módulo de envío por WhatsApp
├── comprobar_carton.py    # Sistema de verificación
├── jugadores.py           # Gestión de jugadores
├── requirements.txt       # Dependencias del proyecto
├── estado_imagenes.json   # Estado de generación de imágenes
├── estado_envio.json      # Estado de envío de cartones
├── comprobar_carton.md    # Lista de comprobación de cartones
├── cartones/              # Directorio de cartones generados
└── cartones/imagenes_de_los_cartones/  # Imágenes PNG de los cartones
```

## Uso

1. Iniciar la aplicación:
```bash
python3 aplicacion_bingo.py
```

2. Flujo de trabajo típico:
   - Añadir jugadores con sus números de WhatsApp
   - Generar cartones únicos para cada jugador
   - Convertir cartones a imágenes PNG (selectivamente según estado)
   - Comprimir imágenes en archivo ZIP para distribución
   - Enviar cartones por WhatsApp
   - Iniciar el juego de bingo
   - Verificar cartones ganadores

## Funcionalidades Detalladas

### Gestión de Jugadores
- Añadir jugadores con nombre y número de WhatsApp
- Asignar múltiples cartones a un jugador
- Eliminar jugadores y sus cartones asociados

### Generación de Cartones
- Cartones únicos garantizados
- Formato markdown para fácil visualización
- Verificación automática de duplicados
- Conversión selectiva a imágenes PNG basada en estado
- Almacenamiento organizado en directorio dedicado

### Conversión y Gestión de Imágenes
- Conversión de cartones markdown a imágenes PNG
- Generación selectiva basada en el estado del cartón
- Almacenamiento en directorio dedicado (`cartones/imagenes_de_los_cartones`)
- Compresión inteligente de imágenes recientes en archivos ZIP
- Generación de archivos ZIP con marcas de tiempo únicas
- Eliminación de imágenes al borrar jugadores

### Sistema de Envío por WhatsApp
- Envío automático de cartones
- Seguimiento del estado de envío
- Reintento de envíos fallidos
- Requiere WhatsApp Web activo
- Opción de enviar imágenes o archivos ZIP

### Juego de Bingo
- Interfaz intuitiva para el cantador
- Síntesis de voz para números cantados
- Verificación automática de cartones ganadores
- Historial de números cantados

## Consideraciones de Seguridad
- No almacena contraseñas
- Usa WhatsApp Web para autenticación
- Mantiene registro de envíos localmente

### Gestión de Estados y Limpieza
- Seguimiento del estado de generación de imágenes (`estado_imagenes.json`)
- Seguimiento del estado de envío de cartones (`estado_envio.json`)
- Función "Borrar Todo" para limpiar todos los datos manteniendo la estructura de directorios
- Eliminación selectiva de imágenes al eliminar jugadores
- Registro de imágenes generadas recientemente para compresión selectiva

## Solución de Problemas

### WhatsApp Web
- Asegurarse de tener WhatsApp Web abierto y activo
- Verificar la conexión a internet
- Mantener la sesión iniciada durante el envío

### Síntesis de Voz
- Verificar que sox y libsox-fmt-mp3 estén instalados
- Comprobar que la función 'hablar' esté correctamente configurada
- Asegurar que el sistema de audio funcione

## Contribuir
Las contribuciones son bienvenidas. Por favor:
1. Haz fork del repositorio
2. Crea una rama para tu característica
3. Envía un pull request


## Autor
Juan Diego Florez Vera

## Agradecimientos
- A la comunidad de Python

- A los usuarios que proporcionan retroalimentación
