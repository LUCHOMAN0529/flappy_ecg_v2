import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time
import numpy as np

BAUD_RATE   = 115200
BUFFER_SIZE = 500
PUERTO      = "COM6"

# --- Rango real del ADC del ESP32 (12 bits, no 10 bits como el Mega) ---
ADC_MAX = 4095

# --- Filtro de media móvil (suaviza el ruido antes de comparar con el umbral) ---
VENTANA_FILTRO = 10

# --- Detección simple por umbral (igual que el Arduino original) ---
UMBRAL_ACTIVACION = 2800  # valor FILTRADO por encima de esto = SALTO
UMBRAL_DESCANSO   = 2200  # valor FILTRADO por debajo de esto = listo para el próximo salto

buffer_filtro   = deque(maxlen=VENTANA_FILTRO)
estado_puno     = "reposo"  # "reposo" | "contraido"
contador_saltos = 0

try:
    ser = serial.Serial(PUERTO, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"✓ Conectado a {PUERTO}")
    print("  Corre esto junto con ecg_diagnostico.ino (versión simplificada) en el ESP32\n")
except serial.SerialException as e:
    print(f"✗ Error: {e}")
    exit(1)

datos_raw      = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
datos_filtrado = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)

fig, ax = plt.subplots(figsize=(13, 5))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

linea_raw,  = ax.plot([], [], color='#334466', linewidth=1.0, label='Señal cruda')
linea_filt, = ax.plot([], [], color='#00ff88', linewidth=2.0, label='Filtrada')
ax.axhline(y=UMBRAL_ACTIVACION, color='#ff4444', linewidth=1.2, linestyle='--', label=f'Umbral SALTO ({UMBRAL_ACTIVACION})')
ax.axhline(y=UMBRAL_DESCANSO, color='#44ff88', linewidth=1.0, linestyle='--', label=f'Umbral reposo ({UMBRAL_DESCANSO})')

texto_estado = ax.text(0.01, 0.95, '● Esperando...', transform=ax.transAxes,
                        color='white', fontsize=12, va='top', fontweight='bold')
texto_val = ax.text(0.99, 0.95, '', transform=ax.transAxes,
                     color='#aaaaaa', fontsize=11, va='top', ha='right')
texto_saltos = ax.text(0.01, 0.85, 'Saltos: 0', transform=ax.transAxes,
                        color='#ffdd00', fontsize=12, va='top', fontweight='bold')

ax.set_xlim(0, BUFFER_SIZE)
ax.set_ylim(-100, ADC_MAX + 200)
ax.set_title('Detección de salto — señal filtrada (ESP32)', color='white', fontsize=13)
ax.set_xlabel('Muestras')
ax.tick_params(colors='#aaaaaa')
ax.spines[:].set_color('#333355')
ax.grid(True, color='#222244', linewidth=0.5)
ax.legend(loc='lower right', facecolor='#1a1a2e', labelcolor='white', fontsize=9)


def actualizar(frame):
    global estado_puno, contador_saltos

    while ser.in_waiting > 0:
        try:
            linea_txt = ser.readline().decode('utf-8', errors='ignore').strip()

            if linea_txt == '!' or linea_txt.startswith('!'):
                texto_estado.set_text('⚠ ELECTRODOS DESCONECTADOS')
                texto_estado.set_color('#ff4444')
                continue

            crudo = int(linea_txt)
            datos_raw.append(crudo)

            # --- Filtro de media móvil ---
            buffer_filtro.append(crudo)
            valor_f = int(np.mean(buffer_filtro))
            datos_filtrado.append(valor_f)

            # --- Detección por umbral SOBRE EL VALOR FILTRADO, con histéresis ---
            if valor_f > UMBRAL_ACTIVACION and estado_puno == "reposo":
                estado_puno = "contraido"
                contador_saltos += 1
                print(f"🐦 SALTO #{contador_saltos}  — filtrado: {valor_f}")
            elif valor_f < UMBRAL_DESCANSO and estado_puno == "contraido":
                estado_puno = "reposo"

            if crudo >= ADC_MAX - 5 or crudo <= 5:
                texto_estado.set_text('⚠ SEÑAL SATURADA')
                texto_estado.set_color('#ff4444')
            elif estado_puno == "contraido":
                texto_estado.set_text('✊ CONTRAÍDO — SALTO')
                texto_estado.set_color('#ff8800')
            else:
                texto_estado.set_text('● Leyendo')
                texto_estado.set_color('#00ff88')

            texto_val.set_text(f'crudo: {crudo}  |  filtrado: {valor_f}')
            texto_saltos.set_text(f'Saltos: {contador_saltos}')

        except ValueError:
            pass

    linea_raw.set_data(range(len(datos_raw)), list(datos_raw))
    linea_filt.set_data(range(len(datos_filtrado)), list(datos_filtrado))
    return linea_raw, linea_filt, texto_estado, texto_val, texto_saltos


ani = animation.FuncAnimation(
    fig, actualizar, interval=20, blit=True, cache_frame_data=False
)

plt.tight_layout()
plt.show()
ser.close()
print("✓ Puerto cerrado.")