# TeleModem

TeleModem ist ein einfaches Python-Projekt, das Textnachrichten über akustische
Frequenzen überträgt. Das Repository enthält zwei Skripte:

* **sender.py**  – kodiert eine eingegebene Nachricht in Tonsignale und gibt sie
  über das Wiedergabegerät aus.
* **receiver.py** – empfängt Tonsignale vom Mikrofon, dekodiert die
  Frequenzen und stellt daraus die ursprüngliche Nachricht wieder her.

## Voraussetzungen

- Python 3.8 oder neuer
- Abhängigkeiten: `pyaudio`, `numpy` und `alive_progress`

`pyaudio` benötigt PortAudio. Unter Linux kann dies je nach Distribution
zusätzliche Systempakete erfordern. Beispiel für Debian/Ubuntu:

```bash
sudo apt-get install portaudio19-dev
pip install pyaudio numpy alive_progress
```

## Verwendung

1. **Empfänger starten**
   ```bash
   python receiver.py
   ```
   Das Skript wartet auf ein Startsignal und zeigt eingehende Zeichen an.
2. **Sender starten**
   ```bash
   python sender.py
   ```
   Nach Aufforderung eine Nachricht eingeben. Diese wird Zeichen für Zeichen als
   Tonfolge ausgegeben. Bei erfolgreichem Empfang erscheint die komplette
   Nachricht im Empfängerfenster.

## Funktionsweise in Kürze

- Jedem unterstützten Zeichen ist eine eindeutige Frequenz im Bereich 400–2400 Hz
  zugeordnet.
- Vor jedem Symbol wird ein Taktsignal (2900 Hz) ausgegeben, damit der
  Empfänger die darauffolgende Information richtig zuordnet.
- Eine Übertragung beginnt mit einem Startmarker (3000 Hz) und endet mit einem
  Endmarker (3100 Hz).
- Der Sender überträgt zu Beginn einen zufälligen achtstelligen Schlüssel mit
  10 Zeichen pro Sekunde. Dieser Schlüssel legt eine zufällige Zuordnung der
  Zeichen zu den verfügbaren Frequenzen fest und dient gleichzeitig der
  Verschlüsselung des Textes.
- Die eigentliche Nachricht wird anschließend mit 20 Zeichen pro Sekunde
  übertragen. Pro Symbol wird nur eine Frequenz gesendet.
- Für die Erkennung der Frequenzen kommt ein Hanning-Fenster zum Einsatz, was
  auch bei kürzeren Symboldauern stabile Ergebnisse liefert.

Weitere Details lassen sich direkt in den beiden Skripten nachlesen.
