# --- peak_detector.py ---
# Detector EMG simple: solo mira el último valor del buffer en cada frame.

UMBRAL_ACTIVACION  = 550
UMBRAL_DESCANSO    = 430
MIN_FRAMES_ENTRE   = 15   # frames de cooldown entre detecciones (~0.25s a 60fps)


class PeakDetector:
    def __init__(self):
        self._estado       = "abierto"
        self._cooldown     = 0

    def detect_peak(self, raw_data: list, current_time_ms: int) -> bool:
        if not raw_data:
            return False

        # Solo el último valor disponible
        valor = raw_data[-1]
        if valor is None:
            return False

        if self._cooldown > 0:
            self._cooldown -= 1

        # Detección de CIERRE
        if (valor > UMBRAL_ACTIVACION
                and self._estado == "abierto"
                and self._cooldown == 0):
            self._estado   = "cerrado"
            self._cooldown = MIN_FRAMES_ENTRE
            print(f"✊ PUÑO CERRADO  — ADC: {valor}  → ¡SALTO!")
            return True

        # Rearme
        if valor < UMBRAL_DESCANSO and self._estado == "cerrado":
            self._estado = "abierto"
            print(f"✋ Puño abierto  — ADC: {valor}")

        return False