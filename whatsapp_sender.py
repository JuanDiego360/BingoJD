import pywhatkit
import json
import os
from datetime import datetime, timedelta
import time

def leer_carton(archivo_md, nombre_carton):
    """Lee un archivo markdown y lo convierte en formato de texto para WhatsApp.
    Args:
        archivo_md: Ruta al archivo markdown del cartón
        nombre_carton: Nombre/identificador del cartón
    """
    try:
        with open(archivo_md, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Convertir el formato markdown a un formato más amigable para WhatsApp
        lineas = [linea for linea in contenido.split('\n') if linea.strip() and ':-:' not in linea]
        
        # Extraer los números del cartón
        numeros = []
        for linea in lineas[1:]:  # Saltar la línea del encabezado
            fila = [num.strip() for num in linea.split('|')[1:-1]]
            numeros.append(fila)
        
        # Formatear el mensaje
        carton_texto = "*Bingo JD*\n"
        carton_texto += f"Cartón: {nombre_carton}\n\n"
        carton_texto += "🎯 *CARTÓN DE BINGO* 🎯\n\n\n"
        carton_texto += " B     I     N    G     O\n"
        
        # Agregar los números
        for fila in numeros:
            carton_texto += "{}  {}  {}   {}   {}\n".format(*fila)
        return carton_texto
    except Exception as e:
        return f"Error al leer el cartón: {str(e)}"

def enviar_carton(telefono, contenido_carton, carton_id):
    """Envía un cartón individual por WhatsApp.
    Args:
        telefono: Número de teléfono del destinatario
        contenido_carton: Contenido del cartón en formato markdown
        carton_id: Identificador del cartón
    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    try:
        # Formatear el cartón para WhatsApp
        mensaje = leer_carton_desde_texto(contenido_carton, carton_id)
        
        # Obtener la hora actual
        now = datetime.now()
        
        # Limpiar el número de teléfono
        numero = telefono.replace('+57', '').replace(' ', '').replace('-', '')
        
        # Calcular tiempo de envío con margen de 2 minutos
        tiempo_envio = now + timedelta(minutes=2)
        nueva_hora = tiempo_envio.hour
        nuevos_minutos = tiempo_envio.minute
        
        # Ajustar si los minutos superan 60
        if nuevos_minutos >= 60:
            nueva_hora = (nueva_hora + 1) % 24
            nuevos_minutos = nuevos_minutos % 60
        
        # Enviar mensaje
        pywhatkit.sendwhatmsg(
            f"+57{numero}",
            mensaje,
            nueva_hora,
            nuevos_minutos,
            wait_time=30,
            tab_close=True
        )
        
        return True
        
    except Exception as e:
        print(f"Error al enviar cartón {carton_id}: {str(e)}")
        return False

def leer_carton_desde_texto(contenido, nombre_carton):
    """Convierte el contenido markdown de un cartón en formato de texto para WhatsApp.
    Args:
        contenido: Contenido del cartón en formato markdown
        nombre_carton: Nombre/identificador del cartón
    """
    try:
        # Convertir el formato markdown a un formato más amigable para WhatsApp
        lineas = [linea for linea in contenido.split('\n') if linea.strip() and ':-:' not in linea]
        
        # Extraer los números del cartón
        numeros = []
        for linea in lineas[1:]:
            if '|' in linea:
                fila = [num.strip() for num in linea.split('|')[1:-1]]
                numeros.append(fila)
        
        # Formatear el mensaje
        carton_texto = "*Bingo JD*\n"
        carton_texto += f"Cartón: {nombre_carton}\n\n"
        carton_texto += "🎯 *CARTÓN DE BINGO* 🎯\n\n\n"
        carton_texto += " B     I     N    G     O\n"
        
        # Agregar los números
        for fila in numeros:
            carton_texto += "{}  {}  {}   {}   {}\n".format(*fila)
        return carton_texto
    except Exception as e:
        return f"Error al formatear el cartón: {str(e)}"

def enviar_cartones():
    """Envía los cartones por WhatsApp a los números registrados."""
    try:
        # Leer el archivo de datos
        with open('datos_bingo.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Cargar estado de envío
        try:
            with open('estado_envio.json', 'r', encoding='utf-8') as f:
                estado_envio = json.load(f)
        except FileNotFoundError:
            estado_envio = {}
        
        mensajes_enviados = 0
        errores = []
        
        # Procesar cada cartón no enviado
        for clave, telefono in datos.items():
            # Verificar si el cartón ya fue enviado
            if estado_envio.get(clave) == "✅":
                continue
                
            try:
                archivo_carton = f"cartones/{clave}.md"
                if not os.path.exists(archivo_carton):
                    errores.append(f"No se encontró el cartón para {clave}")
                    continue
                
                # Leer contenido del cartón
                with open(archivo_carton, 'r', encoding='utf-8') as f:
                    contenido_carton = f.read()
                
                # Enviar cartón
                if enviar_carton(telefono, contenido_carton, clave):
                    mensajes_enviados += 1
                    estado_envio[clave] = "✅"
                    time.sleep(10)  # Esperar entre envíos
                else:
                    errores.append(f"Error al enviar cartón {clave}")
                    
            except Exception as e:
                errores.append(f"Error al procesar cartón {clave}: {str(e)}")
        
        # Guardar estado de envío actualizado
        with open('estado_envio.json', 'w', encoding='utf-8') as f:
            json.dump(estado_envio, f, indent=4)
        
        # Preparar mensaje de resultado
        resultado = f"Se enviaron {mensajes_enviados} cartones exitosamente."
        if errores:
            resultado += f"\n\nErrores ({len(errores)}):\n" + "\n".join(errores)
        
        return True, resultado
        
    except Exception as e:
        return False, f"Error general: {str(e)}"
