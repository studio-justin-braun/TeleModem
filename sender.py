import pyaudio
import numpy as np
from alive_progress import alive_bar

# Frequenzzuweisung für Zeichen
char_to_freq = {
    'A': 400, 'B': 440, 'C': 480, 'D': 520, 'E': 560, 'F': 600, 'G': 640, 'H': 680,
    'I': 720, 'J': 760, 'K': 800, 'L': 840, 'M': 880, 'N': 920, 'O': 960, 'P': 1000,
    'Q': 1040, 'R': 1080, 'S': 1120, 'T': 1160, 'U': 1200, 'V': 1240, 'W': 1280, 'X': 1320,
    'Y': 1360, 'Z': 1400, 'Ä': 1440, 'Ö': 1480, 'Ü': 1520, 'ß': 1560, '?': 1600, '1': 1640,
    '2': 1680, '3': 1720, '4': 1760, '5': 1800, '6': 1840, '7': 1880, '8': 1920, '9': 1960,
    '0': 2000, '.': 2040, ',': 2080, ':': 2120, '-': 2160, "'": 2200, '(': 2240, ')': 2280,
    '=': 2320, ' ': 2360, '\\': 2400
}
freq_to_char = {v: k for k, v in char_to_freq.items()}  # Inverse Zuordnung für den Empfänger

# Parameter
sample_rate = 44100  # Abtastrate
clock_freq = 2900  # Frequenz für Takt
baud_rate = 10     # Baudrate in Zeichen pro Sekunde
start_marker_freq = 3000  # Startmarker Frequenz
end_marker_freq = 3100   # Endmarker Frequenz

# Funktion, um ein Signal für eine Frequenz zu erzeugen
def generate_signal(frequency, duration):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * frequency * t)

# Funktion zum Senden der Nachricht
def send_message(message):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True)
    message = message.replace("ß", "SS").replace("!", ".")   # Ersetze "ß" durch "SS" und "!" durch "."
    total_chars = len(message)

    # Vorverarbeitung der Nachricht:
    # Sende Startmarker
    start_signal = generate_signal(start_marker_freq, 1 / (2 * baud_rate))
    stream.write(start_signal.astype(np.float32).tobytes())

    with alive_bar(total_chars, title="Sende", spinner="dots") as bar:
        for char in message:
            # Zeichen in Frequenz umwandeln
            char_freq = char_to_freq.get(char.upper(), None)  # Umwandeln auf Großbuchstaben und prüfen
            if char_freq is None:
                print(f"Ungültiges Zeichen '{char}' gefunden. Wird übersprungen.")
                continue  # Ungültige Zeichen überspringen

            # Sende Takt-Signal
            clock_signal = generate_signal(clock_freq, 1 / (2 * baud_rate))
            stream.write(clock_signal.astype(np.float32).tobytes())

            # Sende Zeichen-Frequenz
            char_signal = generate_signal(char_freq, 1 / baud_rate)
            stream.write(char_signal.astype(np.float32).tobytes())

            # Fortschrittsanzeige aktualisieren
            bar()

    # Sende Endmarker
    end_signal = generate_signal(end_marker_freq, 1 / baud_rate)
    stream.write(end_signal.astype(np.float32).tobytes())

    stream.stop_stream()
    stream.close()
    p.terminate()
    print("\nNachricht erfolgreich gesendet!")

# Hauptprogramm
while True:
    message = input("\nGeben Sie die Nachricht ein, die gesendet werden soll: ")
    if not message.strip():
        print("Leere Nachricht. Bitte geben Sie eine gültige Nachricht ein.")
        continue

    print("Sende Nachricht...")
    send_message(message)
