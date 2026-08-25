"""
server_standalone.py
=====================
UN SOLO ARCHIVO. Un solo comando. No necesitas correr nada más.

Este servidor abre el puerto Serial del Arduino él mismo (en un hilo
aparte) y expone los datos por HTTP en tiempo real. No requiere el
script ecg_sender.py ni nada intermedio.

Reproduce la lógica real de tu repo flappy_ecg_v2:
  - flappy_ecg/config.py                         -> BAUD_RATE=115200
  - flappy_ecg/serial_reader/reader.py            -> formato de línea (entero, '!' o 'X')
  - flappy_ecg/signal_processing/peak_detector.py -> UMBRAL_ACTIVACION=500, UMBRAL_DESCANSO=380, COOLDOWN_FRAMES=15

⚠️ El puerto Serial solo lo puede tener abierto un programa a la vez.
No corras esto al mismo tiempo que el juego (main.py) sobre el mismo puerto COM.

Uso:
    pip install flask pyserial
    python server_standalone.py --port COM3 --baud 115200
    # o en Linux/Mac: --port /dev/ttyACM0

Luego abre http://localhost:5000/ en el navegador.
"""

import argparse
import json
import queue
import threading
import time
from collections import deque
from threading import Lock

import serial
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# --- Mismos valores que flappy_ecg/signal_processing/peak_detector.py ---
UMBRAL_ACTIVACION = 2800
UMBRAL_DESCANSO = 2200
VENTANA_FILTRO = 10
COOLDOWN_FRAMES = 15

HISTORY_MAXLEN = 2000
history = deque(maxlen=HISTORY_MAXLEN)
state_lock = Lock()
subscribers = []

last_reading = {
    "valor": None,
    "umbral_activacion": UMBRAL_ACTIVACION,
    "umbral_descanso": UMBRAL_DESCANSO,
    "estado": "abierto",
    "salto": False,
    "electrodos_ok": False,
    "timestamp": None,
}

arduino_connected = False


def broadcast(reading):
    dead = []
    for q in subscribers:
        try:
            q.put_nowait(reading)
        except queue.Full:
            dead.append(q)
    for q in dead:
        subscribers.remove(q)


class SerialWorker(threading.Thread):
    """Hilo que lee el Arduino y actualiza last_reading, igual que reader.py + peak_detector.py."""

    def __init__(self, port, baud):
        super().__init__(daemon=True)
        self.port = port
        self.baud = baud
        self.estado = "abierto"
        self.cooldown = 0
        self.buffer_filtro = deque(maxlen=VENTANA_FILTRO)

    def run(self):
        global arduino_connected
        while True:
            try:
                print(f"[serial] Conectando a {self.port} @ {self.baud}...")
                ser = serial.Serial(self.port, self.baud, timeout=1)
                time.sleep(2)  # el Arduino Mega reinicia al abrir el puerto
                ser.reset_input_buffer()
                arduino_connected = True
                print(f"[serial] Conectado en {self.port}.")
                self._read_loop(ser)
            except serial.SerialException as e:
                arduino_connected = False
                print(f"[serial] No se pudo conectar ({e}). Reintentando en 3s...")
                time.sleep(3)

    def _read_loop(self, ser):
        global arduino_connected
        while True:
            try:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
            except serial.SerialException:
                arduino_connected = False
                print("[serial] Se perdió la conexión. Reintentando...")
                try:
                    ser.close()
                except Exception:
                    pass
                return

            if not line:
                continue

            if line in ("!", "X"):
                valor = None
            else:
                try:
                    valor = int(line)
                except ValueError:
                    continue

            estado, salto = self._update_peak(valor)

            reading = {
                "valor": valor,
                "umbral_activacion": UMBRAL_ACTIVACION,
                "umbral_descanso": UMBRAL_DESCANSO,
                "estado": estado,
                "salto": salto,
                "electrodos_ok": valor is not None,
                "timestamp": time.time(),
            }

            with state_lock:
                last_reading.update(reading)
                history.append(reading)

            broadcast(reading)

            if salto:
                print(f"[serial] SALTO detectado — ADC: {valor}")

    def _update_peak(self, valor):
        if valor is None:
            return self.estado, False

        self.buffer_filtro.append(valor)
        valor_f = sum(self.buffer_filtro) / len(self.buffer_filtro)

        if self.cooldown > 0:
            self.cooldown -= 1
            return self.estado, False

        if valor_f > UMBRAL_ACTIVACION and self.estado == "abierto":
            self.estado = "cerrado"
            self.cooldown = COOLDOWN_FRAMES
            return self.estado, True

        if valor_f < UMBRAL_DESCANSO and self.estado == "cerrado":
            self.estado = "abierto"

        return self.estado, False


