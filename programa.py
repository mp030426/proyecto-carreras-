from pymongo import MongoClient
from pymongo.errors import OperationFailure
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
#conexion y usuarios
client = MongoClient("mongodb://localhost:27017/")
db = client["galgos"]
coleccion = {
    "perros": db["perros"],
    "carreras": db["carreras"],
    "dueños": db["dueños"],
    "cuidadores":db["cuidadores"]
}
estado_login={"logueado":False,"rol":None}
cliente_autenticado = None


#funciones de autenticacion de usuario
def login():
    if estado_login["logueado"]:
        return

    login_win = tk.Toplevel(menu)
    login_win.title("Iniciar sesión")

    tk.Label(login_win, text="Usuario").pack()
    entry_user = tk.Entry(login_win)
    entry_user.pack()

    tk.Label(login_win, text="Contraseña").pack()
    entry_pass = tk.Entry(login_win, show="*")
    entry_pass.pack()

    def autenticar():
        user = entry_user.get()
        pwd = entry_pass.get()

        posibles_bases = ["admin", "galgos"]
        usuario_encontrado = False

        for base_auth in posibles_bases:
            try:
                cliente = MongoClient(
                    host="localhost",
                    port=27017,
                    username=user,
                    password=pwd,
                    authSource=base_auth,
                    serverSelectionTimeoutMS=3000
                )

                cliente.admin.command("ping")  # fuerza la conexión

                # Buscamos al usuario en esta base
                resultado = cliente[base_auth].command("usersInfo", {"user": user, "db": base_auth})


                if not resultado['users']:
                    continue  # Usuario no está en esta base, probamos otra

                roles = resultado['users'][0]['roles']
                nombres_roles = [rol["role"] for rol in roles]

                estado_login["logueado"] = True

                if "root" in nombres_roles or "userAdminAnyDatabase" in nombres_roles:
                    estado_login["rol"] = "admin"
                elif "insertAndFindOnly" in nombres_roles:
                    estado_login["rol"] = "limitado"
                else:
                    estado_login["rol"] = "desconocido"

                messagebox.showinfo("Login exitoso", f"Bienvenido, {user} (rol: {estado_login['rol']})")
                global cliente_autenticado
                cliente_autenticado = cliente
                habilitar_botones()
                login_win.destroy()
                usuario_encontrado = True
                break

            except OperationFailure as e:
                continue  # Prueba con la siguiente base
            except Exception as e:
                messagebox.showerror("Error de conexión", str(e))
                return

        if not usuario_encontrado:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos, o sin permisos.")



    tk.Button(login_win, text="Ingresar", command=autenticar).pack(pady=10)

def habilitar_botones():
    for widget in menu.winfo_children():
        if isinstance(widget, ttk.Button):
            texto = widget.cget("text")
            if estado_login["rol"] == "admin":
                widget.config(state="normal")
            elif estado_login["rol"] == "limitado":
                if texto in ["🔍 Buscar", "➕ Agregar"]:
                    widget.config(state="normal")
                else:
                    widget.config(state="disabled")
            else:
                widget.config(state="disabled")
