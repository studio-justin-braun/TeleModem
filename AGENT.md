# Anleitung für Codex-Agenten

Dieses Repository enthält zwei Python-Skripte (*sender.py* und *receiver.py*),
die Audiofrequenzen zur Übertragung von Text verwenden. Beim Bearbeiten des Codes
sollten folgende Hinweise beachtet werden:

- Kommentare und Ausgaben sind auf Deutsch gehalten und sollten so belassen
  werden.
- Verwende Python 3 und halte dich an den bestehenden Stil (keine externen
  Frameworks einführen).
- Nach jeder Änderung muss ein Syntaxcheck durchgeführt werden:

```bash
python -m py_compile sender.py receiver.py
```

- Es gibt keine weiteren automatischen Tests. Stelle sicher, dass die Skripte
  weiterhin direkt startbar sind.
