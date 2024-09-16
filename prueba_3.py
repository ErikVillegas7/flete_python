import flet as ft
import mysql.connector

# Conexión a la base de datos
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='12345678',
            database='sistema_votacion'
        )
        if connection.is_connected():
            print('Conexión exitosa')
            return connection
    except Exception as ex:
        print('Conexión errónea')
        print(ex)
        return None

# Función para verificar el login por DNI
def verificar_login(dni):
    conexion = connect_to_db()
    cursor = conexion.cursor()
    
    query = "SELECT id, nombre, apellido FROM votantes WHERE dni = %s"
    cursor.execute(query, (dni,))
    votante = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    
    if votante:
        return votante  # Devuelve los datos del votante
    return None

# Función para cargar los representantes desde la base de datos
def obtener_representantes():
    conexion = connect_to_db()
    cursor = conexion.cursor()
    
    query = "SELECT id, nombre, cargo FROM representantes"
    cursor.execute(query)
    representantes = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return representantes

# Función para registrar los votos
def registrar_voto(votante_id, representante_id):
    conexion = connect_to_db()
    cursor = conexion.cursor()
    
    query_voto = "INSERT INTO votos (votante_id, eleccion, opcion) VALUES (%s, 'Representante', %s)"
    cursor.execute(query_voto, (votante_id, representante_id))
    
    conexion.commit()
    cursor.close()
    conexion.close()

# Interfaz con Flet
def main(page: ft.Page):
    page.title = "Sistema de Votación - Login y Votación"
    
    # Campos de Login
    dni_input = ft.TextField(label="Ingrese su DNI")
    
    # Contenedor de Checkboxes para los representantes
    checkbox_container = ft.Column()
    
    # Cuadro de diálogo para mostrar mensajes
    dialog = ft.AlertDialog()
    
    def mostrar_dialog(title, content):
        dialog.title = ft.Text(title)
        dialog.content = ft.Text(content)
        dialog.open = True
        page.overlay.append(dialog)
        page.update()
    
    # Botón de Login
    def login(e):
        dni = dni_input.value
        
        # Verificar si el DNI fue ingresado
        if not dni:
            mostrar_dialog("Error", "Por favor, ingrese un DNI.")
            return
        
        votante = verificar_login(dni)
        
        if votante:
            votante_id, nombre, apellido = votante
            mostrar_dialog("Bienvenido", f"¡Bienvenido {nombre} {apellido}!")
            
            # Cargar los representantes
            representantes = obtener_representantes()
            
            # Crear un checkbox por cada representante
            checkbox_container.controls.clear()  # Limpiar los anteriores
            for representante in representantes:
                rep_id, rep_nombre, rep_cargo = representante
                checkbox_container.controls.append(
                    ft.Checkbox(label=f"{rep_nombre} - {rep_cargo}", value=False, data=rep_id)
                )
            
            page.update()
        else:
            mostrar_dialog("Error", "DNI no encontrado. Verifique su información.")
    
    # Función para registrar votos
    def votar(e):
        # Validar que al menos un representante fue seleccionado
        seleccionados = [c.data for c in checkbox_container.controls if c.value]
        
        if seleccionados:
            dni = dni_input.value
            votante_id = verificar_login(dni)[0]  # Obtener votante_id con el DNI ingresado
            for rep_id in seleccionados:
                registrar_voto(votante_id, rep_id)
            
            mostrar_dialog("Éxito", "¡Voto registrado con éxito!")
        else:
            mostrar_dialog("Error", "Debe seleccionar al menos un representante.")
    
    # Añadir widgets a la página
    page.add(
        dni_input,
        ft.ElevatedButton("Login", on_click=login),
        checkbox_container,
        ft.ElevatedButton("Votar", on_click=votar)
    )

# Ejecutar la aplicación
ft.app(target=main)