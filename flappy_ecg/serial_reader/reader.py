# --- reader.py ---
# Hilo encargado de leer los datos del puerto serie (Arduino)

import serial
import threading
from collections import deque
import time

import config as cfg

class SerialReader:
    def __init__(self):
        self.buffer = deque(maxlen=cfg.BUFFER_SIZE)
        self.running = False
        self.connected = False
        self.serial_thread = None
        self.serial_inst = None

    def connect(self):
        """Abre la conexión con el puerto serie de Arduino."""
        print(f"[SerialReader] Intentando conectar a {cfg.SERIAL_PORT}...")
        try:
            self.serial_inst = serial.Serial(cfg.SERIAL_PORT, cfg.BAUD_RATE, timeout=1)
            time.sleep(2)  # Espera que Arduino reinicie
            self.connected = True
            print(f"[SerialReader] Conectado exitosamente en {cfg.SERIAL_PORT}.")
        except serial.SerialException as e:
            self.connected = False
            print(f"[SerialReader] Arduino no detectado en {cfg.SERIAL_PORT}. Modo simulación activado.")

    def start(self) -> bool:
        """
        Inicia la lectura del puerto serie en un hilo separado.
        RETORNA True si el Arduino está conectado, False en caso contrario.
        """
        if not self.connected:
            self.connect()

        if self.connected:
            self.running = True
            self.serial_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.serial_thread.start()
            print("[SerialReader] Hilo de lectura iniciado.")
            return True          # ← FIX: retornar True cuando conecta OK

        return False             # ← FIX: retornar False si no hay Arduino

    def stop(self):
        """Detiene la lectura y cierra el hilo."""
        self.running = False
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=2)
        if self.serial_inst and self.serial_inst.is_open:
            self.serial_inst.close()
        print("[SerialReader] Lectura detenida y puerto cerrado.")

    def _update_loop(self):
        """Bucle principal de lectura que corre en el hilo separado."""
        self.serial_inst.reset_input_buffer()

        while self.running:
            try:
                if self.serial_inst and self.serial_inst.in_waiting > 0:
                    line = self.serial_inst.readline().decode('utf-8', errors='ignore').strip()

                    if not line:
                        continue

                    if line == '!' or line == 'X':
                        self.buffer.append(None)
                    else:
                        try:
                            value = int(line)
                            self.buffer.append(value)
                        except ValueError:
                            pass
            except Exception as e:
                print(f"[SerialReader] Error en hilo: {e}")
                self.running = False

            time.sleep(0.001)

    def get_latest_data(self):
        """Retorna una copia del buffer actual como una lista."""
        return list(self.buffer)

    def is_electrodes_connected(self):
        """Verifica el último dato para saber si los electrodos están puestos."""
        if not self.buffer:
            return False
        return self.buffer[-1] is not None
