import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import jugadores
import generador_cartones
import whatsapp_sender
import os
import random
import subprocess
import json
import zipfile
import datetime

class VentanaJugador(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Añadir Jugador")
        self.geometry("400x300")
        
        # Crear y colocar widgets
        ttk.Label(self, text="Nombre:").pack(pady=5)
        self.nombre = ttk.Entry(self)
        self.nombre.pack(pady=5)
        
        ttk.Label(self, text="Número de Celular:").pack(pady=5)
        self.celular = ttk.Entry(self)
        self.celular.pack(pady=5)
        
        ttk.Label(self, text="Número de Cartones:").pack(pady=5)
        self.num_cartones = ttk.Entry(self)
        self.num_cartones.pack(pady=5)
        
        ttk.Button(self, text="Guardar", command=self.guardar_jugador).pack(pady=20)
    
    def guardar_jugador(self):
        try:
            nombre = self.nombre.get().strip()
            celular = self.celular.get().strip()
            num_cartones = int(self.num_cartones.get().strip())
            
            if not nombre or not celular or num_cartones <= 0:
                messagebox.showerror("Error", "Por favor complete todos los campos correctamente")
                return
                
            if not celular.isdigit():
                messagebox.showerror("Error", "El número de celular debe contener solo dígitos")
                return
            
            # Agregar jugador y sus cartones
            cartones_actualizados = jugadores.agregar_jugador(nombre, celular, num_cartones)
            
            # Actualizar la lista de comprobación
            try:
                import comprobar_carton
                comprobar_carton.generar_lista_comprobacion()
                print("Lista de comprobación actualizada exitosamente")
            except Exception as e:
                print(f"Error al actualizar la lista de comprobación: {str(e)}")
            
            messagebox.showinfo("Éxito", f"Se han registrado {num_cartones} cartones para {nombre}")
            self.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "El número de cartones debe ser un número entero positivo")

class VentanaEliminarJugador(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Eliminar Jugador")
        self.geometry("500x400")
        # Centrar la ventana
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label informativo
        ttk.Label(main_frame, text="Seleccione el jugador a eliminar:", 
                 font=("Helvetica", 10)).pack(pady=10)
        
        # Lista de jugadores
        # Frame para la lista con scroll
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lista de jugadores con scroll
        self.lista_jugadores = tk.Listbox(list_frame, width=50, height=15,
                                         yscrollcommand=scrollbar.set)
        self.lista_jugadores.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_jugadores.yview)
        self.lista_jugadores.pack(pady=10)
        
        # Botón eliminar
        ttk.Button(main_frame, text="Eliminar Jugador", 
                  command=self.eliminar_jugador_seleccionado).pack(pady=10)
        
        # Cargar jugadores
        self.cargar_jugadores()
    
    def cargar_jugadores(self):
        """Carga la lista de jugadores en el Listbox."""
        cartones = jugadores.obtener_cartones()
        for clave in cartones.keys():
            self.lista_jugadores.insert(tk.END, clave)
    
    def eliminar_jugador_seleccionado(self):
        """Elimina el jugador seleccionado."""
        seleccion = self.lista_jugadores.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un jugador")
            return
            
        clave_jugador = self.lista_jugadores.get(seleccion[0])
        
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar", 
            f"¿Está seguro de eliminar al jugador {clave_jugador}?\n\n" +
            "Esta acción eliminará:\n" +
            "1. El registro del jugador\n" +
            "2. Su cartón (si existe)\n" +
            "3. La entrada en la lista de comprobación\n" +
            "4. El registro de envío de WhatsApp"):
            return
            
        # Eliminar jugador
        exito, mensaje = jugadores.eliminar_jugador(clave_jugador)
        
        if exito:
            # Eliminar registro en estado_envio.json si existe
            try:
                with open('estado_envio.json', 'r', encoding='utf-8') as f:
                    estado_envio = json.load(f)
                
                # Eliminar el registro si existe
                if clave_jugador in estado_envio:
                    del estado_envio[clave_jugador]
                    
                    # Guardar el archivo actualizado
                    with open('estado_envio.json', 'w', encoding='utf-8') as f:
                        json.dump(estado_envio, f, indent=4)
            except FileNotFoundError:
                # Si el archivo no existe, no hay problema
                pass
            except Exception as e:
                print(f"Error al actualizar estado_envio.json: {str(e)}")
            
            self.lista_jugadores.delete(seleccion[0])
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showerror("Error", mensaje)

class BingoApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Bingo JD')
        self.root.geometry('800x600')

        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame izquierdo para botones
        self.left_frame = ttk.Frame(self.main_frame, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Frame derecho para imagen
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        self.title_label = ttk.Label(self.left_frame, text='Bienvenido al Bingo JD', font=('Helvetica', 14, 'bold'))
        self.title_label.pack(pady=20)

        # Botones
        buttons = [
            ('Añadir Jugadores', self.add_players),
            ('Eliminar Jugadores', self.delete_players),
            ('Ver Jugadores', self.ver_cartones),
            ('Generar Cartones', self.generate_cards),
            ('Generar Cartones img', self.generate_card_images),
            ('Enviar Cartones', self.send_cards),
            ('Jugar Bingo', self.play_bingo),
            ('Borrar Todo', self.borrar_todo)
        ]

        for text, command in buttons:
            btn = ttk.Button(self.left_frame, text=text, command=command)
            btn.pack(pady=10, fill=tk.X)

        # Cargar y mostrar la imagen
        try:
            # Cargar la imagen
            image = Image.open('imagen_bingo.jpeg')
            
            # Obtener las dimensiones del frame derecho
            self.right_frame.update()
            frame_width = self.right_frame.winfo_width()
            frame_height = self.right_frame.winfo_height()
            
            # Redimensionar la imagen manteniendo la proporción
            image.thumbnail((frame_width, frame_height), Image.Resampling.LANCZOS)
            
            # Convertir la imagen para tkinter
            self.photo = ImageTk.PhotoImage(image)
            
            # Mostrar la imagen
            self.image_label = ttk.Label(self.right_frame, image=self.photo)
            self.image_label.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f'Error al cargar la imagen: {e}')
            self.image_label = ttk.Label(self.right_frame, text='No se pudo cargar la imagen')
            self.image_label.pack(fill=tk.BOTH, expand=True)

    def add_players(self):
        VentanaJugador(self.root)
        
    def delete_players(self):
        VentanaEliminarJugador(self.root)

    def generate_cards(self):
        exito, mensaje = generador_cartones.generar_cartones()
        if exito:
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showerror("Error", mensaje)
            
    def generate_card_images(self):
        # Verificar si existen archivos markdown en el directorio de cartones
        cartones_dir = '/home/juandiego/Documentos/bingo/cartones'
        md_files = [f for f in os.listdir(cartones_dir) if f.endswith('.md')]
        
        if not md_files:
            messagebox.showerror("Error", "No hay cartones en formato markdown para convertir.")
            return
        
        # Ejecutar el script convertidor_imag.py
        try:
            result = subprocess.run(["python", "/home/juandiego/Documentos/bingo/convertidor_imag.py"], 
                                 capture_output=True, text=True, check=True)
            
            # Verificar la salida del script para determinar si fue exitoso
            if "exitosamente" in result.stdout:
                # Crear una ventana de diálogo para preguntar si se desean comprimir las imágenes
                if messagebox.askyesno("Conversión Exitosa", 
                                    "Los cartones han sido convertidos a imágenes exitosamente.\n\n" +
                                    "¿Deseas comprimir todas estas imágenes en un archivo ZIP?"):
                    # Comprimir las imágenes en un archivo ZIP
                    self.comprimir_imagenes(cartones_dir)
            else:
                messagebox.showinfo("Resultado", "Proceso completado. Revisa la terminal para más detalles.")
                
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error al convertir cartones: {str(e)}\n\nSalida de error: {e.stderr}")
            
    def comprimir_imagenes(self, cartones_dir):
        # Obtener la fecha actual para el nombre del archivo
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Crear nombre del archivo ZIP
        zip_filename = f"{cartones_dir}/cartones_img_{fecha_actual}.zip"
        
        # Lista para almacenar los archivos PNG
        png_files = [f for f in os.listdir(cartones_dir) if f.endswith('.png')]
        
        if not png_files:
            messagebox.showerror("Error", "No se encontraron imágenes PNG para comprimir.")
            return
        
        try:
            # Crear archivo ZIP
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for png_file in png_files:
                    png_path = os.path.join(cartones_dir, png_file)
                    zipf.write(png_path, arcname=png_file)
            
            # Preguntar si se desean eliminar las imágenes originales
            if messagebox.askyesno("Compresión Exitosa", 
                                "Las imágenes han sido comprimidas exitosamente.\n\n" +
                                f"Archivo creado: {zip_filename}\n\n" +
                                "¿Deseas eliminar las imágenes PNG originales?"):
                # Eliminar las imágenes originales
                for png_file in png_files:
                    png_path = os.path.join(cartones_dir, png_file)
                    os.remove(png_path)
                messagebox.showinfo("Completado", "Las imágenes originales han sido eliminadas.")
            
            messagebox.showinfo("Éxito", f"Proceso completado. Archivo ZIP creado: {zip_filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al comprimir las imágenes: {str(e)}")

    def send_cards(self):
        # Confirmar antes de enviar
        if messagebox.askyesno("Confirmar", "¿Estás seguro de enviar los cartones por WhatsApp? \n\nAsegúrate de:\n1. Tener WhatsApp Web abierto\n2. Tener una buena conexión a internet"):
            print("\nIniciando envío de cartones...")
            
            # Cargar estado de envío
            try:
                with open('estado_envio.json', 'r', encoding='utf-8') as f:
                    estado_envio = json.load(f)
            except FileNotFoundError:
                estado_envio = {}
            
            # Cargar datos de jugadores
            try:
                with open('datos_bingo.json', 'r', encoding='utf-8') as f:
                    datos_jugadores = json.load(f)
            except FileNotFoundError:
                messagebox.showerror("Error", "No hay jugadores registrados")
                return
            
            # Obtener lista de cartones no enviados
            cartones_no_enviados = []
            for archivo in os.listdir('cartones'):
                if archivo.endswith('.md'):
                    clave = archivo[:-3]  # Quitar la extensión .md
                    if estado_envio.get(clave, "x") == "x" and clave in datos_jugadores:
                        cartones_no_enviados.append(clave)
            
            if not cartones_no_enviados:
                messagebox.showinfo("Información", "No hay cartones pendientes por enviar")
                return
            
            # Enviar cartones no enviados
            mensajes_enviados = 0
            errores = []
            total_cartones = len(cartones_no_enviados)
            
            print(f"\nIniciando envío de {total_cartones} cartones...")
            
            for i, carton_id in enumerate(cartones_no_enviados):
                try:
                    # Mostrar progreso en la terminal
                    print(f"Enviando cartón {i+1}/{total_cartones}: {carton_id}")
                    
                    # Obtener número de teléfono del jugador
                    telefono = datos_jugadores[carton_id]
                    
                    # Leer contenido del cartón
                    with open(f'cartones/{carton_id}.md', 'r', encoding='utf-8') as f:
                        contenido_carton = f.read()
                    
                    # Enviar cartón por WhatsApp
                    if whatsapp_sender.enviar_carton(telefono, contenido_carton, carton_id):
                        # Marcar como enviado
                        estado_envio[carton_id] = "✅"
                        mensajes_enviados += 1
                        print(f"✅ Cartón {carton_id} enviado exitosamente ({i+1}/{total_cartones})")
                    else:
                        errores.append(f"No se pudo enviar el cartón {carton_id}")
                        print(f"❌ Error al enviar cartón {carton_id} ({i+1}/{total_cartones})")
                except Exception as e:
                    errores.append(f"Error al enviar cartón {carton_id}: {str(e)}")
                    print(f"❌ Error al enviar cartón {carton_id} ({i+1}/{total_cartones}): {str(e)}")
            
            # Guardar estado de envío actualizado
            with open('estado_envio.json', 'w', encoding='utf-8') as f:
                json.dump(estado_envio, f, indent=4)
            
            # Actualizar la lista de comprobación
            from comprobar_carton import generar_lista_comprobacion
            generar_lista_comprobacion()
            
            # Mostrar resumen en la terminal
            print(f"\n===== RESUMEN DE ENVÍO =====")
            print(f"Total de cartones: {total_cartones}")
            print(f"Cartones enviados: {mensajes_enviados}")
            print(f"Cartones con error: {len(errores)}")
            if errores:
                print("\nErrores encontrados:")
                for error in errores:
                    print(f"- {error}")
            print("============================\n")
            
            # Mostrar resumen final
            if mensajes_enviados > 0:
                mensaje = f"Se enviaron {mensajes_enviados} cartones exitosamente."
                if errores:
                    mensaje += "\n\nErrores encontrados:\n" + "\n".join(errores)
                messagebox.showinfo("Resumen de envío", mensaje)
            elif errores:
                mensaje = "No se pudo enviar ningún cartón.\n\nErrores encontrados:\n" + "\n".join(errores)
                messagebox.showerror("Error", mensaje)

    def play_bingo(self):
        # Verificar que haya jugadores
        cartones = jugadores.obtener_cartones()
        if not cartones:
            messagebox.showerror("Error", "No hay jugadores registrados.\n\nAntes de jugar el bingo, debes:\n1. Añadir jugadores\n2. Generar sus cartones\n3. Enviar los cartones por WhatsApp")
            return
        
        # Verificar que todos los cartones estén enviados
        try:
            with open('comprobar_carton.md', 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            cartones_no_enviados = []
            for linea in lineas[4:]:  # Saltar el encabezado y la línea de separación
                if '|' in linea:
                    partes = [p.strip() for p in linea.split('|')[1:-1]]
                    if len(partes) >= 3:
                        usuario = partes[0].strip()
                        id_carton = partes[1].strip()
                        tiene_carton = partes[2].strip() == '✅'
                        if not tiene_carton:
                            cartones_no_enviados.append(f"{usuario}_{id_carton}")
            
            if cartones_no_enviados:
                mensaje = "Hay cartones pendientes por enviar:\n\n"
                for carton in cartones_no_enviados:
                    mensaje += f"- {carton}\n"
                mensaje += "\nAntes de jugar el bingo, debes enviar todos los cartones por WhatsApp."
                messagebox.showerror("Error", mensaje)
                return
            
            # Si pasó todas las verificaciones, iniciar el juego
            VentanaJuegoBingo(self.root)
            
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el archivo de verificación de cartones.\n\nAntes de jugar el bingo, debes:\n1. Añadir jugadores\n2. Generar sus cartones\n3. Enviar los cartones por WhatsApp")
            return
        
    def ver_cartones(self):
        cartones = jugadores.obtener_cartones()
        if not cartones:
            messagebox.showinfo("Cartones", "No hay cartones registrados todavía")
            return
            
        # Crear una nueva ventana para mostrar los cartones
        ventana = tk.Toplevel(self.root)
        ventana.title("Jugadores Registrados")
        ventana.geometry("600x400")
        
        # Crear un widget Text con scroll
        frame = ttk.Frame(ventana)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, width=60, height=20)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insertar la información de los cartones
        text_widget.insert(tk.END, "Jugadores Registrados:\n\n")
        for clave, telefono in cartones.items():
            nombre_num = clave.split('_')[0]
            id_carton = clave.split('_')[1]
            text_widget.insert(tk.END, f"Cartón: {nombre_num}\n")
            text_widget.insert(tk.END, f"ID: {id_carton}\n")
            text_widget.insert(tk.END, f"Teléfono: {telefono}\n\n")
        
        text_widget.configure(state='disabled')  # Hacer el texto de solo lectura
        
        # También mostrar en consola
        print("\nJugadores registrados:")
        for clave, telefono in cartones.items():
            print(f"Clave: {clave} -> Teléfono: {telefono}")

    def borrar_todo(self):
        """
        Borra todos los archivos en el directorio cartones y limpia los archivos de datos
        datos_bingo.json y estado_envio.json
        """
        # Confirmar antes de borrar
        if messagebox.askyesno("Confirmar", "¿Estás seguro de borrar todos los datos?\n\nEsta acción eliminará:\n1. Todos los cartones generados\n2. Todos los jugadores registrados\n3. El estado de envío de cartones\n\nEsta acción no se puede deshacer."):
            try:
                # 1. Borrar todos los archivos en el directorio cartones
                cartones_dir = '/home/juandiego/Documentos/bingo/cartones'
                for archivo in os.listdir(cartones_dir):
                    ruta_archivo = os.path.join(cartones_dir, archivo)
                    if os.path.isfile(ruta_archivo):
                        os.remove(ruta_archivo)
                
                # 2. Limpiar datos_bingo.json (crear un archivo vacío con un diccionario)
                with open('/home/juandiego/Documentos/bingo/datos_bingo.json', 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
                
                # 3. Limpiar estado_envio.json (crear un archivo vacío con un diccionario)
                with open('/home/juandiego/Documentos/bingo/estado_envio.json', 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
                
                messagebox.showinfo("Éxito", "Todos los datos han sido borrados correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al borrar los datos: {str(e)}")

class VentanaSeleccionCarton(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Seleccionar Cartón")
        self.geometry("400x200")
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Label
        ttk.Label(main_frame, text="Buscar cartón:").pack(pady=5)
        
        # Entry para filtrar
        self.filtro_var = tk.StringVar()
        self.filtro_var.trace('w', self.filtrar_cartones)
        self.entry_filtro = ttk.Entry(main_frame, textvariable=self.filtro_var)
        self.entry_filtro.pack(pady=5, fill=tk.X)
        
        # Combobox para cartones
        self.combo_cartones = ttk.Combobox(main_frame, state='readonly')
        self.combo_cartones.pack(pady=10, fill=tk.X)
        
        # Botón Siguiente
        ttk.Button(main_frame, text="Siguiente", command=self.mostrar_verificacion).pack(pady=10)
        
        # Cargar cartones
        self.cargar_cartones()
        
        # Asegurarse de que esta ventana sea modal
        self.transient(parent)
        self.grab_set()
    
    def cargar_cartones(self):
        cartones_dir = os.path.join(os.getcwd(), 'cartones')
        self.cartones = [f.split('.')[0] for f in os.listdir(cartones_dir) if f.endswith('.md')]
        self.combo_cartones['values'] = self.cartones
        if self.cartones:
            self.combo_cartones.set(self.cartones[0])
    
    def filtrar_cartones(self, *args):
        filtro = self.filtro_var.get().lower()
        cartones_filtrados = [c for c in self.cartones if c.lower().startswith(filtro)]
        self.combo_cartones['values'] = cartones_filtrados
        if cartones_filtrados:
            self.combo_cartones.set(cartones_filtrados[0])
    
    def mostrar_verificacion(self):
        carton_seleccionado = self.combo_cartones.get()
        if carton_seleccionado:
            # Crear la ventana de verificación usando el parent original
            verificacion = VentanaVerificacionBingo(self.parent, carton_seleccionado)
            # Liberar el control de eventos
            self.grab_release()
            self.destroy()
            # Hacer la nueva ventana modal
            verificacion.transient(self.parent)
            verificacion.grab_set()

class VentanaVerificacionBingo(tk.Toplevel):
    def __init__(self, parent, carton_id):
        super().__init__(parent)
        self.title("Verificar Bingo")
        self.geometry("400x500")
        
        # Centrar la ventana
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo = ttk.Label(main_frame, text=carton_id, font=('Arial', 14, 'bold'))
        titulo.pack(pady=(0, 20))
        
        # Text widget para mostrar la tabla
        self.text = tk.Text(main_frame, width=30, height=15, font=('Courier', 12))
        self.text.pack(pady=10)
        self.text.tag_configure('center', justify='center')
        self.text.tag_configure('tachado', foreground='red', overstrike=1)
        self.text.tag_configure('header', font=('Courier', 12, 'bold'))
        
        # Cargar contenido del cartón
        self.cargar_carton(carton_id)
        
        # Frame para botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        # Botones
        ttk.Button(btn_frame, text="Correcto", command=self.bingo_correcto).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Incorrecto", command=self.bingo_incorrecto).pack(side=tk.LEFT, padx=10)
    
    def cargar_carton(self, carton_id):
        cartones_jugando = os.path.join(os.getcwd(), 'cartonesjugando.md')
        try:
            with open(cartones_jugando, 'r', encoding='utf-8') as f:
                contenido = f.read()
                # Buscar la sección del cartón
                inicio = contenido.find(f'## {carton_id}')
                if inicio != -1:
                    fin = contenido.find('##', inicio + 1)
                    if fin == -1:
                        fin = len(contenido)
                    carton_contenido = contenido[inicio:fin].strip()
                    
                    # Extraer los números de la tabla
                    numeros = []
                    lineas = carton_contenido.split('\n')
                    for linea in lineas:
                        if '|' in linea and not ':-:' in linea:
                            # Obtener solo los números de la línea
                            celdas = [c.strip() for c in linea.split('|')[1:-1]]
                            if celdas and all(c.strip() for c in celdas):  # Ignorar líneas vacías
                                numeros.append(celdas)
                    
                    # Limpiar el Text widget
                    self.text.delete('1.0', tk.END)
                    
                    # Añadir encabezado
                    self.text.insert(tk.END, "  B   I   N   G   O\n", 'header')
                    self.text.insert(tk.END, "-" * 30 + "\n", 'center')
                    
                    # Añadir números
                    for fila in numeros:
                        linea = ""
                        for celda in fila:
                            # Dar formato a cada número para que ocupe 4 espacios
                            if '~~[' in celda:
                                num = celda.replace('~~[', '').replace(']~~', '')
                                num = num.rjust(4)
                                self.text.insert(tk.END, num, 'tachado')
                            else:
                                num = celda.rjust(4)
                                self.text.insert(tk.END, num)
                        self.text.insert(tk.END, "\n")
                    
                    # Hacer el texto no editable
                    self.text.configure(state='disabled')
                    
        except Exception as e:
            print(f"Error al cargar el cartón: {e}")
    
    def bingo_correcto(self):
        comando = f'source {os.path.expanduser("~")}/.zshrc && hablar "El Bingo ha sido correcto, ¡felicitaciones al ganador!"'
        subprocess.Popen(comando, shell=True, executable='/bin/zsh')
        self.destroy()
    
    def bingo_incorrecto(self):
        comando = f'source {os.path.expanduser("~")}/.zshrc && hablar "El bingo no es válido, seguimos jugando"'
        subprocess.Popen(comando, shell=True, executable='/bin/zsh')
        self.destroy()

class VentanaJuegoBingo(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Jugar Bingo")
        self.geometry("800x600")
        
        # Lista de números disponibles (1-75)
        self.numeros_disponibles = list(range(1, 76))
        # Lista de números que han salido
        self.numeros_sacados = []
        # Estilo para los botones marcados
        self.style = ttk.Style()
        self.style.configure('Marcado.TButton', background='green', foreground='white')
        
        # Centrar la ventana
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame izquierdo para la cuadrícula de números
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame derecho para los botones
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        
        # Título BINGO
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Letras BINGO
        letras = ['B', 'I', 'N', 'G', 'O']
        letra_frames = {}
        
        for letra in letras:
            frame = ttk.Frame(title_frame)
            frame.pack(side=tk.LEFT, expand=True)
            ttk.Label(frame, text=letra, font=("Helvetica", 24, "bold")).pack()
            letra_frames[letra] = frame
        
        # Cuadrícula de números
        self.numeros_frames = {}
        rangos = {
            'B': (1, 15),
            'I': (16, 30),
            'N': (31, 45),
            'G': (46, 60),
            'O': (61, 75)
        }
        
        for letra, (inicio, fin) in rangos.items():
            frame = ttk.Frame(left_frame)
            frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            
            for num in range(inicio, fin + 1):
                btn = ttk.Button(frame, text=str(num), width=4)
                btn.pack(pady=2)
                self.numeros_frames[num] = btn
        
        # Frame para mostrar la balota actual
        self.balota_frame = ttk.Frame(right_frame)
        self.balota_frame.pack(pady=20)
        self.balota_label = ttk.Label(self.balota_frame, text="", font=("Helvetica", 24, "bold"))
        self.balota_label.pack()
        
        # Botones de control
        botones = [
            ("Empezar", self.empezar_juego),
            ("Siguiente", self.siguiente_balota),
            ("Bingo", self.verificar_bingo),
            ("Reiniciar", self.reiniciar_juego)
        ]
        
        self.botones = {}
        for texto, comando in botones:
            btn = ttk.Button(right_frame, text=texto, command=comando, width=15)
            btn.pack(pady=10)
            self.botones[texto] = btn
            
        # Deshabilitar el botón Siguiente al inicio
        self.botones["Siguiente"].configure(state='disabled')
            
    def obtener_letra(self, numero):
        """Obtiene la letra correspondiente al número."""
        if 1 <= numero <= 15:
            return 'B'
        elif 16 <= numero <= 30:
            return 'I'
        elif 31 <= numero <= 45:
            return 'N'
        elif 46 <= numero <= 60:
            return 'G'
        else:
            return 'O'
    
    def procesar_balota(self, numero):
        """Procesa una balota: la muestra, marca y actualiza los cartones."""
        # Obtener letra correspondiente
        letra = self.obtener_letra(numero)
        
        # Mostrar balota
        texto_balota = f"{letra}{numero}"
        self.balota_label.configure(text=texto_balota)
        
        # Marcar el número en la cuadrícula
        self.numeros_frames[numero].configure(style='Marcado.TButton')
        
        # Añadir el número a la lista de sacados
        if numero not in self.numeros_sacados:
            self.numeros_sacados.append(numero)
        
        # Crear/Actualizar archivo cartonesjugando.md con todos los cartones
        cartones_dir = os.path.join(os.getcwd(), 'cartones')
        cartones_jugando = os.path.join(os.getcwd(), 'cartonesjugando.md')
        
        contenido_final = ""
        
        # Iterar sobre todos los archivos .md en el directorio cartones
        for filename in os.listdir(cartones_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(cartones_dir, filename)
                # Obtener el nombre sin extensión para el subtítulo
                nombre = os.path.splitext(filename)[0]
                
                # Leer el contenido del archivo
                with open(file_path, 'r', encoding='utf-8') as f_in:
                    contenido = f_in.read()
                
                # Tachar todos los números que han salido
                for num in self.numeros_sacados:
                    num_str = f"{num:02d}"
                    contenido = contenido.replace(f"| {num_str} ", f"| ~~[{num_str}]~~ ")
                    contenido = contenido.replace(f"|{num_str} ", f"|~~[{num_str}]~~ ")
                    contenido = contenido.replace(f" {num_str}|", f" ~~[{num_str}]~~|")
                    contenido = contenido.replace(f"{num_str}|", f"~~[{num_str}]~~|")
                
                # Añadir al contenido final
                contenido_final += f'## {nombre}\n'
                contenido_final += f'{contenido}\n\n'
        
        # Escribir todo el contenido actualizado
        with open(cartones_jugando, 'w', encoding='utf-8') as f_out:
            f_out.write(contenido_final)
        
        # Ejecutar comando para hablar la balota
        home = os.path.expanduser('~')
        comando = f'source {home}/.zshrc && hablar "{letra},{numero}"'
        subprocess.Popen(comando, shell=True, executable='/bin/zsh')

    def empezar_juego(self):
        """Inicia el juego sacando una balota al azar."""
        if not self.numeros_disponibles:
            messagebox.showinfo("Fin del Juego", "Ya se han sacado todas las balotas")
            return
            
        # Deshabilitar botón Empezar y habilitar Siguiente
        self.botones["Empezar"].configure(state='disabled')
        self.botones["Siguiente"].configure(state='normal')
        
        # Elegir número al azar
        numero = random.choice(self.numeros_disponibles)
        self.numeros_disponibles.remove(numero)
        
        # Procesar la balota
        self.procesar_balota(numero)

    def siguiente_balota(self):
        """Saca la siguiente balota al azar."""
        if not self.numeros_disponibles:
            messagebox.showinfo("Fin del Juego", "Ya se han sacado todas las balotas")
            self.botones["Siguiente"].configure(state='disabled')
            return
            
        # Elegir número al azar
        numero = random.choice(self.numeros_disponibles)
        self.numeros_disponibles.remove(numero)
        
        # Procesar la balota
        self.procesar_balota(numero)
        
    def verificar_bingo(self):
        """Inicia el proceso de verificación de bingo."""
        # Anunciar que han cantado bingo
        comando = f'source {os.path.expanduser("~")}/.zshrc && hablar "Han cantado Bingo!"'
        subprocess.Popen(comando, shell=True, executable='/bin/zsh')
        
        # Mostrar ventana de selección de cartón
        VentanaSeleccionCarton(self)
        
    def reiniciar_juego(self):
        """Reinicia el juego al estado inicial."""
        # Preguntar confirmación
        if messagebox.askyesno("Reiniciar Juego", "¿Estás seguro de que quieres reiniciar el juego? Se perderá el progreso actual."):
            # Reiniciar números disponibles y sacados
            self.numeros_disponibles = list(range(1, 76))
            self.numeros_sacados = []
            
            # Limpiar la balota actual
            self.balota_label.configure(text="")
            
            # Reiniciar todos los botones de números
            for btn in self.numeros_frames.values():
                btn.configure(style='TButton')
            
            # Reiniciar estados de botones
            self.botones["Empezar"].configure(state='normal')
            self.botones["Siguiente"].configure(state='disabled')
            
            # Restaurar cartonesjugando.md desde cartones.md
            cartones_jugando = os.path.join(os.getcwd(), 'cartonesjugando.md')
            cartones_original = os.path.join(os.getcwd(), 'cartones.md')
            
            try:
                # Copiar el contenido original
                with open(cartones_original, 'r', encoding='utf-8') as f_original:
                    contenido_original = f_original.read()
                with open(cartones_jugando, 'w', encoding='utf-8') as f_jugando:
                    f_jugando.write(contenido_original)
                
                # Anunciar reinicio
                subprocess.run(['zsh', '-c', 'hablar "El juego ha sido reiniciado"'])
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al reiniciar el juego: {e}")


if __name__ == '__main__':
    root = tk.Tk()
    app = BingoApp(root)
    root.mainloop()
