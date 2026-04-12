import numpy as np
import config as cfg

class PeakDetector:
    def __init__(self):
        self.last_peak_time = 0
        self.threshold = 0.0

    def detect_peak(self, filtered_data, current_time_ms):
        """
        Analiza los datos más recientes para detectar un latido.
        Retorna True si detecta un pico R válido, False en caso contrario.
        """
        if len(filtered_data) < 50:
            return False

        # Usar una ventana de las últimas 50 muestras para el análisis
        window = filtered_data[-50:]
        max_val = np.max(window)
        mean_val = np.mean(window)

        # Calcular un umbral dinámico basado en la media y el máximo reciente
        self.threshold = mean_val + (max_val - mean_val) * cfg.PEAK_THRESHOLD_REL

        # Tomar el valor más reciente para evaluarlo
        latest_val = filtered_data[-1]

        # Verificar si el valor superó el umbral
        if latest_val > self.threshold:
            # Verificar si ha pasado suficiente tiempo desde el último latido
            if (current_time_ms - self.last_peak_time) > cfg.PEAK_MIN_DIST:
                self.last_peak_time = current_time_ms
                return True

        return False