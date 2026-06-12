# --- peak_detector.py ---
UMBRAL_ACTIVACION  = 500   # Bajado a 500 - ajustar según tu señal
UMBRAL_DESCANSO    = 380   # Bajado proporcionalmente
MIN_FRAMES_ENTRE   = 12    # Reducido para ser más responsivo


class PeakDetector:
    def __init__(self):
        self.reset()

    def reset(self):
        self._estado   = "abierto"
        self._cooldown = 0
        print(f"[PeakDetector] Reiniciado. Umbral: {UMBRAL_ACTIVACION}")

    def detect_peak(self, raw_data: list, current_time_ms: int) -> bool:
        if not raw_data:
            return False

        valor = raw_data[-1]
        if valor is None:
            return False

        if self._cooldown > 0:
            self._cooldown -= 1

        if (valor > UMBRAL_ACTIVACION
                and self._estado == "abierto"
                and self._cooldown == 0):
            self._estado   = "cerrado"
            self._cooldown = MIN_FRAMES_ENTRE
            print(f"✊ PUÑO CERRADO  — ADC: {valor}  → ¡SALTO!")
            return True

        if valor < UMBRAL_DESCANSO and self._estado == "cerrado":
            self._estado = "abierto"
            print(f"✋ Puño abierto  — ADC: {valor}")

        return False