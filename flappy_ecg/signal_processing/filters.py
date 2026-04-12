import numpy as np
from scipy.signal import butter, lfilter, iirnotch
import config as cfg

def butter_lowpass(cutoff, fs, order=5):
    """Diseña un filtro pasa-bajos tipo Butterworth."""
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):
    """Aplica el filtro pasa-bajos a los datos."""
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def notch_filter(data, cutoff, q, fs):
    """Aplica un filtro Notch para eliminar una frecuencia específica (ej. 60Hz)."""
    nyq = 0.5 * fs
    freq = cutoff / nyq
    b, a = iirnotch(freq, q)
    y = lfilter(b, a, data)
    return y

def apply_filters(data):
    """
    Función principal para procesar el array de datos del ECG.
    Aplica primero el filtro Notch y luego el pasa-bajos.
    """
    # Si no hay suficientes datos, retornar tal cual
    if len(data) < 15:
        return data

    # 1. Filtro Notch (60Hz para ruido de red eléctrica)
    notch_filtered = notch_filter(data, cutoff=60.0, q=30.0, fs=cfg.SAMPLING_RATE_HZ)

    # 2. Filtro Pasa-bajos (para quitar ruido de alta frecuencia muscular)
    final_data = lowpass_filter(notch_filtered, cutoff=cfg.FILTER_HIGH_FREQ, fs=cfg.SAMPLING_RATE_HZ, order=2)

    return final_data