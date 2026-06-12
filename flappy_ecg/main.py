import pygame
import time
import sys
from serial_reader.reader import SerialReader
from signal_processing.peak_detector import PeakDetector
from game.game_manager import GameManager


def main():
    reader     = SerialReader()
    arduino_ok = reader.start()

    peak_detector = PeakDetector()
    game          = GameManager()
    game.set_arduino_connected(arduino_ok)
    game.set_peak_detector(peak_detector)

    running = True
    print("[Main] Juego iniciado. Esperando datos del EMG...")

    try:
        while running:
            running = game.handle_events()
            if not running:
                break

            if arduino_ok:
                raw_data = reader.get_latest_data()
                if raw_data:
                    # Alimentar la gráfica con el último valor
                    ultimo = raw_data[-1]
                    game.push_emg(ultimo)

                    current_time = int(time.time() * 1000)
                    if peak_detector.detect_peak(raw_data, current_time):
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