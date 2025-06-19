import pyaudio
import numpy as np
import secrets
import random
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
sample_rate = 44100   # Abtastrate
clock_freq = 2900     # Frequenz für Takt
baud_rate = 20        # Zeichen pro Sekunde
key_baud_rate = 10    # Übertragungsrate für den Schlüssel
symbol_duration = 1 / baud_rate
half_duration = symbol_duration / 2
start_marker_freq = 3000  # Startmarker Frequenz
end_marker_freq = 3100    # Endmarker Frequenz
key_length = 8            # Länge des Schlüssels (Hex-Zeichen)

# Funktion, um ein Signal für eine Frequenz zu erzeugen
def generate_signal(frequency, duration):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * frequency * t)

# Funktion zum Senden der Nachricht
def shuffle_mapping(key):
    rng = random.Random(key)
    freqs = list(char_to_freq.values())
    rng.shuffle(freqs)
    mapping = dict(zip(char_to_freq.keys(), freqs))
    return mapping


def encrypt(text, key):
    rng = random.Random(key)
    encrypted = [f"{c ^ rng.randrange(256):02X}" for c in text.encode("utf-8")]
    return "".join(encrypted)


def send_chars(stream, chars, mapping, baud, bar=None):
    dur = 1 / baud
    half = dur / 2
    for ch in chars:
        freq = mapping.get(ch.upper())
        if freq is None:
            print(f"Ungültiges Zeichen '{ch}' gefunden. Wird übersprungen.")
            continue
        clock = generate_signal(clock_freq, half)
        stream.write(clock.astype(np.float32).tobytes())
        tone = generate_signal(freq, dur)
        stream.write(tone.astype(np.float32).tobytes())
        if bar:
            bar()


def send_message(message):
    key = secrets.token_hex(key_length // 2).upper()
    dynamic_map = shuffle_mapping(key)
    encrypted = encrypt(message, key)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, output=True)

    # Startsignal
    start_signal = generate_signal(start_marker_freq, half_duration)
    stream.write(start_signal.astype(np.float32).tobytes())

    # Schlüssel langsam senden
    send_chars(stream, key, char_to_freq, key_baud_rate)

    # Nochmals Startmarker vor der eigentlichen Nachricht
    stream.write(start_signal.astype(np.float32).tobytes())

    with alive_bar(len(encrypted), title="Sende", spinner="dots") as bar:
        send_chars(stream, encrypted, dynamic_map, baud_rate, bar)

    end_signal = generate_signal(end_marker_freq, half_duration)
    stream.write(end_signal.astype(np.float32).tobytes())

    stream.stop_stream()
    stream.close()
    p.terminate()
    print(f"\nNachricht erfolgreich gesendet! Schlüssel: {key}")

# Hauptprogramm
while True:
    message = input("\nGeben Sie die Nachricht ein, die gesendet werden soll: ")
    if not message.strip():
        print("Leere Nachricht. Bitte geben Sie eine gültige Nachricht ein.")
        continue

    print("Sende Nachricht...")
    send_message(message)
