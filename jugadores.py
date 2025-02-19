import datetime
import json
import os

# Archivo para almacenar los datos
ARCHIVO_DATOS = 'datos_bingo.json'

# Diccionario para almacenar la información de los cartones
cartones = {}

# Cargar datos existentes si el archivo existe
def cargar_datos():
    global cartones
    try:
        if os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, 'r', encoding='utf-8') as archivo:
                cartones = json.load(archivo)
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        cartones = {}

# Guardar datos en el archivo
def guardar_datos():
    try:
        with open(ARCHIVO_DATOS, 'w', encoding='utf-8') as archivo:
            json.dump(cartones, archivo, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar los datos: {e}")

# Cargar datos al iniciar el módulo
cargar_datos()

def generar_id_carton(num_carton):
    """Genera un ID único para el cartón basado en la fecha y hora actual.
    Args:
        num_carton: Número del cartón (1-based) para este jugador
    Returns:
        ID en formato MMddHHmm seguido del número de cartón en dos dígitos
    """
    now = datetime.datetime.now()
    # Formatear el número de cartón a dos dígitos (01, 02, etc.)
    num_carton_str = f"{num_carton:02d}"
    return now.strftime("%m%d%H%M") + num_carton_str

def agregar_jugador(nombre, celular, num_cartones):
    """Agrega un jugador con sus cartones al diccionario y guarda los datos."""
    for i in range(1, num_cartones + 1):
        id_carton = generar_id_carton(i)
        clave = f"{nombre}{i}_{id_carton}"
        cartones[clave] = f"+57{celular}"
    # Guardar los datos después de cada actualización
    guardar_datos()
    return cartones

def obtener_cartones():
    """Retorna el diccionario de cartones."""
    return cartones

def eliminar_jugador(clave_jugador):
    """Elimina un jugador y sus cartones asociados.
    
    Args:
        clave_jugador (str): La clave del jugador (formato: nombre_id)
        
    Returns:
        tuple: (bool, str) indicando éxito/fallo y mensaje
    """
    try:
        # 1. Eliminar del diccionario cartones
        if clave_jugador not in cartones:
            return False, "Jugador no encontrado"
            
        cartones.pop(clave_jugador)
        guardar_datos()
            
        # 2. Eliminar el cartón si existe
        carton_path = f"cartones/{clave_jugador}.md"
        if os.path.exists(carton_path):
            os.remove(carton_path)
            
        # 3. Actualizar la lista de comprobación
        import comprobar_carton
        comprobar_carton.generar_lista_comprobacion()
            
        return True, f"Jugador {clave_jugador} eliminado exitosamente"
    except Exception as e:
        return False, f"Error al eliminar jugador: {str(e)}"
