import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import datetime
import numpy as np
import json


def extract_metadata(markdown_filename):
    """Extrae los metadatos (nombre e ID) a partir del nombre del archivo markdown.
    Se espera que el archivo tenga el formato '[nombre]_[ID].md'.
    Se extrae el nombre y, del ID (formato MMddhhmmss), se obtiene el mes y día para formar la fecha con el año actual.
    """
    import os
    meta = {}
    base = os.path.basename(markdown_filename)
    if base.endswith('.md'):
        base = base[:-3]
    parts = base.split('_')
    if len(parts) >= 2:
        meta['nombre'] = parts[0]
        meta['id'] = parts[1]
        if len(meta['id']) >= 4:
            MM = meta['id'][:2]
            dd = meta['id'][2:4]
            year = datetime.datetime.now().year
            meta['fecha'] = f"{MM}/{dd}/{year}"
        else:
            meta['fecha'] = "N/A"
    else:
        meta['nombre'] = "N/A"
        meta['id'] = "N/A"
        meta['fecha'] = "N/A"
    return meta


def extract_table(markdown_content):
    """Extrae la primera tabla en formato markdown.
    Busca líneas que comienzan con '|' y asume que la primera es la cabecera y la segunda es separador.
    """
    lines = markdown_content.split('\n')
    table_lines = []
    for line in lines:
        if line.strip().startswith('|'):
            table_lines.append(line)
        elif table_lines:
            break

    if len(table_lines) < 2:
        return None, None

    header = [cell.strip() for cell in table_lines[0].strip().strip('|').split('|')]
    rows = []
    for row_line in table_lines[2:]:
        if row_line.strip() == '':
            continue
        row = [cell.strip() for cell in row_line.strip().strip('|').split('|')]
        rows.append(row)
    return header, rows


def render_table_with_metadata(header, rows, meta, output_file):
    """Renderiza la tabla con metadatos usando matplotlib.
    Agrega un título centrado y en la parte superior muestra el nombre, el ID y la fecha.
    La tabla se posiciona pegada al margen izquierdo y elevada.
    Se agrega una imagen de fondo que cubre toda la figura con una transparencia del 80%.
    """
    import matplotlib.image as mpimg
    
    # Crear la figura
    fig = plt.figure(figsize=(6, 6))
    
    # Eje para la imagen de fondo
    bg_ax = fig.add_axes([0, 0, 1, 1], zorder=0)
    bg_ax.axis('off')
    
    # Cargar y mostrar la imagen de fondo con transparencia incorporada
    bg_img = mpimg.imread('/home/juandiego/Documentos/bingo/imagen_bingo.jpeg')
    # Aplicar transparencia del 80% (alpha=0.2 significa 20% de opacidad)
    bg_ax.imshow(bg_img, extent=[0, 1, 0, 1], aspect='auto', alpha=0.2, interpolation='bilinear')
    
    # Eje para el contenido
    content_ax = fig.add_axes([0, 0, 1, 1], zorder=1)
    content_ax.axis('off')
    
    # Título centrado (ajustado hacia arriba)
    fig.suptitle("Bienvenido al Bingo JD", fontsize=16, fontweight='bold', y=0.98)
    
    # Metadatos alineados a la izquierda
    meta_text = f"Nombre: {meta.get('nombre', 'N/A')}\nID: {meta.get('id', 'N/A')}\nFecha: {meta.get('fecha', 'N/A')}"
    fig.text(0.05, 0.92, meta_text, fontsize=14, va='top', ha='left')
    
    # Posicionar la tabla centrada, elevada, y aumentar el tamaño de fuente
    table_data = [header] + rows
    table = content_ax.table(cellText=table_data, cellLoc='center', bbox=[0.05, 0.2, 0.9, 0.6])
    
    # Dar formato a todas las celdas
    for (i, j), cell in table.get_celld().items():
        cell.set_fontsize(14)
        
        # Dar formato al encabezado (primera fila)
        if i == 0:
            cell.set_facecolor('cornflowerblue')  # Color de fondo azul para encabezado
            cell.set_text_props(color='white', fontweight='bold')
            
        # Identificar y dar formato a la celda central (JD)
        # La celda central típicamente está en la posición [3, 2] en un cartón de bingo estándar
        # (asumiendo que la tabla es 5x5 sin contar el encabezado)
        if len(rows) >= 5 and len(header) >= 5:  # Verificar que sea un cartón 5x5
            middle_row = 3  # Tercera fila (índice 3 contando el encabezado)
            middle_col = 2  # Columna central (índice 2 de 0-4)
            
            if i == middle_row and j == middle_col:
                cell.set_facecolor('red')  # Fondo rojo para celda central
                cell.set_text_props(color='white', fontweight='bold')  # Texto blanco y negrita
    
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()


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