#funciones CRUD
def buscar():
    global cliente_autenticado

    if not estado_login["logueado"] or cliente_autenticado is None:
        messagebox.showerror("Error", "Debe iniciar sesión primero.")
        return

    def opcion_perro():
        def buscar_perro():
            nombre = nombre_perro.get().strip()
            origen = origen_perro.get().strip()
            edad = edad_perro.get().strip()
            color = color_perro.get().strip()


            filtro = {}
            if nombre:
                filtro["nombre"] = nombre
            if origen:
                filtro["origen"] = origen
            if edad:
                try:
                 filtro["edad"] = int(edad)
                except ValueError:
                    messagebox.showerror("Error", "La edad debe ser un número.")
                    return
            if color:
                filtro["color"] = color

            try:
                db = cliente_autenticado["galgos"]
                perros_col = db["perros"]
                resultados = list(perros_col.find(filtro))

                if not resultados:
                    messagebox.showinfo("Sin resultados", "No se encontraron perros con esos criterios.")
                    return

                resultado_ventana = tk.Toplevel(ventana)
                resultado_ventana.title("Resultados de búsqueda")

                for idx, perro in enumerate(resultados, start=1):
                    nombre_perro_db = perro.get("nombre", "")
                    origen_db = perro.get("origen", "")
                    edad_db = perro.get("edad", "")
                    color_db = perro.get("color", "")
                    # Buscar dueño y cuidador
                    dueño_id = perro.get('dueño_id')
                    cuidador_id = perro.get('cuidador_id')

                    nombre_dueño = "No registrado"
                    nombre_cuidador = "No registrado"

                    if dueño_id:
                        dueño = cliente_autenticado["galgos"]["dueños"].find_one({"_id": dueño_id})
                        if dueño:
                            nombre_dueño = dueño.get("nombre", "Sin nombre")

                    if cuidador_id:
                        cuidador = cliente_autenticado["galgos"]["cuidadores"].find_one({"_id": cuidador_id})
                        if cuidador:
                            nombre_cuidador = cuidador.get("nombre", "Sin nombre")
                    texto = (
                        f"{idx}. Nombre: {nombre_perro_db}, Origen: {origen_db}, Edad: {edad_db}, Color: {color_db},\n"
                        f"   Dueño: {nombre_dueño}, Cuidador: {nombre_cuidador}"
                    )
                    tk.Label(resultado_ventana, text=texto, justify="left", anchor="w", wraplength=500).pack(anchor="w", padx=10, pady=2)
                

            except Exception as e:
                messagebox.showerror("Error al buscar", str(e))

        ventana_perros = tk.Toplevel(ventana)
        ventana_perros.title("BUSCAR PERROS")

        tk.Label(ventana_perros, text="Nombre del perro:").pack(pady=5)
        nombre_perro = tk.Entry(ventana_perros)
        nombre_perro.pack(pady=5)

        tk.Label(ventana_perros, text="Origen del perro:").pack(pady=5)
        origen_perro = tk.Entry(ventana_perros)
        origen_perro.pack(pady=5)

        tk.Label(ventana_perros, text="Edad del perro:").pack(pady=5)
        edad_perro = tk.Entry(ventana_perros)
        edad_perro.pack(pady=5)

        tk.Label(ventana_perros, text="Color del perro:").pack(pady=5)
        color_perro = tk.Entry(ventana_perros)
        color_perro.pack(pady=5)

        tk.Button(ventana_perros, text="BUSCAR", command=buscar_perro).pack(pady=10)

    def opcion_dueño():
        def buscar_dueño():
            nombre=nombre_dueño.get().strip()
            telefono=telefono_dueño.get().strip()

            filtro = {}

            if nombre:
                filtro["nombre"] = nombre

            if telefono:
                filtro["telefono"] = telefono

            try:
                db = cliente_autenticado["galgos"]
                dueños_col = db["dueños"]
                perros_col = db["perros"]
                resultados = list(dueños_col.find(filtro))

                if not resultados:
                    messagebox.showinfo("Sin resultados", "No se encontraron dueños con esos criterios.")
                    return
                
                resultado_ventana = tk.Toplevel(ventana)
                resultado_ventana.title("Resultados de búsqueda")

                for idx, dueño in enumerate(resultados, start=1):
                    nombre_db = dueño.get("nombre", "")
                    telefono_db = dueño.get("telefono", "")
                    direccion_db= dueño.get("direccion","")

                    # Buscar perros asociados a este dueño
                    dueño_id = dueño.get("_id")
                    perros = list(perros_col.find({"dueño_id": dueño_id}))

                    if perros:
                        nombres_perros = ", ".join([p.get("nombre", "Sin nombre") for p in perros])
                    else:
                        nombres_perros = "Sin perros asignados"
                    texto = (
                        f"{idx}. Nombre:  {nombre_db}\n"
                        f" Numero Telefonico:  {telefono_db}\n"
                        f"Direccion:  {direccion_db}\n"
                        f"perros asociados:  {nombres_perros}"
                    )
                tk.Label(resultado_ventana, text=texto, justify="left", anchor="w", wraplength=500).pack(anchor="w", padx=10, pady=2)
                

            except Exception as e:
                messagebox.showerror("Error al buscar", str(e))


            print("")
        ventana_dueño = tk.Toplevel(ventana)
        ventana_dueño.title("BUSCAR PERROS")

        tk.Label(ventana_dueño, text="Nombre del dueño:").pack(pady=5)
        nombre_dueño = tk.Entry(ventana_dueño)
        nombre_dueño.pack(pady=5)

        tk.Label(ventana_dueño, text="numero del dueño:").pack(pady=5)
        telefono_dueño = tk.Entry(ventana_dueño)
        telefono_dueño.pack(pady=5)

        tk.Button(ventana_dueño, text="BUSCAR", command=buscar_dueño).pack(pady=10)
        ventana.title("BUSCAR DUEÑOS")

    def opcion_cuidador():
        def buscar_cuidador():


            nombre=nombre_cuidador.get().strip()
            telefono=telefono_cuidador.get().strip()

            filtro = {}

            if nombre:
                filtro["nombre"] = nombre

            if telefono:
                filtro["telefono"] = telefono

            try:
                db = cliente_autenticado["galgos"]
                cuidadores_col = db["cuidadores"]
                perros_col = db["perros"]
                resultados = list(cuidadores_col.find(filtro))

                if not resultados:
                    messagebox.showinfo("Sin resultados", "No se encontraron dueños con esos criterios.")
                    return
                
                resultado_ventana = tk.Toplevel(ventana)
                resultado_ventana.title("Resultados de búsqueda")

                for idx, cuidador in enumerate(resultados, start=1):
                    nombre_db = cuidador.get("nombre", "")
                    telefono_db = cuidador.get("telefono", "")
                    direccion_db= cuidador.get("direccion","")

                    # Buscar perros asociados a este dueño
                    cuidador_id = cuidador.get("_id")
                    perros = list(perros_col.find({"cuidador_id": cuidador_id}))

                    if perros:
                        nombres_perros = ", ".join([p.get("nombre", "Sin nombre") for p in perros])
                    else:
                        nombres_perros = "Sin perros asignados"
                    texto = (
                        f"{idx}. Nombre:  {nombre_db}\n"
                        f" Numero Telefonico:  {telefono_db}\n"
                        f"Direccion:  {direccion_db}\n"
                        f"perros asociados:  {nombres_perros}"
                    )
                tk.Label(resultado_ventana, text=texto, justify="left", anchor="w", wraplength=500).pack(anchor="w", padx=10, pady=2)
                

            except Exception as e:
                messagebox.showerror("Error al buscar", str(e))


            print("")
        ventana_cuidador = tk.Toplevel(ventana)
        ventana_cuidador.title("BUSCAR CUIDADOR")

        tk.Label(ventana_cuidador, text="Nombre del cuidador:").pack(pady=5)
        nombre_cuidador = tk.Entry(ventana_cuidador)
        nombre_cuidador.pack(pady=5)

        tk.Label(ventana_cuidador, text="Numero telefonico del cuidador:").pack(pady=5)
        telefono_cuidador = tk.Entry(ventana_cuidador)
        telefono_cuidador.pack(pady=5)

        tk.Button(ventana_cuidador, text="BUSCAR", command=buscar_cuidador).pack(pady=10)
        ventana.title("BUSCAR CUIDADORES")

    def opcion_carreras():
        print("buscandooo")
        def buscar_carreras():
            try:
                # 1. Captura de datos desde el formulario
                fecha_str = f"{dia_var.get()}/{mes_var.get()}/{anio_var.get()}"
                lugar = origen_perro.get().strip()
                cantidad = edad_perro.get().strip()
                division = color_perro.get().strip()

                # 2. Construcción del filtro
                filtro = {}

                # Convertir fecha a objeto datetime
                try:
                    fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
                    filtro["fecha"] = {
                        "$gte": datetime(fecha_obj.year, fecha_obj.month, fecha_obj.day),
                        "$lt": datetime(fecha_obj.year, fecha_obj.month, fecha_obj.day + 1)
                    }
                except Exception:
                    pass  # Si no se puede convertir, no se filtra por fecha

                if lugar:
                    filtro["lugar"] = lugar

                # Conectar con Mongo
                db = cliente_autenticado["galgos"]
                carreras_col = db["carreras"]
                carreras = carreras_col.find(filtro)

                # Ventana de resultados
                resultado_ventana = tk.Toplevel(ventana)
                resultado_ventana.title("Resultados de búsqueda")

                encontrados = 0
                for idx, carrera in enumerate(carreras, start=1):
                    resultados = carrera.get("resultados", [])
                    
                    # Si se solicitó filtrar por cantidad
                    if cantidad:
                        try:
                            if len(resultados) != int(cantidad):
                                continue
                        except ValueError:
                            pass

                    # Si se solicitó filtrar por división (ej. tiempo máximo permitido)
                    if division:
                        try:
                            tiempo_limite = float(division)
                            if not all(r.get("tiempo", 0) <= tiempo_limite for r in resultados):
                                continue
                        except ValueError:
                            pass

                    # Mostrar resultado
                    fecha_db = carrera.get("fecha", "").strftime("%d/%m/%Y %H:%M")
                    lugar_db = carrera.get("lugar", "")
                    total_perros = len(resultados)
                    ganador = str(carrera.get("ganador_id", ""))

                    texto = (
                        f"{idx}. Fecha: {fecha_db}\n"
                        f"   Lugar: {lugar_db}\n"
                        f"   Nº de perros: {total_perros}\n"
                        f"   Ganador (ID): {ganador}\n"
                        "------------------------------"
                    )

                    tk.Label(resultado_ventana, text=texto, justify="left", anchor="w", wraplength=500).pack(anchor="w", padx=10, pady=2)
                    encontrados += 1

                if encontrados == 0:
                    tk.Label(resultado_ventana, text="No se encontraron carreras con los criterios dados.").pack(pady=10)

            except Exception as e:
                messagebox.showerror("Error al buscar", str(e))


        ventana_perros = tk.Toplevel()
        ventana_perros.title("BUSCAR CARRERAS")

        # ===== Fecha (día / mes / año) =====
        tk.Label(ventana_perros, text="Fecha de carrera:").pack(pady=5)

        # Variables y opciones para día, mes y año
        dia_var = tk.StringVar()
        mes_var = tk.StringVar()
        anio_var = tk.StringVar()

        dias = [str(d) for d in range(1, 32)]
        meses = [str(m) for m in range(1, 13)]
        anios = [str(a) for a in range(2020, datetime.now().year + 2)]

        dia_var.set(dias[0])
        mes_var.set(meses[0])
        anio_var.set(anios[0])

        # Menús desplegables
        frame_fecha = tk.Frame(ventana_perros)
        frame_fecha.pack(pady=5)

        tk.OptionMenu(frame_fecha, dia_var, *dias).pack(side="left")
        tk.OptionMenu(frame_fecha, mes_var, *meses).pack(side="left")
        tk.OptionMenu(frame_fecha, anio_var, *anios).pack(side="left")

        # ===== Otros campos =====
        tk.Label(ventana_perros, text="Lugar de carrera:").pack(pady=5)
        origen_perro = tk.Entry(ventana_perros)
        origen_perro.pack(pady=5)

        tk.Label(ventana_perros, text="Cantidad de perros:").pack(pady=5)
        edad_perro = tk.Entry(ventana_perros)
        edad_perro.pack(pady=5)

        tk.Label(ventana_perros, text="División por tiempos de perros:").pack(pady=5)
        color_perro = tk.Entry(ventana_perros)
        color_perro.pack(pady=5)

        # ===== Botón buscar =====
        tk.Button(ventana_perros, text="BUSCAR", command=buscar_carreras).pack(pady=10)

    # Ventana principal de búsqueda
    global ventana
    ventana = tk.Toplevel()  # usa Toplevel para no duplicar la raíz
    ventana.title("¿QUÉ DESEAS BUSCAR?")

    tk.Label(ventana, text="OPCIÓN BUSCAR PERROS:").pack(pady=5)
    tk.Button(ventana, text="BUSCAR", command=opcion_perro).pack(pady=10)

    tk.Label(ventana, text="OPCIÓN BUSCAR DUEÑOS:").pack(pady=5)
    tk.Button(ventana, text="BUSCAR", command=opcion_dueño).pack(pady=10)

    tk.Label(ventana, text="OPCIÓN BUSCAR CUIDADORES:").pack(pady=5)
    tk.Button(ventana, text="BUSCAR", command=opcion_cuidador).pack(pady=10)

    tk.Label(ventana, text="OPCIÓN BUSCAR CARRERAS:").pack(pady=5)
    tk.Button(ventana, text="BUSCAR", command=opcion_carreras).pack(pady=10)

