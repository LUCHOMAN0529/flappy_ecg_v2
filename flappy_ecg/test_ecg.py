import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time
import numpy as np

BAUD_RATE   = 115200
BUFFER_SIZE = 500
PUERTO      = "COM3"

VENTANA_FILTRO = 8

UMBRAL_ACTIVACION  = 550
UMBRAL_DESCANSO    = 430
MIN_MUESTRAS_ENTRE = 30

estado_anterior    = "abierto"
muestras_desde_det = 0
buffer_filtro      = deque(maxlen=VENTANA_FILTRO)

try:
    ser = serial.Serial(PUERTO, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"✓ Conectado a {PUERTO}")
    print("  Abre y cierra el puño para ver la detección\n")
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
ax.axhline(y=UMBRAL_ACTIVACION, color='#ff4444',
           linewidth=1.0, linestyle='--', label=f'Umbral ({UMBRAL_ACTIVACION})')

texto_estado = ax.text(0.01, 0.95, '● Esperando...', transform=ax.transAxes,
                       color='white', fontsize=12, va='top', fontweight='bold')
texto_val    = ax.text(0.99, 0.95, '', transform=ax.transAxes,
                       color='#aaaaaa', fontsize=11, va='top', ha='right')

ax.set_xlim(0, BUFFER_SIZE)
ax.set_ylim(0, 1023)
ax.set_title('Señal EMG — Detección de contracción muscular', color='white', fontsize=13)
ax.tick_params(colors='#aaaaaa')
ax.spines[:].set_color('#333355')
ax.grid(True, color='#222244', linewidth=0.5)
ax.legend(loc='lower right', facecolor='#1a1a2e', labelcolor='white', fontsize=9)

def actualizar(frame):
    global estado_anterior, muestras_desde_det

    while ser.in_waiting > 0:
        try:
            linea_raw_txt = ser.readline().decode('utf-8', errors='ignore').strip()

            if linea_raw_txt == 'X':
                texto_estado.set_text('⚠ ELECTRODOS DESCONECTADOS')
                texto_estado.set_color('#ff4444')
                continue

            valor = int(linea_raw_txt)
            datos_raw.append(valor)

            buffer_filtro.append(valor)
            valor_f = int(np.mean(buffer_filtro))
            datos_filtrado.append(valor_f)

            muestras_desde_det += 1

            if (valor_f > UMBRAL_ACTIVACION
                    and estado_anterior == "abierto"
                    and muestras_desde_det > MIN_MUESTRAS_ENTRE):
                estado_anterior    = "cerrado"
                muestras_desde_det = 0
                print(f"✊ PUÑO CERRADO  — ADC: {valor_f}")
                texto_estado.set_text('✊ PUÑO CERRADO')
                texto_estado.set_color('#ff8800')

            elif valor_f < UMBRAL_DESCANSO and estado_anterior == "cerrado":
                estado_anterior = "abierto"
                print(f"✋ Puño abierto  — ADC: {valor_f}")
                texto_estado.set_text('✋ Puño abierto')
                texto_estado.set_color('#00ff88')

            texto_val.set_text(f'ADC: {valor_f}')

        except ValueError:
            pass

    linea_raw.set_data(range(len(datos_raw)),      list(datos_raw))
    linea_filt.set_data(range(len(datos_filtrado)), list(datos_filtrado))
    return linea_raw, linea_filt, texto_estado, texto_val

ani = animation.FuncAnimation(
    fig, actualizar, interval=20, blit=True, cache_frame_data=False
)

plt.tight_layout()
plt.show()
ser.close()
print("✓ Puerto cerrado.")