def guardar_estado_imagenes(estado):
    """Guarda el estado de generación de imágenes de los cartones en un archivo JSON."""
    try:
        with open('estado_imagenes.json', 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar estado de imágenes: {e}")
        return False
        
def guardar_estado_envio(estado):
    """Guarda el estado de envío de los cartones en un archivo JSON."""
    try:
        with open('estado_envio.json', 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar estado de envío: {e}")
        return False

def actualizar_lista_comprobacion():
    """Actualiza la lista de comprobación de cartones."""
    try:
        import subprocess
        result = subprocess.run(["python", "/home/juandiego/Documentos/bingo/comprobar_carton.py"], 
                             capture_output=True, text=True)
        if "exitosamente" in result.stdout:
            print("Lista de comprobación actualizada exitosamente.")
            return True
        else:
            print(f"Error al actualizar la lista de comprobación: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error al ejecutar el script de comprobación: {e}")
        return False

def main():
    input_dir = '/home/juandiego/Documentos/bingo/cartones'
    output_dir = '/home/juandiego/Documentos/bingo/cartones/imagenes_de_los_cartones'
    
    # Lista para almacenar las imágenes generadas en esta sesión
    imagenes_generadas = []
    
    # Crear el directorio de salida si no existe
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Directorio creado: {output_dir}")
    except Exception as e:
        print(f"Error al crear el directorio de salida: {e}")
        return
        
    try:
        files = [f for f in os.listdir(input_dir) if f.endswith('.md')]
    except Exception as e:
        print(f"Error accediendo al directorio: {e}")
        return

    if not files:
        print("No se encontraron archivos markdown en el directorio.")
        return

    # Cargar el estado actual de las imágenes y envío
    estado_imagenes = cargar_estado_imagenes()
    estado_envio = cargar_estado_envio()
    
    # Filtrar los archivos para procesar solo los que tienen 'x' en Estado_Imag
    archivos_pendientes = []
    for md_file in files:
        carton_id = md_file[:-3]  # Quitar la extensión .md
        if carton_id in estado_imagenes and estado_imagenes[carton_id] == "x" or carton_id not in estado_imagenes:
            archivos_pendientes.append(md_file)
    
    if not archivos_pendientes:
        print("No hay cartones pendientes de generar imágenes.")
        return
        
    print(f"Se procesarán {len(archivos_pendientes)} cartones pendientes de generar imágenes.")
    
    # Contador para archivos procesados exitosamente
    successful = 0
    
    # Archivo para registrar las imágenes generadas en esta sesión
    try:
        with open('imagenes_recientes.json', 'w', encoding='utf-8') as f:
            json.dump([], f)  # Iniciar con lista vacía
    except Exception as e:
        print(f"Error al crear archivo de imágenes recientes: {e}")
    
    # Procesar solo los archivos pendientes
    for md_file in archivos_pendientes:
        input_file = os.path.join(input_dir, md_file)
        carton_id = md_file[:-3]  # Quitar la extensión .md
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error leyendo el archivo {md_file}: {e}")
            continue

        meta = extract_metadata(input_file)
        header, rows = extract_table(content)
        if header is None or not rows:
            print(f"No se encontró una tabla válida en el archivo {md_file}.")
            continue

        # Usar el directorio de salida para las imágenes
        output_file = os.path.join(output_dir, os.path.basename(input_file).replace('.md', '.png'))
        render_table_with_metadata(header, rows, meta, output_file)
        
        # Marcar como generado en el estado de imágenes
        estado_imagenes[carton_id] = "✅"
        
        # Marcar como enviado en el estado de envío
        estado_envio[carton_id] = "✅"
        
        # Agregar a la lista de imágenes generadas en esta sesión
        imagenes_generadas.append(os.path.basename(output_file))
        
        successful += 1
        print(f"Tabla convertida a imagen con metadatos: {output_file}")
    
    # Guardar el estado actualizado de imágenes
    if guardar_estado_imagenes(estado_imagenes):
        print("Estado de generación de imágenes actualizado exitosamente.")
    else:
        print("Error al guardar el estado de generación de imágenes.")
        
    # Guardar el estado actualizado de envío
    if guardar_estado_envio(estado_envio):
        print("Estado de envío actualizado exitosamente.")
    else:
        print("Error al guardar el estado de envío.")
    
    # Guardar la lista de imágenes generadas en esta sesión
    try:
        with open('imagenes_recientes.json', 'w', encoding='utf-8') as f:
            json.dump(imagenes_generadas, f, indent=4)
        print(f"Se han registrado {len(imagenes_generadas)} imágenes recientes en imagenes_recientes.json")
    except Exception as e:
        print(f"Error al guardar la lista de imágenes recientes: {e}")
    
    # Actualizar la lista de comprobación
    actualizar_lista_comprobacion()
    
    print(f"\nProceso completado. {successful} de {len(archivos_pendientes)} archivos fueron convertidos exitosamente.")


if __name__ == '__main__':
    main()