def eliminar():
    print("eliminando")
#menu
menu = tk.Tk()
menu.configure(bg='#f0f0f0') 
menu.after(50000, login)  # 50 segundos se mostrara automaticamente el login  
encabezado = tk.Frame(menu, bg="#8A9A5B",width=100,height=100)
encabezado.pack(fill="x")
menu.geometry("300x300")
tk.Label(encabezado,
         text="🐶 MENÚ GALGERO 🐾",
         font=("Segoe UI", 30, "bold"),
         bg="#2E7D32",
         fg="#f0f0f0",
         pady=10).pack(pady=10)

#imagenes
img_izq = Image.open("images/carreras-de-galgos-c-galgo-libre-1.png").resize((500, 500))
foto_izq = ImageTk.PhotoImage(img_izq)
tk.Label( image=foto_izq, bg="#4CAF50").pack(side="left", padx=10)
img_der = Image.open("images/pbox.png").resize((500, 500))
foto_der = ImageTk.PhotoImage(img_der)
tk.Label( image=foto_der, bg="#4CAF50").pack(side="right", padx=10)
img_abajo = Image.open("images/logo_final.png").resize((400,200))
foto_abajo = ImageTk.PhotoImage(img_abajo)
tk.Label( image=foto_abajo).pack(side="bottom", padx=10)
img_log = Image.open("images/greyhound-speed-flame-silhouette-abstract-racing-hound-white-background-50611162-_1_-_1_.png",).resize((200,100))
foto_log = ImageTk.PhotoImage(img_log)
tk.Label(encabezado, image=foto_log,bg="#8A9A5B").pack(side="top", padx=10,)

