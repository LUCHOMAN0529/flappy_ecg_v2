# Flappy ECG

Videojuego tipo Flappy Bird que se controla con la contracción del antebrazo. Un sensor ECG/EMG (AD8232) capta la señal muscular, un microcontrolador la envía por puerto serial a Python y el pájaro salta cuando el usuario cierra la mano. Sirve como pausa activa gamificada para trabajadores de oficina y, a futuro, como base para detectar señales de síndrome del túnel carpiano.

Proyecto integrador de Ingeniería de Software, desarrollado con Scrum por el **Equipo Pulso Alado**.

## Cómo funciona

1. Los electrodos en el antebrazo captan la actividad eléctrica del músculo.
2. El sensor AD8232 amplifica la señal y el microcontrolador (ESP32 en la configuración actual) la lee por su entrada analógica.
3. Python recibe los datos por puerto serial (115200 baudios).
4. Se filtra la señal y se detecta la contracción.
5. Al detectar la contracción, el pájaro salta; al relajar la mano, cae.

```
Antebrazo -> Electrodos -> AD8232 -> ESP32 -> Serial -> Python (filtro + detección) -> Juego (pygame)
```

## Estructura del proyecto

Todo el código está en la carpeta `flappy_ecg/`.

| Ruta | Qué contiene |
| --- | --- |
| `main.py` | Punto de entrada: conecta el lector serial, el detector de picos y el juego, y ejecuta el ciclo principal. |
| `config.py` | Constantes: puerto serial, baudios, filtros, tamaño de pantalla, física del pájaro y tuberías. |
| `serial_reader/reader.py` | Lee los datos del puerto serial (`SerialReader`). |
| `signal_processing/filters.py` | Filtros de la señal. |
| `signal_processing/peak_detector.py` | Detección de contracciones (`PeakDetector`). |
| `game/` | Lógica del juego: pájaro, tuberías, fondo, pantallas, puntaje y gestor del juego (`game_manager.py`). |
| `game/emg_widget.py` | Widget que muestra la señal muscular en pantalla. |
| `arduino/` | Código del microcontrolador que envía la señal por serial. |
| `images/`, `sounds/` | Recursos gráficos y de sonido. |
| `test_ecg.py` | Script de prueba: grafica la señal en vivo, aplica media móvil y cuenta saltos. |
| `server_standalone.py` | Servidor Flask que expone la señal por HTTP (panel web, `/status`, `/history`, `/stream`). |
| `high_score.json` | Puntaje máximo guardado. |

## Requisitos

- Python 3
- Sensor ECG/EMG AD8232 con electrodos, y un microcontrolador conectado por USB
- Librerías: `pygame`, `pyserial`, `matplotlib` (para `test_ecg.py`) y `flask` (para `server_standalone.py`)

```bash
pip install pygame pyserial matplotlib flask
```

## Cómo ejecutarlo

1. Carga en el microcontrolador el código de la carpeta `arduino/`.
2. En `flappy_ecg/config.py`, cambia `SERIAL_PORT` por el puerto de tu equipo (por defecto `COM6`).
3. Coloca los electrodos en el antebrazo.
4. Ejecuta el juego:

```bash
cd flappy_ecg
python main.py
```

Para ver la señal sin el juego, usa `python test_ecg.py` (actualiza `PUERTO` dentro del archivo).

Nota: solo un programa puede usar el puerto serial a la vez. No ejecutes `main.py` y `server_standalone.py` al mismo tiempo en el mismo puerto.

## Parámetros principales (`config.py`)

| Parámetro | Valor | Significado |
| --- | --- | --- |
| `SERIAL_PORT` | `COM6` | Puerto del microcontrolador |
| `BAUD_RATE` | 115200 | Velocidad de comunicación |
| `SAMPLING_RATE_HZ` | 100 | Muestras por segundo |
| `FILTER_LOW_FREQ` / `FILTER_HIGH_FREQ` | 0.5 Hz / 40 Hz | Filtro para reducir el ruido |
| `PEAK_THRESHOLD_REL` | 0.6 | Umbral relativo para detectar la contracción |
| `JUMP_FORCE` | -14 | Fuerza del salto |
| `PIPE_GAP_SIZE` | 220 px | Espacio entre tuberías |

## Metodología: Scrum

- **Product Owner:** Luis Carlo Daza Ospino
- **Scrum Master:** Jorge Luis González Arroyo
- **Developers:** Rafael Eduardo May Recuero, Jean Marco Oyola De Martino, José Leonardo, Cristian David Diaz España

**Product Goal:** Para los trabajadores de oficina y las áreas de SST, lograremos que al menos el 80% de las pausas activas gamificadas se completen, mediante el control de Flappy ECG con la contracción y relajación del antebrazo, de modo que se reduzca la fatiga muscular y el riesgo de lesiones por movimientos repetitivos.

**Sprint 1 (terminado):**

- Sprint Goal: el trabajador controla el salto del pájaro cerrando el puño, con la señal muscular del antebrazo.
- Historias en Done: captura de la señal muscular (8 pts) y salto del pájaro con el puño cerrado (5 pts).

**Siguiente Sprint:** calibración del umbral por usuario, filtro de ruido, puntaje en pantalla y registro de sesiones para SST.

**Definition of Done:** criterios de aceptación verificados, código revisado, pruebas superadas, sin defectos críticos conocidos, documentación actualizada y funcionando en una demostración.

**Tablero:** [enlace al tablero, por completar]

## Reglas de trabajo

- Cada cambio de código se vincula a una historia del backlog en el mensaje del commit.
- Se trabaja en ramas cortas y se integra con pull request revisado por otro integrante.
- No se suben contraseñas ni credenciales al repositorio.

## Aplicaciones a futuro

- Calibración del umbral de contracción por usuario.
- Registro de sesiones para que SST mida la adherencia a las pausas.
- Análisis de la tendencia de la señal muscular para apoyar la detección temprana del síndrome del túnel carpiano (requiere validación con profesionales de la salud).
- Modo de relajación para aliviar el estrés durante la pausa.
  
