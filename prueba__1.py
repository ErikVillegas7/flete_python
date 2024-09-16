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

# Función para mostrar la pantalla de votación
def mostrar_votacion(page, votante_id):
    def votar(e):
        seleccionados = [c.data for c in checkbox_container.controls if c.value]
        
        if seleccionados:
            for rep_id in seleccionados:
                registrar_voto(votante_id, rep_id)
            
            dialog.title = ft.Text("Éxito")
            dialog.content = ft.Text("¡Voto registrado con éxito!")
            dialog.open = True
        else:
            dialog.title = ft.Text("Error")
            dialog.content = ft.Text("Debe seleccionar al menos un representante.")
            dialog.open = True
        page.dialog = dialog
        page.update()
    
    # Cargar los representantes
    representantes = obtener_representantes()
    
    # Crear los checkboxes
    checkbox_container.controls.clear()
    for representante in representantes:
        rep_id, rep_nombre, rep_cargo = representante
        checkbox_container.controls.append(
            ft.Checkbox(label=f"{rep_nombre} - {rep_cargo}", value=False, data=rep_id)
        )
    
    # Añadir widgets a la página
    page.add(
        ft.Text("Seleccione sus representantes:"),
        checkbox_container,
        ft.ElevatedButton("Votar", on_click=votar)
    )
    
    page.update()

# Interfaz de Login
def login_page(page: ft.Page):
    page.title = "Sistema de Votación - Login"
    
    dni_input = ft.TextField(label="Ingrese su DNI")
    login_button = ft.ElevatedButton("Login", on_click=lambda e: login(dni_input.value, page))
    dialog = ft.AlertDialog()
    
    page.add(
        dni_input,
        login_button
    )
    
    page.update()

# Función de Login
def login(dni, page):
    if not dni:
        dialog.title = ft.Text("Error")
        dialog.content = ft.Text("Por favor, ingrese un DNI.")
        dialog.open = True
        page.dialog = dialog
        page.update()
        return
    
    votante = verificar_login(dni)
    
    if votante:
        votante_id, nombre, apellido = votante
        dialog.title = ft.Text("Bienvenido")
        dialog.content = ft.Text(f"¡Bienvenido {nombre} {apellido}!")
        dialog.open = True
        page.dialog = dialog
        page.update()
        
        # Limpiar la página y mostrar la pantalla de votación
        page.controls.clear()
        mostrar_votacion(page, votante_id)
    else:
        dialog.title = ft.Text("Error")
        dialog.content = ft.Text("DNI no encontrado. Verifique su información.")
        dialog.open = True
        page.dialog = dialog
        page.update()

# Crear y ejecutar la aplicación
def main(page: ft.Page):
    login_page(page)

ft.app(target=main)