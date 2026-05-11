# Excepciones personalizadas del sistema de gestión Software FJ
# Cada una representa un tipo de error específico del negocio

class ErrorClienteInvalido(Exception):
    """Se lanza cuando los datos del cliente no pasan la validación"""
    pass


class ErrorServicioNoDisponible(Exception):
    """Se lanza cuando el servicio no existe o está desactivado"""
    pass


class ErrorReservaInvalida(Exception):
    """Se lanza cuando los datos de la reserva son incorrectos"""
    pass


class ErrorDatosIncompletos(Exception):
    """Se lanza cuando faltan campos obligatorios en el formulario"""
    pass


class ErrorCalculoCosto(Exception):
    """Se lanza cuando hay un problema al calcular el precio"""
    pass


class ErrorOperacionNoPermitida(Exception):
    """Se lanza cuando se intenta hacer algo que el sistema no permite"""
    pass
