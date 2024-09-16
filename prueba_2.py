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
def obtener_representantes_lista_1():
    conexion = connect_to_db()
    cursor = conexion.cursor()
    
    query = "SELECT id, nombre, cargo FROM representantes_lista_1"
    cursor.execute(query)
    representantes = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return representantes

def obtener_representantes_lista_2():
    conexion = connect_to_db()
    cursor = conexion.cursor()
    
    query = "SELECT id, nombre, cargo FROM representantes_lista_2"
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

# Función para mostrar la pantalla de votación con modo claro
def mostrar_votacion(page, votante_id, dialog):
    def votar(e):
        seleccionados = [c.data for c in checkbox_container_lista_1.controls + checkbox_container_lista_2.controls if c.value]
        
        # Validar que solo se haya seleccionado un representante por cargo
        cargos_seleccionados = set()
        for checkbox in checkbox_container_lista_1.controls + checkbox_container_lista_2.controls:
            if checkbox.value:
                cargo = obtener_cargo_por_id(checkbox.data)
                if cargo in cargos_seleccionados:
                    dialog.title = ft.Text("Error")
                    dialog.content = ft.Text(f"Solo puedes votar por un representante de cada cargo. El cargo '{cargo}' ya ha sido seleccionado.")
                    dialog.open = True
                    page.overlay.append(dialog)
                    page.update()
                    return
                cargos_seleccionados.add(cargo)
        
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
        
        page.overlay.append(dialog)
        page.update()
    
    # Definir colores para el modo claro
    bg_color = ft.colors.WHITE
    text_color = ft.colors.BLACK
    
    # Cargar los representantes
    representantes_lista_1 = obtener_representantes_lista_1()
    representantes_lista_2 = obtener_representantes_lista_2()
    
    # Crear los checkboxes para lista 1
    global checkbox_container_lista_1
    checkbox_container_lista_1 = ft.Column()
    for representante in representantes_lista_1:
        rep_id, rep_nombre, rep_cargo = representante
        checkbox_container_lista_1.controls.append(
            ft.Checkbox(
                label=f"{rep_nombre} - {rep_cargo}", 
                value=False, 
                data=rep_id
            )
        )
    
    # Crear los checkboxes para lista 2
    global checkbox_container_lista_2
    checkbox_container_lista_2 = ft.Column()
    for representante in representantes_lista_2:
        rep_id, rep_nombre, rep_cargo = representante
        checkbox_container_lista_2.controls.append(
            ft.Checkbox(
                label=f"{rep_nombre} - {rep_cargo}", 
                value=False, 
                data=rep_id
            )
        )
    
    # Añadir widgets a la página con estilos de modo claro
    page.add(
        ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("Lista 1:", color=text_color),
                    checkbox_container_lista_1
                ]),
                ft.Column([
                    ft.Text("Lista 2:", color=text_color),
                    checkbox_container_lista_2
                ])
            ]),
            bgcolor=bg_color  # Aplicar color de fondo
        ),
        ft.ElevatedButton("Votar", on_click=votar)  # El parámetro color ha sido eliminado
    )
    
    # Aplicar colores de fondo y texto a la página
    page.bgcolor = bg_color
    page.text_color = text_color
    page.update()

def obtener_cargo_por_id(rep_id):
    conexion = connect_to_db()
    cursor = conexion.cursor()
    
    query = """
    SELECT cargo FROM representantes_lista_1 WHERE id = %s
    UNION
    SELECT cargo FROM representantes_lista_2 WHERE id = %s
    """
    cursor.execute(query, (rep_id, rep_id))
    cargo = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    
    if cargo:
        return cargo[0]
    return None

# Interfaz de Login
def login_page(page: ft.Page):
    page.title = "Sistema de Votación - Login"
    
    dni_input = ft.TextField(label="Ingrese su DNI")
    dialog = ft.AlertDialog()
    
    def login(e):
        dni = dni_input.value
        if not dni:
            dialog.title = ft.Text("Error")
            dialog.content = ft.Text("Por favor, ingrese un DNI.")
            dialog.open = True
            page.overlay.append(dialog)
            page.update()
            return
        
        votante = verificar_login(dni)
        
        if votante:
            votante_id, nombre, apellido = votante
            dialog.title = ft.Text("Bienvenido")
            dialog.content = ft.Text(f"¡Bienvenido {nombre} {apellido}!")
            dialog.open = True
            page.overlay.append(dialog)
            page.update()
            
            # Limpiar la página y mostrar la pantalla de votación
            page.controls.clear()
            mostrar_votacion(page, votante_id, dialog)
        else:
            dialog.title = ft.Text("Error")
            dialog.content = ft.Text("DNI no encontrado. Verifique su información.")
            dialog.open = True
            page.overlay.append(dialog)
            page.update()
    
    login_button = ft.ElevatedButton("Login", on_click=login)
    
    page.add(
        dni_input,
        login_button
    )
    
    page.update()

# Crear y ejecutar la aplicación
def main(page: ft.Page):
    # Establecer colores de fondo y texto para toda la página
    page.bgcolor = ft.colors.WHITE
    page.text_color = ft.colors.BLACK
    login_page(page)

ft.app(target=main)