import random
import os
import json

def generar_numeros_columna(inicio, fin, cantidad=5):
    """Genera números aleatorios únicos para una columna."""
    return sorted(random.sample(range(inicio, fin + 1), cantidad))

def obtener_numeros_carton(contenido):
    """Extrae los números de un cartón en formato markdown y los retorna como una lista."""
    numeros = []
    lineas = contenido.split('\n')
    for linea in lineas[2:7]:  # Saltar encabezado y línea de separación
        if '|' in linea:
            nums = [n.strip() for n in linea.split('|')[1:-1]]
            for num in nums:
                if num != "JD":
                    numeros.append(int(num))
    return sorted(numeros)

def carton_es_unico(nuevo_carton, directorio_cartones):
    """Verifica si un cartón es único comparándolo con los existentes."""
    numeros_nuevo = obtener_numeros_carton(nuevo_carton)
    
    # Verificar cada cartón existente
    for archivo in os.listdir(directorio_cartones):
        if archivo.endswith('.md'):
            ruta_carton = os.path.join(directorio_cartones, archivo)
            with open(ruta_carton, 'r', encoding='utf-8') as f:
                contenido = f.read()
                numeros_existente = obtener_numeros_carton(contenido)
                if numeros_nuevo == numeros_existente:
                    return False
    return True

def generar_carton_bingo():
    """Genera un cartón de bingo con números aleatorios en el formato especificado."""
    max_intentos = 100  # Límite de intentos para evitar bucle infinito
    intentos = 0
    
    while intentos < max_intentos:
        # Generar números para cada columna
        b = generar_numeros_columna(1, 15)
        i = generar_numeros_columna(16, 30)
        n = generar_numeros_columna(31, 45)
        g = generar_numeros_columna(46, 60)
        o = generar_numeros_columna(61, 75)
        
        # Reemplazar el número central por "JD"
        n[2] = "JD"
        
        # Formatear números a dos dígitos
        def format_num(num):
            if isinstance(num, str):  # Para el caso de "JD"
                return num
            return f"{num:02d}"  # Formatear números a dos dígitos
        
        b = [format_num(num) for num in b]
        i = [format_num(num) for num in i]
        n = [format_num(num) if isinstance(num, int) else num for num in n]  # Preservar "JD"
        g = [format_num(num) for num in g]
        o = [format_num(num) for num in o]
        
        # Crear el contenido del archivo markdown
        contenido = "|  B  |  I  |  N  |  G  |  O  |\n"
        contenido += "| :-: | :-: | :-: | :-: | :-: |\n"
        
        # Generar las filas
        for fila in range(5):
            contenido += f"| {b[fila]} | {i[fila]} | {n[fila]} | {g[fila]} | {o[fila]} |\n"
        
        # Verificar si el cartón es único
        if not os.path.exists('cartones') or carton_es_unico(contenido, 'cartones'):
            return contenido
        
        intentos += 1
    
    raise Exception("No se pudo generar un cartón único después de varios intentos")

def leer_lista_comprobacion():
    """Lee la lista de comprobación y retorna un diccionario con el estado de cada cartón."""
    try:
        with open('comprobar_carton.md', 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        cartones_existentes = {}
        for linea in lineas[4:]:  # Saltar el encabezado y la línea de separación
            if '|' in linea:
                partes = [p.strip() for p in linea.split('|')[1:-1]]
                if len(partes) >= 3:
                    usuario = partes[0].strip()
                    id_carton = partes[1].strip()
                    tiene_carton = partes[2].strip() == '✅'  # ✅ es el emoji de marca de verificación
                    cartones_existentes[f"{usuario}_{id_carton}"] = tiene_carton
        return cartones_existentes
    except FileNotFoundError:
        return {}

def generar_cartones():
    """Lee el archivo datos_bingo.json y genera los cartones correspondientes."""
    try:
        # Leer el archivo datos_bingo.json
        with open('datos_bingo.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Leer la lista de comprobación
        cartones_existentes = leer_lista_comprobacion()
        
        # Crear directorio cartones si no existe
        os.makedirs('cartones', exist_ok=True)
        
        # Contadores
        cartones_generados = 0
        cartones_omitidos = 0
        errores = []
        
        # Generar un cartón para cada registro que no tenga uno
        for clave in datos.keys():
            if not cartones_existentes.get(clave, False):
                try:
                    # Intentar generar un cartón único
                    contenido = generar_carton_bingo()
                    
                    # Crear el archivo markdown
                    nombre_archivo = f"cartones/{clave}.md"
                    with open(nombre_archivo, 'w', encoding='utf-8') as f:
                        f.write(contenido)
                    cartones_generados += 1
                except Exception as e:
                    errores.append(f"Error al generar cartón para {clave}: {str(e)}")
            else:
                cartones_omitidos += 1
        
        # Generar mensaje de resultado
        mensaje = []
        if cartones_generados > 0:
            mensaje.append(f"Se generaron {cartones_generados} cartones nuevos")
        if cartones_omitidos > 0:
            mensaje.append(f"Se omitieron {cartones_omitidos} cartones existentes")
        if errores:
            mensaje.append("\n\nErrores encontrados:")
            mensaje.extend(errores)
        
        # Actualizar la lista de comprobación
        import comprobar_carton
        comprobar_carton.generar_lista_comprobacion()
        
        # Si hay errores pero se generaron algunos cartones, considerarlo éxito parcial
        if errores and cartones_generados == 0:
            return False, "\n".join(mensaje)
        else:
            return True, "\n".join(mensaje)
        
    except Exception as e:
        return False, f"Error al generar los cartones: {str(e)}"