@app.route("/status")
def status():
    with state_lock:
        return jsonify({
            "connected": arduino_connected,
            "last_reading": last_reading,
        })


@app.route("/threshold")
def threshold():
    with state_lock:
        return jsonify(last_reading)


@app.route("/history")
def get_history():
    n = request.args.get("n", default=100, type=int)
    with state_lock:
        data = list(history)[-n:]
    return jsonify(data)


@app.route("/stream")
def stream():
    def event_stream():
        q = queue.Queue(maxsize=50)
        subscribers.append(q)
        try:
            while True:
                reading = q.get()
                yield f"data: {json.dumps(reading)}\n\n"
        finally:
            if q in subscribers:
                subscribers.remove(q)

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Flappy ECG - Servidor standalone</title>
<style>
  body { font-family: system-ui, sans-serif; background: #0f1115; color: #eee; margin: 0; padding: 2rem; }
  h1 { color: #ff5d73; }
  .card { background: #1a1d24; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; max-width: 480px; }
  .label { color: #888; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
  .value { font-size: 2.2rem; font-weight: 700; }
  .estado-abierto { color: #4ade80; }
  .estado-cerrado { color: #f87171; }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
  .dot.on { background: #4ade80; }
  .dot.off { background: #f87171; }
</style>
</head>
<body>
  <h1>💓 Flappy ECG — Servidor standalone</h1>
  <div class="card">
    <div class="label"><span id="dot" class="dot off"></span>Conexión</div>
    <div class="value" id="conn">esperando datos...</div>
  </div>
  <div class="card">
    <div class="label">Valor ADC</div>
    <div class="value" id="valor">--</div>
  </div>
  <div class="card">
    <div class="label">Umbrales (activación / descanso)</div>
    <div class="value" id="umbrales" style="font-size:1.3rem">500 / 380</div>
  </div>
  <div class="card">
    <div class="label">Estado</div>
    <div class="value" id="estado">--</div>
  </div>
<script>
  const dot = document.getElementById('dot');
  const conn = document.getElementById('conn');
  const valor = document.getElementById('valor');
  const umbrales = document.getElementById('umbrales');
  const estado = document.getElementById('estado');

  const es = new EventSource('/stream');
  es.onmessage = (e) => {
    const d = JSON.parse(e.data);
    dot.className = 'dot ' + (d.electrodos_ok ? 'on' : 'off');
    conn.textContent = d.electrodos_ok ? 'Recibiendo datos' : 'Electrodos desconectados';
    valor.textContent = d.valor === null ? '--' : d.valor;
    umbrales.textContent = `${d.umbral_activacion} / ${d.umbral_descanso}`;
    estado.textContent = d.estado || '--';
    estado.className = 'value ' + (d.estado === 'cerrado' ? 'estado-cerrado' : 'estado-abierto');
    if (d.salto) {
      estado.textContent += ' 🦅 SALTO!';
    }
  };
  es.onerror = () => { conn.textContent = 'Sin conexión al servidor'; dot.className = 'dot off'; };
</script>
</body>
</html>
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor standalone (todo en uno) para flappy_ecg_v2")
    parser.add_argument("--port", required=True, help="Puerto serial del Arduino, ej: COM3 o /dev/ttyACM0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--http-port", type=int, default=5000)
    args = parser.parse_args()

    worker = SerialWorker(args.port, args.baud)
    worker.start()

    print(f"[server] Escuchando en http://{args.host}:{args.http_port}/")
    app.run(host=args.host, port=args.http_port, threaded=True)