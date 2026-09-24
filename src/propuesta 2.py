import tkinter as tk
from tkinter import messagebox
import time
import re
import uuid

SERVICIOS_COMUNES = "Cama king size, Televisión con cable, Baño privado con regadera, Cochera privada"

# ==========================================
# 1. MODELO (Lógica de datos y negocio)
# ==========================================
class MotelModelo:
    def __init__(self):
        self.habitaciones = {
            i: {
                "estado": "Disponible" if i not in (2, 5) else "Ocupado" if i == 2 else "En espera",
                "tipo": "Sencilla" if i <= 4 else "Suite" if i <= 7 else "VIP",
                "precio": 150 if i <= 4 else 250 if i <= 7 else 400,
                "servicios": f"{SERVICIOS_COMUNES}, WiFi, A/C" if i <= 4 else f"{SERVICIOS_COMUNES}, WiFi, A/C, Jacuzzi" if i <= 7 else f"{SERVICIOS_COMUNES}, WiFi, A/C, Jacuzzi, Frigobar",
                "tiempo": 3600 if i == 2 else 1200 if i == 5 else 0,
                "inicio": time.time() - 600 if i in (2, 5) else 0,
                "cliente": ""
            } for i in range(1, 14)
        }
        self.usuarios = []
        self.seleccionada = 1
        self.rol = "Cliente"
        self.admin_usuario = "admin"
        self.admin_contrasena = "admin12345"
        self.min_caracteres_contrasena = 8

    def cambiar_estado_habitacion(self, num, estado, duracion_horas=1):
        self.habitaciones[num]["estado"] = estado
        self.habitaciones[num]["inicio"] = time.time()
        if estado == "En espera":
            self.habitaciones[num]["tiempo"] = 1200
        elif estado == "Disponible":
            self.habitaciones[num]["tiempo"] = 0
            self.habitaciones[num]["cliente"] = ""
            self.usuarios = [u for u in self.usuarios if u["habitacion"] != num]
        elif estado == "Ocupado":
            self.habitaciones[num]["tiempo"] = duracion_horas * 3600

    def registrar_cliente(self, num, nombre, telefono, identificacion, horas):
        self.usuarios.append({
            "nombre": nombre,
            "telefono": telefono,
            "identificacion": identificacion,
            "habitacion": num
        })
        self.habitaciones[num]["cliente"] = nombre
        self.cambiar_estado_habitacion(num, "Ocupado", horas)


