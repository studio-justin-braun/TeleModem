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
- Ein Symbol fasst zwei Zeichen zusammen. Dazu werden die entsprechenden
  Frequenzen gleichzeitig ausgesendet. Bei 20 Symbolen pro Sekunde können so
  etwa 40 Zeichen pro Sekunde übertragen werden.
- Für die Erkennung der Frequenzen kommt ein Hanning-Fenster zum Einsatz, was
  auch bei kürzeren Symboldauern stabile Ergebnisse liefert.

Weitere Details lassen sich direkt in den beiden Skripten nachlesen.
