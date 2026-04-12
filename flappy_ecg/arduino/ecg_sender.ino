// ============================================================
//  ecg_sender.ino — Lee el AD8232 y envía datos por Serial
//  Arduino Mega + Módulo AD8232
// ============================================================

// --- Pines del AD8232 ---
const int ECG_PIN    = A0;   // Salida analógica del AD8232
const int LO_PLUS    = 10;   // Lead-Off detection +
const int LO_MINUS   = 11;   // Lead-Off detection -

// --- Configuración ---
const int BAUD_RATE    = 115200;  // Debe coincidir con config.py
const int SAMPLE_DELAY = 2;       // ms entre muestras (~500 Hz)

void setup() {
  Serial.begin(BAUD_RATE);

  // Configurar pines de detección de electrodos
  pinMode(LO_PLUS,  INPUT);
  pinMode(LO_MINUS, INPUT);
}

void loop() {
  // Verificar si los electrodos están bien conectados
  if (digitalRead(LO_PLUS) == 1 || digitalRead(LO_MINUS) == 1) {
    // Electrodos desconectados — enviar valor nulo
    Serial.println("!");
  } else {
    // Leer señal ECG y enviarla
    int ecgValue = analogRead(ECG_PIN);
    Serial.println(ecgValue);
  }

  delay(SAMPLE_DELAY);
}