from pymongo import MongoClient
from pymongo.errors import OperationFailure
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
#conexion y usuarios
client = MongoClient("mongodb://localhost:27017/")
bd = ["galgos"]
colecion = ["carreras","cuidadores","dueños","perros"]
estado_login={"logueado":False,"rol":None}
usuarios = {"admin":{"clave":"Admin1234","rol":"admin"},
            "usuario_basico":{"clave":"soloBuscarAgregar123","rol":"insertAndFindOnly"}}

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
                resultado = cliente[base_auth].command("usersInfo", user)

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

#imagen
img_izq = Image.open("images/carreras-de-galgos-c-galgo-libre-1.png").resize((500, 500))
foto_izq = ImageTk.PhotoImage(img_izq)
tk.Label( image=foto_izq, bg="#4CAF50").pack(side="left", padx=10)
#imagen
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
ttk.Button(menu, text="🔍 Buscar", style="Menu.TButton",width=50).pack(pady=20)
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


 
