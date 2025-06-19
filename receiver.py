import pyaudio
import numpy as np
import random

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
sample_rate = 44100   # Abtastrate
clock_freq = 2900     # Frequenz für Takt
baud_rate = 20        # Zeichen pro Sekunde
key_baud_rate = 10    # Übertragungsrate für den Schlüssel
symbol_duration = 1 / baud_rate
half_duration = symbol_duration / 2
tolerance = 20        # Toleranz für Frequenzabgleich
samples_per_half = int(sample_rate * half_duration)
key_symbol_duration = 1 / key_baud_rate
key_half_duration = key_symbol_duration / 2
key_length = 8        # Länge des Schlüssels (Hex-Zeichen)
start_marker_freq = 3000  # Startmarker Frequenz
end_marker_freq = 3100   # Endmarker Frequenz

# Funktion, um Frequenzen zu erkennen
def detect_frequencies(signal, n=1):
    window = np.hanning(len(signal))
    fft = np.fft.rfft(signal * window)
    frequencies = np.fft.rfftfreq(len(signal), 1 / sample_rate)
    magnitudes = np.abs(fft)
    top_indices = magnitudes.argsort()[-n:][::-1]
    return [frequencies[i] for i in top_indices]

# Funktion, um Zeichen anhand der Frequenz zu identifizieren
def match_char(frequency, mapping=freq_to_char):
    for freq, char in mapping.items():
        if abs(freq - frequency) <= tolerance:
            return char
    return None


def build_freq_map(key):
    rng = random.Random(key)
    freqs = list(char_to_freq.values())
    rng.shuffle(freqs)
    return {freqs[i]: list(char_to_freq.keys())[i] for i in range(len(freqs))}


def decrypt(hex_text, key):
    """Entschlüsselt einen Hex-String mit dem übergebenen Schlüssel."""
    # Nur gültige Hex-Zeichen verwenden, da Störungen einzelne Zeichen
    # verfälschen können.
    filtered = "".join(ch for ch in hex_text if ch.upper() in "0123456789ABCDEF")
    # Ungerade Länge abschneiden, sonst schlägt fromhex fehl
    if len(filtered) % 2:
        filtered = filtered[:-1]
    rng = random.Random(key)
    data = bytes.fromhex(filtered)
    result = bytes(b ^ rng.randrange(256) for b in data)
    return result.decode("utf-8", errors="ignore")

# Funktion zum Empfang der Nachricht
def receive_message():
    p = pyaudio.PyAudio()
    buffer_size = int(sample_rate * max(half_duration, key_half_duration))
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate,
                    input=True, frames_per_buffer=buffer_size)
    print("\nWarte auf Nachricht...")

    mode = "idle"
    key_chars = ""
    encrypted = ""
    freq_map = None

    while True:
        data = np.frombuffer(stream.read(buffer_size, exception_on_overflow=False), dtype=np.int16)
        freq = detect_frequencies(data, 1)[0]

        if mode == "idle":
            if abs(freq - start_marker_freq) <= tolerance:
                mode = "read_key_clock"
                key_chars = ""
            continue

        if mode == "read_key_clock":
            if abs(freq - start_marker_freq) <= tolerance and len(key_chars) >= key_length:
                freq_map = build_freq_map(key_chars)
                encrypted = ""
                mode = "message_clock"
                print(f"Schlüssel erhalten: {key_chars}")
                continue
            if abs(freq - clock_freq) <= tolerance:
                data = np.frombuffer(stream.read(int(sample_rate * key_half_duration), exception_on_overflow=False), dtype=np.int16)
                f2 = detect_frequencies(data, 1)[0]
                ch = match_char(f2)
                if ch:
                    key_chars += ch
            continue

        if mode == "message_clock":
            if abs(freq - end_marker_freq) <= tolerance:
                if encrypted:
                    text = decrypt(encrypted, key_chars)
                    print(f"\nEmpfangene Nachricht: {text}")
                mode = "idle"
                continue
            if abs(freq - clock_freq) <= tolerance:
                data = np.frombuffer(stream.read(samples_per_half, exception_on_overflow=False), dtype=np.int16)
                f2 = detect_frequencies(data, 1)[0]
                ch = match_char(f2, freq_map)
                if ch:
                    encrypted += ch
                    print(f"Empfangen: {encrypted}", end="\r", flush=True)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Start des Empfangsskripts
receive_message()
