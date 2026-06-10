# --- main.py ---
import pygame
import sys
import time
from serial_reader.reader import SerialReader
from signal_processing.peak_detector import PeakDetector
from game.game_manager import GameManager

def main():
    pygame.init()
    
    reader     = SerialReader()
    arduino_ok = reader.start()   # True si conectó en COM3, False si no
 
    peak_detector = PeakDetector()
    game          = GameManager()
    game.set_arduino_connected(arduino_ok)
 
    running = True
    print("[Main] Juego iniciado. Esperando datos del EMG sin filtros de ECG...")
 
    try:
        while running:
            # 1. Gestión de eventos nativa (Evita que el juego se cierre solo)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Mantenemos el soporte de teclado por si acaso
                        game.ecg_jump()
 
            if not running:
                break
 
            # 2. Lectura EMG desde el buffer del Arduino
            if arduino_ok:
                raw_data = reader.get_latest_data()
                if raw_data:
                    current_time = int(time.time() * 1000)
                    # Llamamos al detector que analiza la última muestra limpia
                    if peak_detector.detect_peak(raw_data, current_time):
                        game.ecg_jump()
 
            # 3. Actualización del motor gráfico del juego
            game.update()
            game.draw()
            game.tick()
 
    except KeyboardInterrupt:
        print("Interrupción por teclado.")
    finally:
        # Aseguramos el cierre limpio del puerto serie al salir
        if arduino_ok:
            reader.stop()
        pygame.quit()
        sys.exit()
 
if __name__ == "__main__":
    main()