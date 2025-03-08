import json
import os

def cargar_estado_envio():
    """Carga el estado de envío de los cartones desde un archivo JSON."""
    try:
        with open('estado_envio.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error al cargar estado de envío: {e}")
        return {}

def cargar_estado_imagenes():
    """Carga el estado de generación de imágenes de los cartones desde un archivo JSON."""
    try:
        with open('estado_imagenes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error al cargar estado de imágenes: {e}")
        return {}

def guardar_estado_envio(estado):
    """Guarda el estado de envío de los cartones en un archivo JSON."""
    try:
        with open('estado_envio.json', 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar estado de envío: {e}")
        return False

def guardar_estado_imagenes(estado):
    """Guarda el estado de generación de imágenes de los cartones en un archivo JSON."""
    try:
        with open('estado_imagenes.json', 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar estado de imágenes: {e}")
        return False

def generar_lista_comprobacion():
    """Genera una lista de comprobación de cartones en formato markdown."""
    try:
        # Leer el archivo datos_bingo.json
        with open('datos_bingo.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Cargar estado de envío y estado de imágenes
        estado_envio = cargar_estado_envio()
        estado_imagenes = cargar_estado_imagenes()
        
        # Crear el contenido del archivo markdown
        contenido = "# Lista de Comprobación de Cartones\n\n"
        contenido += "| Usuario | ID | Estado | Enviado | Estado_Imag |\n"
        contenido += "|---------|----|---------|---------|-----------|\n"
        
        # Obtener lista de archivos en el directorio cartones
        archivos_cartones = os.listdir('cartones') if os.path.exists('cartones') else []
        
        # Verificar cada cartón en el directorio
        cartones_procesados = set()
        for archivo in archivos_cartones:
            if archivo.endswith('.md'):
                clave = archivo[:-3]  # Quitar la extensión .md
                cartones_procesados.add(clave)
                
                # Separar el nombre del usuario y el ID
                partes = clave.split('_')
                nombre = partes[0]
                id_carton = partes[1] if len(partes) > 1 else ''
                
                # Verificar si existe el cartón
                tiene_carton = "✅"
                
                # Verificar estado de envío
                enviado = estado_envio.get(clave, "x")
                
                # Verificar estado de generación de imagen
                estado_img = estado_imagenes.get(clave, "x")
                
                # Añadir la línea a la tabla
                contenido += f"| {nombre} | {id_carton} | {tiene_carton} | {enviado} | {estado_img} |\n"
        
        # Verificar usuarios en datos_bingo.json que no tienen cartón
        for clave in datos.keys():
            if clave not in cartones_procesados:
                partes = clave.split('_')
                nombre = partes[0]
                id_carton = partes[1] if len(partes) > 1 else ''
                contenido += f"| {nombre} | {id_carton} | ❌ | x | x |\n"
        
        # Guardar el archivo
        with open('comprobar_carton.md', 'w', encoding='utf-8') as f:
            f.write(contenido)
            
        return True, "Lista de comprobación generada exitosamente"
    except Exception as e:
        return False, f"Error al generar la lista de comprobación: {str(e)}"

if __name__ == "__main__":
    exito, mensaje = generar_lista_comprobacion()
    print(mensaje)
