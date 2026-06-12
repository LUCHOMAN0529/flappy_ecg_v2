# --- peak_detector.py ---
# VERSION SIMPLE: solo raw_data[-1], sin manejo de indices
UMBRAL_ACTIVACION = 500
UMBRAL_DESCANSO   = 380
COOLDOWN_FRAMES   = 15

class PeakDetector:
    def __init__(self):
        self.reset()

    def reset(self):
        self._estado   = "abierto"
        self._cooldown = 0
        print("[PeakDetector] Reiniciado.")

    def detect_peak(self, raw_data: list, current_time_ms: int) -> bool:
        if not raw_data:
            return False

        valor = raw_data[-1]
        if valor is None:
            return False

        if self._cooldown > 0:
            self._cooldown -= 1
            return False

        if valor > UMBRAL_ACTIVACION and self._estado == "abierto":
            self._estado   = "cerrado"
            self._cooldown = COOLDOWN_FRAMES
            print(f"✊ PUÑO CERRADO — ADC: {valor} → ¡SALTO!")
            return True

        if valor < UMBRAL_DESCANSO and self._estado == "cerrado":
            self._estado = "abierto"
            print(f"✋ Puño abierto — ADC: {valor}")

        return False