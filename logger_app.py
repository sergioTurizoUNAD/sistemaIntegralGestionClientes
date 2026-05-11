import datetime
import os

# Clase que maneja el registro de todos los eventos y errores del sistema
# Se guarda en un archivo de texto plano (sin base de datos)
class Logger:

    def __init__(self, ruta_archivo="logs_sistema.txt"):
        self.ruta_archivo = ruta_archivo

    def _escribir(self, nivel, mensaje):
        # Bloque try/except/finally para garantizar que el sistema no se caiga
        # aunque no se pueda escribir el log
        try:
            ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            linea = f"[{ahora}] [{nivel}] {mensaje}\n"
            with open(self.ruta_archivo, "a", encoding="utf-8") as archivo:
                archivo.write(linea)
        except OSError as e:
            # Si falla el archivo, al menos lo mostramos en consola
            print(f"[ADVERTENCIA] No se pudo escribir en el log: {e}")
        finally:
            pass

    def info(self, mensaje):
        self._escribir("INFO", mensaje)

    def error(self, mensaje):
        self._escribir("ERROR", mensaje)

    def advertencia(self, mensaje):
        self._escribir("ADVERTENCIA", mensaje)

    def leer_todos(self):
        # Retorna el contenido del archivo de logs
        try:
            if not os.path.exists(self.ruta_archivo):
                return "El archivo de logs aun no existe. Realiza algunas operaciones primero."
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
            return contenido if contenido.strip() else "El archivo de logs esta vacio."
        except OSError as e:
            return f"No se pudo leer el archivo de logs: {e}"
