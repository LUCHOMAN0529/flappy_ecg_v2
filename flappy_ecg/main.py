import pygame
import time
import sys
from serial_reader.reader import SerialReader
from signal_processing.filters import apply_filters
from signal_processing.peak_detector import PeakDetector
from game.game_manager import GameManager


def main():
    reader        = SerialReader()
    arduino_ok    = reader.start()          # True si el puerto abrió bien

    peak_detector = PeakDetector()
    game          = GameManager()
    game.set_arduino_connected(arduino_ok)

    running = True
    print("[Main] Juego iniciado. Esperando datos del ECG...")

    try:
        while running:
            running = game.handle_events()
            if not running:
                break

            # Leer ECG solo si el Arduino está conectado
            if arduino_ok:
                raw_data   = reader.get_latest_data()
                valid_data = [x for x in raw_data if x is not None]

                if len(valid_data) > 0:
                    filtered_data = apply_filters(valid_data)
                    current_time  = int(time.time() * 1000)
                    if peak_detector.detect_peak(filtered_data, current_time):
                        game.ecg_jump()

            game.update()
            game.draw()
            game.tick()

    except KeyboardInterrupt:
        print("Interrupción por teclado.")
    finally:
        if arduino_ok:
            reader.stop()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
