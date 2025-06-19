import pyaudio
import numpy as np

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
freq_to_char = {v: k for k, v in char_to_freq.items()}  # Inverse Zuordnung

# Parameter
sample_rate = 44100  # Abtastrate
clock_freq = 2900  # Frequenz für Takt
baud_rate = 10     # Baudrate in Zeichen pro Sekunde
tolerance = 20     # Toleranz für Frequenzabgleich
start_marker_freq = 3000  # Startmarker Frequenz
end_marker_freq = 3100   # Endmarker Frequenz

# Funktion, um Frequenzen zu erkennen
def detect_frequency(signal):
    fft = np.fft.fft(signal)
    frequencies = np.fft.fftfreq(len(fft), 1 / sample_rate)
    magnitudes = np.abs(fft)
    index_max = np.argmax(magnitudes)
    detected_freq = abs(frequencies[index_max])
    return detected_freq

# Funktion, um Zeichen anhand der Frequenz zu identifizieren
def match_char(frequency):
    for freq, char in freq_to_char.items():
        if abs(freq - frequency) <= tolerance:
            return char
    return None

# Funktion zum Empfang der Nachricht
def receive_message():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=512)
    print("\nWarte auf Nachricht...")

    message = []
    clock_detected = False

    while True:
        data = np.frombuffer(stream.read(2048), dtype=np.int16)
        detected_freq = detect_frequency(data)

        # Prüfen auf Startmarker
        if abs(detected_freq - start_marker_freq) <= tolerance:
            print("Nachricht empfangen!")
            message = []  # Zurücksetzen der Nachricht
            continue

        # Prüfen auf Endmarker
        if abs(detected_freq - end_marker_freq) <= tolerance:
            print("\nEmpfangene Nachricht:", ''.join(message))
            message = []  # Zurücksetzen für neue Nachrichten
            continue

        # Prüfen auf Clock-Signal
        if abs(detected_freq - clock_freq) <= tolerance:
            clock_detected = True
            continue

        # Zeichen identifizieren, wenn ein Clock-Signal erkannt wurde
        if clock_detected:
            char = match_char(detected_freq)
            clock_detected = False

            if char:
                message.append(char)
                print(f"Empfangen: {char}", end="\r", flush=True)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Start des Empfangsskripts
receive_message()
