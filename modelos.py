from abc import ABC, abstractmethod
import re

from excepciones import (
    ErrorClienteInvalido,
    ErrorServicioNoDisponible,
    ErrorReservaInvalida,
    ErrorCalculoCosto,
    ErrorOperacionNoPermitida,
)
from logger_app import Logger

# Logger compartido por todos los modelos del sistema
log = Logger()


#  CLASE ABSTRACTA BASE: representa cualquier entidad del sistema
class EntidadBase(ABC):
    """
    Clase abstracta que sirve de base para todas las entidades.
    Define la interfaz mínima que deben implementar Cliente, Servicio y Reserva.
    """
    #contador compartido para generar IDs únicos para todas las entidades que hereden de esta clase
    _id_global = 0  

    def __init__(self, nombre):
        EntidadBase._id_global += 1
        self.__id = EntidadBase._id_global
        self._nombre = nombre

    #Propiedades de solo lectur
    @property
    def id(self):
        return self.__id

    @property
    def nombre(self):
        return self._nombre

    # Métodos abstractos que DEBEN implementar las subclases
    @abstractmethod
    def describir(self):
        """Retorna un texto con la información de la entidad"""
        pass

    @abstractmethod
    def validar(self):
        """Valida que los datos de la entidad sean correctos"""
        pass

    def __str__(self):
        return self.describir()

    def __repr__(self):
        return f"{type(self).__name__}(id={self.__id})"


#  CLASE CLIENTE  -  gestión de datos personales con encapsulación
class Cliente(EntidadBase):
    """
    Representa un cliente del sistema con validaciones estrictas.
    Usa encapsulación (atributos privados con getters y setters).
    """

    def __init__(self, nombre, email, telefono, cedula):
        # Guardamos los atributos privados ANTES de llamar al padre
        # porque validar() los necesita y se llama desde aquí
        self.__email = email
        self.__telefono = telefono
        self.__cedula = cedula
        super().__init__(nombre)
        self.validar()
        log.info(f"Cliente registrado: {nombre} | {email}")

    #Getters
    @property
    def email(self):
        return self.__email

    @property
    def telefono(self):
        return self.__telefono

    @property
    def cedula(self):
        return self.__cedula

    #Setters con validación
    @email.setter
    def email(self, nuevo_valor):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', nuevo_valor):
            raise ErrorClienteInvalido(f"El email '{nuevo_valor}' no es valido")
        self.__email = nuevo_valor

    @telefono.setter
    def telefono(self, nuevo_valor):
        limpio = nuevo_valor.replace(" ", "").replace("-", "")
        if not limpio.isdigit() or len(limpio) < 7:
            raise ErrorClienteInvalido("El telefono debe tener minimo 7 digitos numericos")
        self.__telefono = limpio

    def validar(self):
        """Revisa que nombre, email, telefono y cedula sean correctos"""
        try:
            #Nombre: mínimo 3 caracteres
            if not self._nombre or len(self._nombre.strip()) < 3:
                raise ErrorClienteInvalido("El nombre debe tener al menos 3 caracteres")

            #Email: formato básico con regex
            patron = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
            if not re.match(patron, self.__email):
                raise ErrorClienteInvalido(f"El email '{self.__email}' no tiene formato valido")

            #Teléfono: solo dígitos, mínimo 7
            tel = self.__telefono.replace(" ", "").replace("-", "")
            if not tel.isdigit() or len(tel) < 7:
                raise ErrorClienteInvalido("El telefono debe tener minimo 7 digitos numericos")

            # Cédula: solo dígitos
            if not self.__cedula or not self.__cedula.strip().isdigit():
                raise ErrorClienteInvalido("La cedula solo puede contener numeros")

        except ErrorClienteInvalido as e:
            log.error(f"Validacion fallida - Cliente '{self._nombre}': {e}")
            raise  # re-lanzamos para que quien llame pueda manejarlo

    def describir(self):
        return (f"Cliente #{self.id}: {self._nombre} | "
                f"Email: {self.__email} | Tel: {self.__telefono} | CC: {self.__cedula}")

    def get_info(self):
        """Retorna los datos del cliente como diccionario"""
        return {
            "id": self.id,
            "nombre": self._nombre,
            "email": self.__email,
            "telefono": self.__telefono,
            "cedula": self.__cedula,
        }


