import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime

from modelos import Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada, Reserva
from excepciones import (
    ErrorClienteInvalido,
    ErrorServicioNoDisponible,
    ErrorReservaInvalida,
    ErrorDatosIncompletos,
    ErrorCalculoCosto,
    ErrorOperacionNoPermitida,
)
from logger_app import Logger

# Logger global de la aplicación
log = Logger()


# APLICACIÓN PRINCIPAL
class SistemaGestionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Sistema Integral de Gestion")
        self.root.geometry("980x660")
        self.root.resizable(True, True)
        self.root.configure(bg="#2c3e50")

        # Listas en memoria (sin base de datos)
        self.clientes = []
        self.servicios = []
        self.reservas = []

        # Cargar los servicios que ofrece la empresa
        self._cargar_servicios_empresa()

        # Construir toda la interfaz
        self._construir_ui()

        log.info("Aplicacion iniciada correctamente")

    #  Carga de servicios predefinidos de la empresa
    def _cargar_servicios_empresa(self):
        try:
            s1 = ReservaSala("Sala Boardroom", 60000, capacidad_personas=20, tiene_proyector=True)
            s2 = ReservaSala("Sala Pequena", 30000, capacidad_personas=8, tiene_proyector=False)
            s3 = AlquilerEquipo("Laptop Lenovo", 15000, tipo_equipo="Laptop", cantidad_disponible=5)
            s4 = AlquilerEquipo("Proyector Epson", 20000, tipo_equipo="Proyector", cantidad_disponible=3)
            s5 = AsesoriaEspecializada("Asesoria TI", 90000, area="tecnologia", nombre_asesor="Ing. Ramirez")
            s6 = AsesoriaEspecializada("Asesoria Legal", 110000, area="legal", nombre_asesor="Dr. Martinez")
            self.servicios = [s1, s2, s3, s4, s5, s6]
            log.info(f"Se cargaron {len(self.servicios)} servicios de la empresa")
        except Exception as e:
            log.error(f"Error cargando servicios: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los servicios: {e}")

    #Construcción de la interfaz principal
    def _construir_ui(self):
        #Encabezado
        header = tk.Frame(self.root, bg="#2c3e50")
        header.pack(fill="x")
        tk.Label(
            header,
            text="Software FJ - Sistema Integral de Gestión",
            font=("Arial", 15, "bold"),
            bg="#0fd426",
            fg="white",
            pady=8,
        ).pack()

        # Notebook con las pestanas de Clientes, Servicios, Reservas, Simulación y Logs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._tab_clientes()
        self._tab_servicios()
        self._tab_reservas()
        self._tab_simulacion()
        self._tab_logs()

        # Poblar combos después de crear todas las pestanas
        self._actualizar_combos()

    # La pestaña 1 es la de clientes
    def _tab_clientes(self):
        frame = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(frame, text="  Clientes  ")

        form = tk.LabelFrame(frame, text=" Registrar nuevo cliente ", bg="#ecf0f1",
                             font=("Arial", 10, "bold"))
        form.pack(side="left", fill="y", padx=12, pady=12)

        campos = [
            ("Nombre completo:", "e_nombre"),
            ("Email:", "e_email"),
            ("Telefono:", "e_tel"),
            ("Cedula:", "e_cedula"),
        ]
        self._entradas_cliente = {}

        for i, (lbl, key) in enumerate(campos):
            tk.Label(form, text=lbl, bg="#ecf0f1", anchor="w").grid(
                row=i, column=0, sticky="w", padx=8, pady=6
            )
            ent = tk.Entry(form, width=24)
            ent.grid(row=i, column=1, padx=8, pady=6)
            self._entradas_cliente[key] = ent

        tk.Button(
            form, text="Registrar cliente", command=self._registrar_cliente,
            bg="#1a7a45", fg="white", font=("Arial", 10, "bold"), width=22, pady=4,
            relief="flat", activebackground="#145f35", activeforeground="white",
        ).grid(row=len(campos), column=0, columnspan=2, pady=(12, 4))

        tk.Button(
            form, text="Limpiar campos", command=self._limpiar_form_cliente,
            bg="#4a5568", fg="white", width=22,
            relief="flat", activebackground="#2d3748", activeforeground="white",
        ).grid(row=len(campos) + 1, column=0, columnspan=2, pady=2)

        # --- Lista de clientes ---
        lista = tk.LabelFrame(frame, text=" Clientes registrados ", bg="#ecf0f1",
                              font=("Arial", 10, "bold"))
        lista.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        cols = ("ID", "Nombre", "Email", "Telefono", "Cedula")
        self.tree_clientes = ttk.Treeview(lista, columns=cols, show="headings", height=19)
        anchos = {"ID": 40, "Nombre": 150, "Email": 180, "Telefono": 100, "Cedula": 110}
        for c in cols:
            self.tree_clientes.heading(c, text=c)
            self.tree_clientes.column(c, width=anchos[c])

        sb = ttk.Scrollbar(lista, orient="vertical", command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=sb.set)
        self.tree_clientes.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _registrar_cliente(self):
        try:
            nombre = self._entradas_cliente["e_nombre"].get().strip()
            email = self._entradas_cliente["e_email"].get().strip()
            tel = self._entradas_cliente["e_tel"].get().strip()
            cedula = self._entradas_cliente["e_cedula"].get().strip()

            # Verificar que no queden campos vacíos
            if not all([nombre, email, tel, cedula]):
                raise ErrorDatosIncompletos("Todos los campos son obligatorios")

            cliente = Cliente(nombre, email, tel, cedula)
            self.clientes.append(cliente)

            info = cliente.get_info()
            self.tree_clientes.insert(
                "", "end",
                values=(info["id"], info["nombre"], info["email"],
                        info["telefono"], info["cedula"]),
            )
            self._actualizar_combos()
            self._limpiar_form_cliente()
            messagebox.showinfo("Exito", f"Cliente '{nombre}' registrado correctamente.")

        except ErrorDatosIncompletos as e:
            messagebox.showwarning("Campos incompletos", str(e))
        except ErrorClienteInvalido as e:
            messagebox.showerror("Datos invalidos", str(e))
        except Exception as e:
            log.error(f"Error inesperado al registrar cliente: {e}")
            messagebox.showerror("Error inesperado", str(e))

    def _limpiar_form_cliente(self):
        for ent in self._entradas_cliente.values():
            ent.delete(0, tk.END)

    def _tab_servicios(self):
        frame = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(frame, text="  Servicios  ")

        tk.Label(frame, text="Servicios que ofrece Software FJ",
                 font=("Arial", 12, "bold"), bg="#ecf0f1").pack(pady=10)

        # Tabla de servicios
        contenedor = tk.Frame(frame, bg="#ecf0f1")
        contenedor.pack(fill="both", expand=True, padx=12)

        cols = ("ID", "Nombre", "Tipo", "Precio/hora", "Detalles", "Estado")
        self.tree_servicios = ttk.Treeview(contenedor, columns=cols, show="headings", height=18)
        anchos = {"ID": 40, "Nombre": 150, "Tipo": 150, "Precio/hora": 110, "Detalles": 250, "Estado": 110}
        for c in cols:
            self.tree_servicios.heading(c, text=c)
            self.tree_servicios.column(c, width=anchos[c])

        sb2 = ttk.Scrollbar(contenedor, orient="vertical", command=self.tree_servicios.yview)
        self.tree_servicios.configure(yscrollcommand=sb2.set)
        self.tree_servicios.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

        self.tree_servicios.tag_configure("disponible", background="#d5f5e3")
        self.tree_servicios.tag_configure("nodisponible", background="#fadbd8")

        # Botones para cambiar disponibilidad
        btns = tk.Frame(frame, bg="#ecf0f1")
        btns.pack(pady=8)
        tk.Button(btns, text="Deshabilitar servicio", command=self._deshabilitar_servicio,
                  bg="#922b21", fg="white", width=20,
                  relief="flat", activebackground="#7b241c", activeforeground="white",
                  ).pack(side="left", padx=6)
        tk.Button(btns, text="Habilitar servicio", command=self._habilitar_servicio,
                  bg="#1a7a45", fg="white", width=20,
                  relief="flat", activebackground="#145f35", activeforeground="white",
                  ).pack(side="left", padx=6)

        self._recargar_tabla_servicios()

    def _recargar_tabla_servicios(self):
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)

        for s in self.servicios:
            estado = "Disponible" if s.disponible else "No disponible"
            tag = "disponible" if s.disponible else "nodisponible"

            if isinstance(s, ReservaSala):
                detalles = f"Cap: {s.capacidad_personas} | Proyector: {'Si' if s.tiene_proyector else 'No'}"
            elif isinstance(s, AlquilerEquipo):
                detalles = f"Tipo: {s.tipo_equipo} | Unidades: {s.cantidad_disponible}"
            elif isinstance(s, AsesoriaEspecializada):
                detalles = f"Area: {s.area} | Asesor: {s.nombre_asesor}"
            else:
                detalles = "-"

            self.tree_servicios.insert(
                "", "end",
                values=(s.id, s.nombre, s._tipo, f"${s.precio_hora:,.0f}", detalles, estado),
                tags=(tag,),
            )

    def _deshabilitar_servicio(self):
        seleccion = self.tree_servicios.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un servicio de la lista primero.")
            return
        sid = self.tree_servicios.item(seleccion[0])["values"][0]
        for s in self.servicios:
            if s.id == sid:
                s.disponible = False
                log.advertencia(f"Servicio '{s.nombre}' deshabilitado manualmente")
                break
        self._recargar_tabla_servicios()
        self._actualizar_combos()

    def _habilitar_servicio(self):
        seleccion = self.tree_servicios.selection()
        if not seleccion:
            messagebox.showwarning("Atencion", "Selecciona un servicio de la lista primero.")
            return
        sid = self.tree_servicios.item(seleccion[0])["values"][0]
        for s in self.servicios:
            if s.id == sid:
                s.disponible = True
                log.info(f"Servicio '{s.nombre}' habilitado nuevamente")
                break
        self._recargar_tabla_servicios()
        self._actualizar_combos()

    def _tab_reservas(self):
        frame = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(frame, text="  Reservas  ")

        # --- Formulario nueva reserva ---
        form = tk.LabelFrame(frame, text=" Nueva reserva ", bg="#ecf0f1",
                             font=("Arial", 10, "bold"))
        form.pack(side="left", fill="y", padx=12, pady=12)

        tk.Label(form, text="Cliente:", bg="#ecf0f1").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.combo_cliente = ttk.Combobox(form, width=24, state="readonly")
        self.combo_cliente.grid(row=0, column=1, padx=8, pady=6)

        tk.Label(form, text="Servicio:", bg="#ecf0f1").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.combo_servicio = ttk.Combobox(form, width=24, state="readonly")
        self.combo_servicio.grid(row=1, column=1, padx=8, pady=6)

        tk.Label(form, text="Horas:", bg="#ecf0f1").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.entry_horas = tk.Entry(form, width=26)
        self.entry_horas.grid(row=2, column=1, padx=8, pady=6)

        tk.Label(form, text="Descuento %:", bg="#ecf0f1").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        self.entry_descuento = tk.Entry(form, width=26)
        self.entry_descuento.insert(0, "0")
        self.entry_descuento.grid(row=3, column=1, padx=8, pady=6)

        self.var_iva = tk.BooleanVar(value=True)
        tk.Checkbutton(form, text="Aplicar IVA (19%)", variable=self.var_iva,
                       bg="#ecf0f1").grid(row=4, column=0, columnspan=2, pady=5)

        tk.Button(form, text="Crear reserva", command=self._crear_reserva,
                  bg="#1a5276", fg="white", font=("Arial", 10, "bold"), width=22, pady=4,
                  relief="flat", activebackground="#154360", activeforeground="white",
                  ).grid(row=5, column=0, columnspan=2, pady=(10, 4))

        # Acciones sobre reserva seleccionada
        acciones = tk.LabelFrame(form, text=" Acciones ", bg="#ecf0f1")
        acciones.grid(row=6, column=0, columnspan=2, padx=6, pady=10, sticky="ew")

        tk.Button(acciones, text="Confirmar seleccionada", command=self._confirmar_reserva,
                  bg="#1a7a45", fg="white", width=22,
                  relief="flat", activebackground="#145f35", activeforeground="white",
                  ).pack(pady=4)
        tk.Button(acciones, text="Cancelar seleccionada", command=self._cancelar_reserva,
                  bg="#922b21", fg="white", width=22,
                  relief="flat", activebackground="#7b241c", activeforeground="white",
                  ).pack(pady=4)

        self.lbl_costo = tk.Label(form, text="Costo: ---", bg="#ecf0f1",
                                  font=("Arial", 11, "bold"), fg="#2c3e50")
        self.lbl_costo.grid(row=7, column=0, columnspan=2, pady=6)

        #Tabla de reservas
        lista = tk.LabelFrame(frame, text=" Reservas registradas ", bg="#ecf0f1",
                              font=("Arial", 10, "bold"))
        lista.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        cols = ("ID", "Cliente", "Servicio", "Horas", "Estado", "Costo")
        self.tree_reservas = ttk.Treeview(lista, columns=cols, show="headings", height=19)
        anchos2 = {"ID": 40, "Cliente": 130, "Servicio": 140, "Horas": 60, "Estado": 100, "Costo": 110}
        for c in cols:
            self.tree_reservas.heading(c, text=c)
            self.tree_reservas.column(c, width=anchos2[c])

        self.tree_reservas.tag_configure("pendiente", background="#fef9e7")
        self.tree_reservas.tag_configure("confirmada", background="#d5f5e3")
        self.tree_reservas.tag_configure("cancelada", background="#fadbd8")

        sb3 = ttk.Scrollbar(lista, orient="vertical", command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscrollcommand=sb3.set)
        self.tree_reservas.pack(side="left", fill="both", expand=True)
        sb3.pack(side="right", fill="y")

    def _actualizar_combos(self):
        """Actualiza los combobox de clientes y servicios disponibles"""
        self.combo_cliente["values"] = [
            f"{c.id} - {c.nombre}" for c in self.clientes
        ]
        self.combo_servicio["values"] = [
            f"{s.id} - {s.nombre}" for s in self.servicios if s.disponible
        ]

    def _crear_reserva(self):
        try:
            if not self.combo_cliente.get():
                raise ErrorDatosIncompletos("Debes seleccionar un cliente")
            if not self.combo_servicio.get():
                raise ErrorDatosIncompletos("Debes seleccionar un servicio")

            idx_cliente = self.combo_cliente.current()
            sid = int(self.combo_servicio.get().split(" - ")[0])

            cliente = self.clientes[idx_cliente]
            servicio = next((s for s in self.servicios if s.id == sid), None)

            if servicio is None:
                raise ErrorReservaInvalida("No se encontro el servicio seleccionado")

            try:
                horas = float(self.entry_horas.get())
            except ValueError:
                raise ErrorDatosIncompletos("Las horas deben ser un numero (ej: 2 o 1.5)")

            try:
                descuento = float(self.entry_descuento.get())
            except ValueError:
                descuento = 0

            fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
            reserva = Reserva(cliente, servicio, horas, fecha=fecha_hoy)
            costo = reserva.procesar(con_descuento=descuento, con_iva=self.var_iva.get())

            self.reservas.append(reserva)
            self._insertar_fila_reserva(reserva)
            self.lbl_costo.config(text=f"Costo: ${costo:,.0f}")
            messagebox.showinfo("Reserva creada", f"Reserva registrada.\nCosto total: ${costo:,.0f}")

        except ErrorDatosIncompletos as e:
            messagebox.showwarning("Campos incompletos", str(e))
        except ErrorReservaInvalida as e:
            messagebox.showerror("Reserva invalida", str(e))
        except ErrorServicioNoDisponible as e:
            messagebox.showerror("Servicio no disponible", str(e))
        except ErrorCalculoCosto as e:
            messagebox.showerror("Error en calculo", str(e))
        except Exception as e:
            log.error(f"Error inesperado al crear reserva: {e}")
            messagebox.showerror("Error inesperado", str(e))

    def _insertar_fila_reserva(self, reserva):
        info = reserva.get_info()
        self.tree_reservas.insert(
            "", "end",
            values=(info["id"], info["cliente"], info["servicio"],
                    info["duracion"], info["estado"], f"${info['costo']:,.0f}"),
            tags=(info["estado"],),
        )

    def _confirmar_reserva(self):
        sel = self.tree_reservas.selection()
        if not sel:
            messagebox.showwarning("Atencion", "Selecciona una reserva de la lista primero.")
            return
        rid = self.tree_reservas.item(sel[0])["values"][0]
        try:
            reserva = next((r for r in self.reservas if r.id == rid), None)
            if reserva is None:
                raise ErrorReservaInvalida("No se encontro la reserva seleccionada")
            costo = reserva.confirmar()
            self._recargar_tabla_reservas()
            self.lbl_costo.config(text=f"Costo: ${costo:,.0f}")
            messagebox.showinfo("Confirmada", f"Reserva confirmada.\nCosto: ${costo:,.0f}")
        except ErrorOperacionNoPermitida as e:
            messagebox.showerror("Operacion no permitida", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _cancelar_reserva(self):
        sel = self.tree_reservas.selection()
        if not sel:
            messagebox.showwarning("Atencion", "Selecciona una reserva de la lista primero.")
            return
        rid = self.tree_reservas.item(sel[0])["values"][0]
        try:
            reserva = next((r for r in self.reservas if r.id == rid), None)
            if reserva is None:
                raise ErrorReservaInvalida("No se encontro la reserva seleccionada")
            reserva.cancelar()
            self._recargar_tabla_reservas()
            messagebox.showinfo("Cancelada", "La reserva fue cancelada correctamente.")
        except ErrorOperacionNoPermitida as e:
            messagebox.showerror("Operacion no permitida", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _recargar_tabla_reservas(self):
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        for r in self.reservas:
            self._insertar_fila_reserva(r)

    def _tab_simulacion(self):
        frame = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(frame, text="  Simulacion  ")

        tk.Label(frame, text="Simulacion de 12 operaciones completas del sistema",
                 font=("Arial", 12, "bold"), bg="#ecf0f1").pack(pady=8)

        tk.Label(
            frame,
            text="Demuestra: try/except · try/except/else · try/except/finally · "
                 "encadenamiento de excepciones · excepciones personalizadas",
            font=("Arial", 9), bg="#ecf0f1", fg="#555",
        ).pack()

        tk.Button(frame, text="Ejecutar simulacion",
                  command=self._ejecutar_simulacion,
                  bg="#6c3483", fg="white", font=("Arial", 11, "bold"),
                  width=26, pady=5,
                  relief="flat", activebackground="#5b2c6f", activeforeground="white",
                  ).pack(pady=10)

        self.txt_sim = scrolledtext.ScrolledText(frame, font=("Courier", 9),
                                                  bg="#1a1a2e", fg="#e0e0e0",
                                                  insertbackground="white")
        self.txt_sim.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    def _escribir_sim(self, texto, color=None):
        """Escribe una línea en el área de simulación con color opcional"""
        self.txt_sim.insert(tk.END, texto + "\n")
        if color:
            # Colorear la última línea escrita
            lineas = int(self.txt_sim.index(tk.END).split(".")[0])
            start = f"{lineas - 2}.0"
            end = f"{lineas - 1}.0"
            tag = f"color_{color.replace('#','')}"
            self.txt_sim.tag_configure(tag, foreground=color)
            self.txt_sim.tag_add(tag, start, end)
        self.txt_sim.see(tk.END)
        self.root.update()  # refresca la UI en tiempo real

    def _ejecutar_simulacion(self):
        self.txt_sim.delete(1.0, tk.END)
        log.info("--- Inicio de la simulacion ---")

        def ok(msg):
            self._escribir_sim(f"  [OK]    {msg}", "#a8ff78")

        def err(msg):
            self._escribir_sim(f"  [ERROR] {msg}", "#ff6b6b")

        def info(msg):
            self._escribir_sim(f"  [INFO]  {msg}", "#74b9ff")

        def titulo(msg):
            self._escribir_sim(msg, "#ffeaa7")

        titulo("  SIMULACION - Sistema Software FJ")

        # Usamos los servicios cargados de la empresa
        sala = self.servicios[0]  #Sala Boardroom
        sala2 = self.servicios[1]  #Sala Pequeñaa
        equipo = self.servicios[2]  #Laptop Lenovo
        asesoria = self.servicios[4]  #Asesoria TI

        clientes_sim = []

        # OP 1: Registrar cliente válido
        titulo("\n[OP 1] Registrar cliente valido (try/except)")
        try:
            c1 = Cliente("Ana Garcia", "ana.garcia@gmail.com", "3001234567", "1098765432")
            clientes_sim.append(c1)
            ok(c1.describir())
        except ErrorClienteInvalido as e:
            err(f"No se esperaba este error: {e}")

        titulo("\n[OP 2] Registrar cliente con email invalido (try/except)")
        try:
            c_malo = Cliente("Juan Error", "esto-no-es-un-email", "3009999999", "1111111111")
            clientes_sim.append(c_malo)
        except ErrorClienteInvalido as e:
            err(f"Excepcion capturada: {e}")
            info("El sistema sigue funcionando correctamente")

        titulo("\n[OP 3] Registrar cliente con nombre muy corto (try/except)")
        try:
            c_malo2 = Cliente("AB", "ab@test.com", "3001111111", "22222222")
            clientes_sim.append(c_malo2)
        except ErrorClienteInvalido as e:
            err(f"Excepcion capturada: {e}")

        titulo("\n[OP 4] Registrar segundo cliente valido (try/except/ELSE)")
        try:
            c2 = Cliente("Carlos Lopez", "carlos.lopez@empresa.co", "6041234567", "98765432")
        except ErrorClienteInvalido as e:
            err(f"Fallo al registrar: {e}")
        else:
            clientes_sim.append(c2)
            ok(f"Registrado con exito (bloque else ejecutado): {c2.nombre}")

        titulo("\n[OP 5] Crear reserva de sala (estado: pendiente)")
        r1 = None
        try:
            r1 = Reserva(clientes_sim[0], sala, 2, fecha="2026-05-10")
            ok(f"Reserva creada | Estado: {r1.estado}")
        except ErrorReservaInvalida as e:
            err(f"Error: {e}")

        titulo("\n[OP 6] Crear reserva con duracion negativa (try/except)")
        try:
            r_mala = Reserva(clientes_sim[0], sala, -5)
        except ErrorReservaInvalida as e:
            err(f"Excepcion capturada: {e}")
            info("La reserva invalida fue rechazada, el sistema continua")

        titulo("\n[OP 7] Confirmar reserva r1 (try/except/ELSE)")
        try:
            if r1:
                costo = r1.confirmar()
        except ErrorOperacionNoPermitida as e:
            err(f"Error: {e}")
        else:
            ok(f"Reserva confirmada exitosamente | Costo base: ${costo:,.0f}")

        titulo("\n[OP 8] Reserva equipo | 15% descuento + IVA 19%")
        try:
            if len(clientes_sim) >= 2:
                r2 = Reserva(clientes_sim[1], equipo, 4, fecha="2026-05-10")
                total = r2.procesar(con_descuento=15, con_iva=True)
                ok(f"Reserva procesada | {r2.describir()}")
                info(f"Costo base: ${equipo.calcular_costo(4):,.0f} | "
                     f"Con 15% desc + IVA: ${total:,.0f}")
        except Exception as e:
            err(f"Error inesperado: {e}")

        titulo("\n[OP 9] Crear servicio con area invalida (try/except)")
        try:
            s_malo = AsesoriaEspecializada(
                "Asesoria de Cocina", 50000, area="cocina", nombre_asesor="Chef Perez"
            )
        except ErrorServicioNoDisponible as e:
            err(f"Excepcion capturada: {e}")

        titulo("\n[OP 10] Cancelar r1 y volver a cancelarla (try/except/FINALLY)")
        try:
            if r1:
                r1.cancelar()
                ok(f"Primera cancelacion OK | Estado: {r1.estado}")
                r1.cancelar()  # esto debe lanzar ErrorOperacionNoPermitida
        except ErrorOperacionNoPermitida as e:
            err(f"Segunda cancelacion - excepcion capturada: {e}")
        finally:
            info("Bloque finally ejecutado (siempre corre, con o sin error)")

        titulo("\n[OP 11] Reservar servicio deshabilitado (try/except/else/FINALLY)")
        sala2.disponible = False
        log.advertencia(f"Servicio '{sala2.nombre}' deshabilitado para la prueba")
        try:
            if clientes_sim:
                r_falla = Reserva(clientes_sim[0], sala2, 2)
        except ErrorServicioNoDisponible as e:
            err(f"Excepcion capturada: {e}")
        else:
            ok("No hubo error (inesperado en esta prueba)")
        finally:
            sala2.disponible = True  # restaurar para que la app siga funcionanddo
            info("Bloque finally: servicio restaurado a 'disponible'")

        titulo("\n[OP 12] Descuento invalido -> encadenamiento de excepciones")
        try:
            # descuento de 200% es imposible, deberia lanzar ErrorCalculoCosto
            costo_malo = asesoria.calcular_costo_total(3, descuento=200)
        except ErrorCalculoCosto as e:
            err(f"Excepcion capturada: {e}")
            if e.__cause__:
                info(f"Causa original encadenada: {e.__cause__}")
            else:
                info("(La excepcion fue lanzada directamente, sin causa encadenada)")

        # Resumen final
        titulo("  Simulacion completada: 12 operaciones")
        titulo("  El sistema se mantuvo estable durante todos los errores.")
        log.info("Fin de la simulacion")

        # Recargar la tabla de servicios por si acaso fue que algo cambio
        self._recargar_tabla_servicios()
        self._actualizar_combos()

    def _tab_logs(self):
        frame = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(frame, text="  Logs  ")

        tk.Label(frame, text="Registro de eventos y errores del sistema",
                 font=("Arial", 12, "bold"), bg="#ecf0f1").pack(pady=8)

        btns = tk.Frame(frame, bg="#ecf0f1")
        btns.pack()
        tk.Button(btns, text="Actualizar", command=self._cargar_logs,
                  bg="#2c3e50", fg="white", width=16,
                  relief="flat", activebackground="#1a252f", activeforeground="white",
                  ).pack(side="left", padx=5)
        tk.Button(btns, text="Limpiar vista", command=lambda: self.txt_logs.delete(1.0, tk.END),
                  bg="#4a5568", fg="white", width=16,
                  relief="flat", activebackground="#2d3748", activeforeground="white",
                  ).pack(side="left", padx=5)

        self.txt_logs = scrolledtext.ScrolledText(frame, font=("Courier", 9),
                                                   bg="#0d0d0d", fg="#00ff88")
        self.txt_logs.pack(fill="both", expand=True, padx=12, pady=8)
        self._cargar_logs()

    def _cargar_logs(self):
        self.txt_logs.delete(1.0, tk.END)
        self.txt_logs.insert(tk.END, log.leer_todos())
        self.txt_logs.see(tk.END)


def main():
    root = tk.Tk()
    app = SistemaGestionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