# ==========================================
# 2. VISTA (Interfaz Gráfica con Tkinter)
# ==========================================
class MotelVista(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Motel - Sistema de Reserva (MVC)")
        self.geometry("960x680")
        self.config(bg="#555b60")
        self.resizable(False, False)
        self.option_add("*Font", "Arial 10")

        # Canvas Izquierda (Mapa)
        self.frame_mapa = tk.Frame(self, bg="white", bd=2, relief="solid")
        self.frame_mapa.place(x=10, y=10, width=560, height=430)

        self.canvas = tk.Canvas(self.frame_mapa, bg="#d5d8dc", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_text(280, 18, text="Motel", font=("Arial", 12, "bold"))

        # Dibujar elementos estáticos de la calle y entradas
        ruta = [18, 108, 18, 190, 90, 230, 280, 255, 460, 255, 540, 295, 540, 428]
        self.canvas.create_line(ruta, width=38, fill="#1a1a1a", smooth=True, capstyle=tk.ROUND, joinstyle=tk.ROUND, splinesteps=36)
        self.canvas.create_line(ruta, width=3, fill="white", dash=(18, 12), smooth=True, capstyle=tk.ROUND, splinesteps=36)

        self.canvas.create_rectangle(50, 95, 125, 125, fill="white", outline="#1a237e", width=1.5)
        self.canvas.create_text(87, 110, text="Check in", font=("Arial", 9, "bold"), fill="#1a237e")

        self.canvas.create_rectangle(450, 395, 515, 422, fill="white", outline="#1a237e", width=1.5)
        self.canvas.create_text(482, 408, text="Entrada", font=("Arial", 9, "bold"), fill="#1a237e")

        self.cuartos_btn = {}
        self._construir_cuartos()

        # Panel Derecho
        self.frame_der = tk.Frame(self, bg="white", bd=2, relief="solid")
        self.frame_der.place(x=580, y=10, width=370, height=430)

        self.lbl_rol = tk.Label(self.frame_der, text="Modo: CLIENTE", font=("Arial", 9, "bold"), fg="#1a237e", bg="white")
        self.lbl_rol.place(x=20, y=20)
        tk.Frame(self.frame_der, bg="black", height=1).place(x=10, y=45, width=350)

        self.lbl_num = tk.Label(self.frame_der, text="Habitación 1", font=("Arial", 12, "bold"), bg="white")
        self.lbl_num.place(x=20, y=60)

        self.lbl_detalle = tk.Label(self.frame_der, text="", bg="white", justify=tk.LEFT, font=("Arial", 10), anchor="nw")
        self.lbl_detalle.place(x=20, y=90, width=330, height=150)

        self.btn_espera = tk.Button(self.frame_der, text="En espera", bg="#ffd54f", width=12)
        self.btn_liberar = tk.Button(self.frame_der, text="Liberar", bg="#81c784", width=12)

        self.frame_tiempo = tk.Frame(self.frame_der, bg="#e8eefc", bd=1, relief="solid")
        tk.Label(self.frame_tiempo, text="Duración:", font=("Arial", 9, "bold"), bg="#e8eefc", fg="#1a237e").place(x=12, y=11)
        
        self.horas_seleccionadas = tk.StringVar(value="1 hora")
        self.btn_horas = tk.OptionMenu(self.frame_tiempo, self.horas_seleccionadas, "1 hora", "2 horas", "3 horas", "4 horas", "6 horas", "8 horas", "12 horas")
        self.btn_horas.config(width=10, bg="white", fg="#1a237e", relief="raised", bd=1)
        self.btn_horas.place(x=105, y=4)

        self.btn_registrar = tk.Button(self.frame_der, text="Registrar usuario", bg="#64b5f6", fg="white", width=25)

        # Panel Inferior
        self.frame_inf = tk.Frame(self, bg="#fafafa", bd=2, relief="solid")
        self.frame_inf.place(x=10, y=450, width=940, height=220)

        tk.Label(self.frame_inf, text="Servicios incluidos en la habitación seleccionada", font=("Arial", 11, "bold"), bg="#fafafa", fg="#1a237e").place(x=20, y=15)

        self.lbl_inf_num = tk.Label(self.frame_inf, text="", font=("Arial", 11, "bold"), bg="#fafafa")
        self.lbl_inf_num.place(x=25, y=60)

        self.lbl_inf_precio = tk.Label(self.frame_inf, text="", font=("Arial", 10), bg="#fafafa")
        self.lbl_inf_precio.place(x=25, y=92)

        self.lbl_inf_titulo = tk.Label(self.frame_inf, text="Servicios incluidos:", font=("Arial", 10, "bold"), bg="#fafafa")
        self.lbl_inf_titulo.place(x=300, y=60)
        
        self.lbl_inf_servicios = tk.Label(self.frame_inf, text="", bg="#fafafa", justify=tk.LEFT, anchor="nw", font=("Arial", 11), wraplength=520)
        self.lbl_inf_servicios.place(x=300, y=90, width=560, height=95)

        # Leyenda de estados
        f_ley = tk.Frame(self.frame_inf, bg="#fafafa")
        f_ley.place(x=650, y=18, width=270, height=30)
        tk.Label(f_ley, text="LIBRE", width=8, bg="#81c784", anchor=tk.CENTER).pack(side=tk.LEFT, padx=2)
        tk.Label(f_ley, text="OCUPADO", width=10, bg="#e57373", anchor=tk.CENTER).pack(side=tk.LEFT, padx=2)
        tk.Label(f_ley, text="EN ESPERA", width=12, bg="#ffd54f", anchor=tk.CENTER).pack(side=tk.LEFT, padx=2)

        self.btn_acceso_admin = tk.Button(self.frame_inf, text="Acceso administrador", bg="#1a237e", fg="white", width=22)
        self.btn_acceso_admin.place(x=715, y=175)

    def _construir_cuartos(self):
        def dibujar_cuarto(numero, x1, y1):
            x2 = x1 + 50
            y2 = y1 + 38
            r = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#8ed48e", outline="black", width=1.2)
            t = self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(numero), font=("Arial", 9, "bold"))
            self.cuartos_btn[numero] = (r, t)

        for i in range(1, 11):
            dibujar_cuarto(i, 5 + (i - 1) * 55, 35)
        for i in range(11, 14):
            dibujar_cuarto(i, 5 + 9 * 55, 35 + (i - 10) * 45)

    def actualizar_visuales(self, modelo):
        i = modelo.seleccionada
        info = modelo.habitaciones[i]
        
        # Pintar canvas
        for num in range(1, 14):
            r, t = self.cuartos_btn[num]
            est = modelo.habitaciones[num]["estado"]
            if est == "Disponible":
                self.canvas.itemconfig(r, fill="#81c784")
            elif est == "Ocupado":
                self.canvas.itemconfig(r, fill="#e57373")
            else:
                self.canvas.itemconfig(r, fill="#ffd54f")
            
            if num == i:
                self.canvas.itemconfig(r, outline="#1a237e", width=3)
            else:
                self.canvas.itemconfig(r, outline="black", width=1.2)

        # Actualizar textos del panel derecho e inferior
        self.lbl_num.config(text=f"Habitación {i} - {info['tipo']}")
        self.lbl_inf_num.config(text=f"Habitación {i} - {info['tipo']}")
        self.lbl_inf_precio.config(text=f"Precio por hora: ${info['precio']}")
        self.lbl_inf_servicios.config(text=info["servicios"])

        descripcion = info["servicios"]
        if info["estado"] == "Disponible":
            txt = f"Estado: DISPONIBLE\n\nPrecio por hora: ${info['precio']}\n\nServicios:\n{descripcion}"
        elif info["estado"] == "Ocupado":
            restante = max(0, info["tiempo"] - int(time.time() - info["inicio"]))
            m, s = divmod(restante, 60)
            registro_cliente = next((u for u in modelo.usuarios if u["habitacion"] == i), None)
            cliente_txt = f"\nCliente: {info['cliente']}" if info['cliente'] else ""
            if modelo.rol == "Administrador" and registro_cliente:
                cliente_txt += f"\nCódigo: {registro_cliente['identificacion']}"
            txt = f"Estado: OCUPADO\n\nTiempo restante: {m:02d}:{s:02d}\n\nTipo: {info['tipo']}\nPrecio por hora: ${info['precio']}{cliente_txt}"
        else:
            trans = int(time.time() - info["inicio"])
            m, s = divmod(trans, 60)
            txt = f"Estado: EN ESPERA\n\nTiempo transcurrido: {m:02d}:{s:02d}\n\nTipo: {info['tipo']}\nPrecio por hora: ${info['precio']}"

        self.lbl_detalle.config(text=txt, wraplength=300)


# ==========================================
# 3. CONTROLADOR (El Puente)
# ==========================================
class MotelControlador:
    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.actualizacion_id = None

        # Vincular eventos de la vista con métodos del controlador
        self.vista.canvas.bind("<Button-1>", self.seleccionar_habitacion)
        self.vista.btn_espera.config(command=lambda: self.cambiar_estado("En espera"))
        self.vista.btn_liberar.config(command=lambda: self.cambiar_estado("Disponible"))
        self.vista.btn_registrar.config(command=self.abrir_ventana_registro)
        self.vista.btn_acceso_admin.config(command=self.gestionar_sesion)

        self.actualizar_bucle()

    def seleccionar_habitacion(self, event):
        for i in range(1, 14):
            r, t = self.vista.cuartos_btn[i]
            x1, y1, x2, y2 = self.vista.canvas.coords(r)
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.modelo.seleccionada = i
                self.vista.actualizar_visuales(self.modelo)
                break

    def cambiar_estado(self, estado):
        self.modelo.cambiar_estado_habitacion(self.modelo.seleccionada, estado)
        self.vista.actualizar_visuales(self.modelo)

    def actualizar_bucle(self):
        self.vista.actualizar_visuales(self.modelo)
        if self.actualizacion_id:
            self.vista.after_cancel(self.actualizacion_id)
        self.actualizacion_id = self.vista.after(1000, self.actualizar_bucle)

    def cambiar_rol(self, nuevo_rol):
        self.modelo.rol = nuevo_rol
        self.vista.lbl_rol.config(text="Modo: " + nuevo_rol.upper())
        estado = "normal" if nuevo_rol == "Administrador" else "disabled"
        
        for boton in [self.vista.btn_espera, self.vista.btn_liberar, self.vista.btn_registrar, self.vista.btn_horas]:
            boton.config(state=estado)

        if nuevo_rol == "Administrador":
            self.vista.btn_acceso_admin.config(text="Cerrar sesión", command=self.gestionar_sesion)
            self.vista.btn_espera.place(x=50, y=265)
            self.vista.btn_liberar.place(x=200, y=265)
            self.vista.btn_registrar.place(x=80, y=355)
            self.vista.frame_tiempo.place(x=20, y=295, width=330, height=45)
        else:
            self.vista.btn_acceso_admin.config(text="Acceso administrador", command=self.gestionar_sesion)
            self.vista.btn_espera.place_forget()
            self.vista.btn_liberar.place_forget()
            self.vista.btn_registrar.place_forget()
            self.vista.frame_tiempo.place_forget()

    def gestionar_sesion(self):
        if self.modelo.rol == "Administrador":
            self.cambiar_rol("Cliente")
            messagebox.showinfo("Sesión cerrada", "El modo administrador se ha cerrado.")
        else:
            self.abrir_login()

    def abrir_login(self):
        ventana_login = tk.Toplevel(self.vista)
        ventana_login.title("Acceso de administrador")
        ventana_login.geometry("320x210")
        ventana_login.resizable(False, False)
        ventana_login.transient(self.vista)
        ventana_login.grab_set()

        tk.Label(ventana_login, text="Acceso de administrador", font=("Arial", 12, "bold")).pack(pady=12)
        tk.Label(ventana_login, text="Usuario:").pack()
        entrada_usuario = tk.Entry(ventana_login, width=28)
        entrada_usuario.pack(pady=3)

        tk.Label(ventana_login, text="Contraseña:").pack()
        entrada_contrasena = tk.Entry(ventana_login, width=28, show="*")
        entrada_contrasena.pack(pady=3)

        def iniciar_sesion():
            usuario = entrada_usuario.get().strip()
            contrasena = entrada_contrasena.get()

            if len(contrasena) < self.modelo.min_caracteres_contrasena:
                messagebox.showwarning("Contraseña no válida", f"Mínimo {self.modelo.min_caracteres_contrasena} caracteres.", parent=ventana_login)
                return
            if not re.fullmatch(r"[A-Za-z0-9]+", contrasena):
                messagebox.showwarning("Contraseña no válida", "Solo letras y números.", parent=ventana_login)
                return

            if usuario == self.modelo.admin_usuario and contrasena == self.modelo.admin_contrasena:
                self.cambiar_rol("Administrador")
                ventana_login.destroy()
                messagebox.showinfo("Acceso autorizado", "Modo administrador activado.")
            else:
                messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.", parent=ventana_login)

        tk.Button(ventana_login, text="Iniciar sesión", command=iniciar_sesion, bg="#1a237e", fg="white", width=18).pack(pady=10)
        entrada_usuario.focus_set()

    def abrir_ventana_registro(self):
        i = self.modelo.seleccionada
        if self.modelo.habitaciones[i]["estado"] != "Disponible":
            messagebox.showwarning("Habitación ocupada", "Selecciona una habitación disponible.")
            return

        ventana_reg = tk.Toplevel(self.vista)
        ventana_reg.title("Registrar usuario")
        ventana_reg.geometry("390x340")
        ventana_reg.resizable(False, False)
        ventana_reg.configure(bg="#f4f6fb")

        formulario = tk.Frame(ventana_reg, bg="#f4f6fb")
        formulario.pack(fill=tk.BOTH, expand=True)

        tk.Label(formulario, text=f"Registrar usuario - Habitación {i}", font=("Arial", 12, "bold"), fg="#1a237e", bg="#f4f6fb").pack(pady=15)
        tk.Label(formulario, text="Nombre:", bg="#f4f6fb").pack()
        nombre = tk.Entry(formulario, width=30)
        nombre.pack(pady=5)

        tk.Label(formulario, text="Teléfono:", bg="#f4f6fb").pack()
        telefono = tk.Entry(formulario, width=30)
        telefono.pack(pady=5)

        tk.Label(formulario, text="Identificación generada:", bg="#f4f6fb").pack()
        identificacion = f"CLI-{uuid.uuid4().hex[:8].upper()}"
        tk.Label(formulario, text=identificacion, fg="#1a237e", bg="#f4f6fb", font=("Arial", 10, "bold")).pack(pady=5)

        verificacion = tk.Frame(ventana_reg, bg="#f4f6fb")
        tk.Label(verificacion, text="Verificar información", font=("Arial", 15, "bold"), fg="#1a237e", bg="#f4f6fb").pack(pady=(18, 4))
        tk.Label(verificacion, text="Revisa los datos antes de confirmar el registro", font=("Arial", 9), fg="#555555", bg="#f4f6fb").pack(pady=(0, 12))

        tarjeta = tk.Frame(verificacion, bg="white", bd=1, relief="solid")
        tarjeta.pack(fill=tk.X, padx=25, pady=4)
        datos_verificacion = tk.Label(tarjeta, text="", justify=tk.LEFT, anchor="w", font=("Arial", 10), bg="white", padx=15, pady=12)
        datos_verificacion.pack(fill=tk.X)

        botones_verificacion = tk.Frame(verificacion, bg="#f4f6fb")
        botones_verificacion.pack(pady=18)

        def guardar():
            if not nombre.get().strip():
                messagebox.showwarning("Error", "Ingresa el nombre.")
                return

            datos = (
                f"Nombre: {nombre.get().strip()}\n"
                f"Teléfono: {telefono.get().strip() or 'No indicado'}\n"
                f"Código: {identificacion}\n"
                f"Habitación: {i}\n"
                f"Duración: {self.vista.horas_seleccionadas.get()}"
            )
            datos_verificacion.config(text=datos)
            formulario.pack_forget()
            verificacion.pack(fill=tk.BOTH, expand=True)

        def confirmar_registro():
            horas = int(self.vista.horas_seleccionadas.get().split()[0])
            self.modelo.registrar_cliente(i, nombre.get(), telefono.get(), identificacion, horas)
            ventana_reg.destroy()
            self.vista.actualizar_visuales(self.modelo)
            messagebox.showinfo("Registro", "Usuario registrado correctamente.")

        tk.Button(botones_verificacion, text="Cancelar", command=ventana_reg.destroy, width=12, bg="#e0e0e0").pack(side=tk.LEFT, padx=6)
        tk.Button(botones_verificacion, text="Confirmar registro", command=confirmar_registro, width=16, bg="#1a237e", fg="white").pack(side=tk.LEFT, padx=6)
        tk.Button(formulario, text="Verificar datos", command=guardar, bg="#1a237e", fg="white", width=18).pack(pady=15)
        tk.Button(botones_verificacion, text="Editar datos", command=lambda: (verificacion.pack_forget(), formulario.pack(fill=tk.BOTH, expand=True)), width=12, bg="#e0e0e0").pack(side=tk.LEFT, padx=6)


# ==========================================
# 4. INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    modelo = MotelModelo()
    vista = MotelVista()
    controlador = MotelControlador(modelo, vista)
    vista.mainloop()