#  CLASE ABSTRACTA SERVICIO, base para los 3 tipos de servicio
class Servicio(EntidadBase):
    """
    Clase abstracta que define la estructura común de los servicios.
    Las subclases deben implementar calcular_costo() y describir().
    Aquí van los métodos "sobrecargados" usando parámetros opcionales
    (en Python no hay sobrecarga real, se usa esta técnica).
    """

    def __init__(self, nombre, precio_hora, tipo_servicio):
        super().__init__(nombre)
        self._precio_hora = precio_hora
        self._tipo = tipo_servicio
        self._disponible = True
        #Nota: NO llamamos validar() aquí porque las subclases tienen
        #atributos propios que validar() necesita. Cada subclase lo llama.

    @property
    def precio_hora(self):
        return self._precio_hora

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)

    #Método abstracto: cada servicio calcula su costo diferente
    @abstractmethod
    def calcular_costo(self, horas):
        """Calculo base del costo (polimorfismo - se sobreescribe en cada clase)"""
        pass

    #Métodos sobrecargados (variantes del cálculo de costos)

    def calcular_costo_con_descuento(self, horas, descuento=0):
        """Variante 1: costo con un porcentaje de descuento"""
        try:
            if descuento < 0 or descuento > 100:
                raise ErrorCalculoCosto(
                    f"El descuento {descuento}% no es valido (debe estar entre 0 y 100)"
                )
            costo_base = self.calcular_costo(horas)
            ahorro = costo_base * (descuento / 100)
            return round(costo_base - ahorro, 2)
        except ErrorCalculoCosto:
            raise
        except Exception as e:
            raise ErrorCalculoCosto("Error aplicando el descuento") from e

    def calcular_costo_con_iva(self, horas, iva=0.19):
        """Variante 2: costo más IVA (19% por defecto, como en Colombia)"""
        try:
            if iva < 0:
                raise ErrorCalculoCosto("El IVA no puede ser un valor negativo")
            costo_base = self.calcular_costo(horas)
            return round(costo_base * (1 + iva), 2)
        except ErrorCalculoCosto:
            raise
        except Exception as e:
            raise ErrorCalculoCosto("Error calculando con IVA") from e

    def calcular_costo_total(self, horas, descuento=0, iva=0.19):
        """Variante 3 (completa): aplica descuento e IVA juntos"""
        try:
            #Primero aplica el descuento, luego le suma el IVA
            sin_iva = self.calcular_costo_con_descuento(horas, descuento)
            return round(sin_iva * (1 + iva), 2)
        except ErrorCalculoCosto:
            raise
        except Exception as e:
            #Encadenamiento de excepciones: guardamos la causa original
            raise ErrorCalculoCosto("No se pudo calcular el costo total") from e

    def verificar_disponibilidad(self):
        """Lanza excepcion si el servicio no está activo"""
        if not self._disponible:
            raise ErrorServicioNoDisponible(
                f"El servicio '{self._nombre}' no esta disponible en este momento"
            )

    def validar(self):
        """Validación base para todos los servicios"""
        if self._precio_hora <= 0:
            raise ErrorServicioNoDisponible(
                "El precio por hora debe ser un numero positivo"
            )

    def describir(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"[{self._tipo}] {self._nombre} | ${self._precio_hora:,.0f}/hora | {estado}"


#SERVICIO 1: RESERVA DE SALA
class ReservaSala(Servicio):
    """
    Servicio para reservar salas de reuniones o conferencias.
    Hereda de Servicio e implementa calcular_costo() con polimorfismo.
    """

    def __init__(self, nombre, precio_hora, capacidad_personas, tiene_proyector=False):
        #Atributos propios se asignan ANTES de llamar al padre
        self.capacidad_personas = capacidad_personas
        self.tiene_proyector = tiene_proyector
        super().__init__(nombre, precio_hora, "Sala de reuniones")
        self.validar()
        log.info(f"Servicio ReservaSala creado: {nombre} | cap: {capacidad_personas}")

    def calcular_costo(self, horas):
        """Costo de la sala: precio/hora * horas + cargo por proyector si aplica"""
        try:
            if horas <= 0:
                raise ErrorCalculoCosto("Las horas de reserva deben ser mayores a cero")
            costo = self._precio_hora * horas
            #Cargo fijo si la sala tiene proyector
            if self.tiene_proyector:
                costo += 20000
            return costo
        except ErrorCalculoCosto:
            raise
        except Exception as e:
            raise ErrorCalculoCosto("Error calculando costo de la sala") from e

    def describir(self):
        proyector = "con proyector" if self.tiene_proyector else "sin proyector"
        estado = "Disponible" if self._disponible else "No disponible"
        return (f"Sala '{self._nombre}' | {self.capacidad_personas} personas | "
                f"{proyector} | ${self._precio_hora:,.0f}/hora | {estado}")

    def validar(self):
        super().validar()
        if self.capacidad_personas <= 0:
            raise ErrorServicioNoDisponible(
                "La capacidad de la sala debe ser un numero mayor a cero"
            )


# SERVICIO 2:ALQUILER DE EQUIPO
class AlquilerEquipo(Servicio):
    """
    Servicio para alquilar equipos tecnológicos como laptops o proyectores.
    Hereda de Servicio e implementa calcular_costo() con polimorfismo.
    """

    def __init__(self, nombre, precio_hora, tipo_equipo, cantidad_disponible):
        self.tipo_equipo = tipo_equipo
        self.cantidad_disponible = cantidad_disponible
        super().__init__(nombre, precio_hora, "Alquiler de equipo")
        self.validar()
        log.info(f"Servicio AlquilerEquipo creado: {nombre} | tipo: {tipo_equipo}")

    def calcular_costo(self, horas):
        """Costo del equipo: precio/hora * horas"""
        try:
            if horas <= 0:
                raise ErrorCalculoCosto("Las horas deben ser un numero positivo")
            if self.cantidad_disponible <= 0:
                raise ErrorServicioNoDisponible(
                    f"No hay unidades disponibles de '{self._nombre}'"
                )
            return self._precio_hora * horas
        except (ErrorCalculoCosto, ErrorServicioNoDisponible):
            raise
        except Exception as e:
            raise ErrorCalculoCosto("Error calculando costo del equipo") from e

    def describir(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return (f"Equipo '{self._nombre}' | Tipo: {self.tipo_equipo} | "
                f"Unidades: {self.cantidad_disponible} | ${self._precio_hora:,.0f}/hora | {estado}")

    def validar(self):
        super().validar()
        if self.cantidad_disponible < 0:
            raise ErrorServicioNoDisponible(
                "La cantidad disponible no puede ser un numero negativo"
            )


#SERVICIO 3: ASESORÍA ESPECIALIZADA
class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría con expertos en distintas áreas temáticas.
    Hereda de Servicio e implementa calcular_costo() con polimorfismo.
    """

    AREAS_VALIDAS = ["tecnologia", "finanzas", "legal", "marketing", "rrhh", "contabilidad"]

    def __init__(self, nombre, precio_hora, area, nombre_asesor):
        self.area = area.lower().strip()
        self.nombre_asesor = nombre_asesor
        super().__init__(nombre, precio_hora, "Asesoria especializada")
        self.validar()
        log.info(f"Servicio AsesoriaEspecializada creado: {nombre} | area: {area}")

    def calcular_costo(self, horas):
        """Costo de asesoría: mínimo 1 hora cobrada"""
        try:
            if horas <= 0:
                raise ErrorCalculoCosto("Las horas de asesoria deben ser positivas")
            # Mínimo de facturación: 1 hora
            horas_a_cobrar = max(horas, 1)
            return self._precio_hora * horas_a_cobrar
        except ErrorCalculoCosto:
            raise
        except Exception as e:
            raise ErrorCalculoCosto("Error calculando el costo de la asesoria") from e

    def describir(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return (f"Asesoria '{self._nombre}' | Area: {self.area} | "
                f"Asesor: {self.nombre_asesor} | ${self._precio_hora:,.0f}/hora | {estado}")

    def validar(self):
        super().validar()
        if self.area not in self.AREAS_VALIDAS:
            raise ErrorServicioNoDisponible(
                f"El area '{self.area}' no es valida. "
                f"Areas disponibles: {', '.join(self.AREAS_VALIDAS)}"
            )
        if not self.nombre_asesor or len(self.nombre_asesor.strip()) < 3:
            raise ErrorServicioNoDisponible(
                "El nombre del asesor debe tener al menos 3 caracteres"
            )


#LASE RESERVA: asocia un cliente con un servicio
class Reserva(EntidadBase):
    """
    Gestiona una reserva que relaciona un Cliente con un Servicio.
    Implementa confirmación, cancelación y procesamiento con manejo de excepciones.
    """

    def __init__(self, cliente, servicio, duracion_horas, fecha="Sin fecha"):
        # Verificamos que los parámetros sean del tipo correcto
        if not isinstance(cliente, Cliente):
            raise ErrorReservaInvalida("El parametro 'cliente' debe ser una instancia de Cliente")
        if not isinstance(servicio, Servicio):
            raise ErrorReservaInvalida("El parametro 'servicio' debe ser una instancia de Servicio")

        nombre_res = f"Res-{cliente.nombre[:8]}-{servicio.nombre[:6]}"
        super().__init__(nombre_res)

        #Atributos privados con encapsulación
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = duracion_horas
        self.__estado = "pendiente"
        self.__fecha = fecha
        self.__costo_final = 0.0

        self.validar()
        log.info(
            f"Reserva #{self.id} creada | {cliente.nombre} -> "
            f"{servicio.nombre} | {duracion_horas}h | Estado: pendiente"
        )

    #Propiedades (solo lectura) ------
    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def estado(self):
        return self.__estado

    @property
    def duracion(self):
        return self.__duracion

    @property
    def costo_final(self):
        return self.__costo_final

    @property
    def fecha(self):
        return self.__fecha

    def validar(self):
        """Verifica duración y disponibilidad del servicio al crear la reserva"""
        try:
            if self.__duracion <= 0:
                raise ErrorReservaInvalida("La duracion debe ser mayor a cero horas")
            if self.__duracion > 24:
                raise ErrorReservaInvalida("No se puede reservar por mas de 24 horas seguidas")
            self.__servicio.verificar_disponibilidad()
        except (ErrorReservaInvalida, ErrorServicioNoDisponible) as e:
            log.error(f"Reserva invalida: {e}")
            raise

    def confirmar(self):
        """Confirma la reserva calculando el costo base (sin descuentos)"""
        try:
            if self.__estado == "cancelada":
                raise ErrorOperacionNoPermitida(
                    "No se puede confirmar una reserva que ya fue cancelada"
                )
            if self.__estado == "confirmada":
                raise ErrorOperacionNoPermitida("Esta reserva ya habia sido confirmada")

            self.__servicio.verificar_disponibilidad()
            self.__costo_final = self.__servicio.calcular_costo(self.__duracion)
            self.__estado = "confirmada"
            log.info(f"Reserva #{self.id} confirmada | Costo: ${self.__costo_final:,.0f}")
            return self.__costo_final

        except ErrorOperacionNoPermitida as e:
            log.error(f"Operacion no permitida - Reserva #{self.id}: {e}")
            raise
        except Exception as e:
            log.error(f"Error al confirmar reserva #{self.id}: {e}")
            # Encadenamiento de excepciones
            raise ErrorReservaInvalida("No se pudo confirmar la reserva") from e

    def cancelar(self):
        """Cancela la reserva. Usa try/except/finally para demostrar el patrón"""
        try:
            if self.__estado == "cancelada":
                raise ErrorOperacionNoPermitida("Esta reserva ya estaba cancelada anteriormente")
            self.__estado = "cancelada"
            log.info(f"Reserva #{self.id} cancelada")

        except ErrorOperacionNoPermitida as e:
            log.error(f"Intento de doble cancelacion - Reserva #{self.id}: {e}")
            raise

        finally:
            pass

    def procesar(self, con_descuento=0, con_iva=True):
        """
        Procesa la reserva con opciones de descuento e IVA.
        Demuestra el uso de los métodos sobrecargados de Servicio.
        """
        try:
            self.__servicio.verificar_disponibilidad()

            if con_iva:
                self.__costo_final = self.__servicio.calcular_costo_total(
                    self.__duracion, descuento=con_descuento
                )
            else:
                self.__costo_final = self.__servicio.calcular_costo_con_descuento(
                    self.__duracion, con_descuento
                )

            self.__estado = "confirmada"
            log.info(
                f"Reserva #{self.id} procesada | "
                f"Costo final: ${self.__costo_final:,.0f} | IVA: {con_iva}"
            )
            return self.__costo_final

        except (ErrorServicioNoDisponible, ErrorCalculoCosto) as e:
            log.error(f"Error al procesar reserva #{self.id}: {e}")
            raise
        except Exception as e:
            log.error(f"Error inesperado procesando reserva #{self.id}: {e}")
            raise

    def describir(self):
        return (
            f"Reserva #{self.id} | Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | {self.__duracion}h | "
            f"Estado: {self.__estado} | Costo: ${self.__costo_final:,.0f}"
        )

    def get_info(self):
        """Retorna los datos de la reserva como diccionario para mostrar en la tabla"""
        return {
            "id": self.id,
            "cliente": self.__cliente.nombre,
            "servicio": self.__servicio.nombre,
            "tipo_servicio": self.__servicio._tipo,
            "duracion": self.__duracion,
            "estado": self.__estado,
            "costo": self.__costo_final,
            "fecha": self.__fecha,
        }
