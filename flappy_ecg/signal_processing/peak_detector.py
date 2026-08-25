# --- peak_detector.py ---
# Detección por umbral sobre señal FILTRADA (media móvil), calibrado para
# el ESP32 (ADC de 12 bits, 0-4095) con AD8232.
#
# Umbrales obtenidos calibrando en vivo con graficar_ecg.py / test_filtrado.py
# — ajusta UMBRAL_ACTIVACION / UMBRAL_DESCANSO aquí si cambias de persona,
# electrodos, o posición.

from collections import deque

VENTANA_FILTRO     = 10    # muestras para el promedio móvil (igual que en la calibración)
UMBRAL_ACTIVACION  = 2800  # valor FILTRADO por encima de esto = SALTO
UMBRAL_DESCANSO    = 2200  # valor FILTRADO por debajo de esto = listo para el próximo salto
COOLDOWN_FRAMES    = 15


class PeakDetector:
    def __init__(self):
        self.reset()

    def reset(self):
        self._estado   = "abierto"
        self._cooldown = 0
        self._buffer_filtro = deque(maxlen=VENTANA_FILTRO)
        print("[PeakDetector] Reiniciado.")

    def detect_peak(self, raw_data: list, current_time_ms: int) -> bool:
        if not raw_data:
            return False

        valor = raw_data[-1]
        if valor is None:
            return False

        # --- Filtro de media móvil (igual que en la calibración con test_filtrado.py) ---
        self._buffer_filtro.append(valor)
        valor_f = sum(self._buffer_filtro) / len(self._buffer_filtro)

        if self._cooldown > 0:
            self._cooldown -= 1
            return False

        if valor_f > UMBRAL_ACTIVACION and self._estado == "abierto":
            self._estado   = "cerrado"
            self._cooldown = COOLDOWN_FRAMES
            print(f"✊ CONTRACCIÓN — ADC filtrado: {valor_f:.0f} → ¡SALTO!")
            return True

        if valor_f < UMBRAL_DESCANSO and self._estado == "cerrado":
            self._estado = "abierto"
            print(f"✋ Reposo — ADC filtrado: {valor_f:.0f}")

        return False