#texto de bienvenida
tk.Label(menu,text="BIENVENIDO GALGERO :)",font=('Segoe UI', 12,"bold"), bg="#677141",fg="#f0f0f0").pack(pady=5)
#botones
ttk.Button(menu, text="🔍 Buscar", style="Menu.TButton",command=buscar,width=50).pack(pady=20)
ttk.Button(menu, text="🔐 Login",style="BotonGrande.TButton", command=login ,width=50).pack(pady=10)
ttk.Button(menu, text="🗑️Eliminar", style="Menu.TButton",state="disabled",width=50).pack(pady=4)
ttk.Button(menu, text="✏️ Actualizar", style="Menu.TButton",state="disabled",width=50).pack(pady=10)
ttk.Button(menu, text="➕ Agregar", style="Menu.TButton",state="disabled",width=50).pack(pady=10)
#estilos
style = ttk.Style()
style.theme_use('default')
style.configure("Menu.TButton",
                font=('Segoe UI', 10, 'bold'),
                foreground="white",
                background="#4CAF50",
                padding=10,
                bd=3)
style.map("Menu.TButton",
          background=[('active', '#45a049')])
style = ttk.Style()
style.configure("BotonGrande.TButton", font=("Segoe UI", 10))
#abre menu
menu.mainloop()



 
