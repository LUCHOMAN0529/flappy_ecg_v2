# --- config.py ---
# Parámetros globales del proyecto Flappy ECG

import collections

# --- Configuración Puerto Serie (Arduino) ---
SERIAL_PORT = "COM3"
BAUD_RATE = 115200

# --- Parámetros de Adquisición y Procesamiento de Señal ---
BUFFER_SIZE = 1000
SAMPLING_RATE_HZ = 100

FILTER_LOW_FREQ = 0.5
FILTER_HIGH_FREQ = 40

PEAK_MIN_DIST = 250
PEAK_THRESHOLD_REL = 0.6

# --- Parámetros del Juego (Físicas y Visuales) ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

GRAVITY_ACCEL = 0.8
JUMP_FORCE = -14
MAX_UP_VELOCITY = -15

PIPE_WIDTH = 80
PIPE_GAP_SIZE = 220
PIPE_DISTANCE_MS = 1500

# --- Reinicio automático tras Game Over (segundos) ---
GAME_OVER_WAIT_SECONDS = 5

# --- Historial de partidas ---
MAX_HISTORY = 5

# --- Archivo de puntuación máxima ---
HIGH_SCORE_FILE = "high_score.json"

# --- Definición de Colores (RGB) ---
COLOR_SKY_BLUE       = (135, 206, 235)
COLOR_YELLOW_BIRD    = (255, 220, 50)
COLOR_GREEN_PIPE     = (83,  160, 58)
COLOR_WHITE          = (255, 255, 255)
COLOR_GROUND_ARENA   = (222, 184, 135)
COLOR_RED_ERROR      = (255,  50,  50)
COLOR_GOLD           = (255, 215,   0)
COLOR_DARK_OVERLAY   = (0,     0,   0)   # se usa con alpha
COLOR_HEART_RED      = (220,  30,  60)
COLOR_HEART_PINK     = (255, 120, 150)
COLOR_GRAY           = (180, 180, 180)
COLOR_GREEN_OK       = (80,  200,  80)
