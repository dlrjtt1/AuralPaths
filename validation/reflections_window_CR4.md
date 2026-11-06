# CR4: first-order reflections, timing-tolerant check (browser engine, BRAS fitted materials)

Isolated first-order reflections: 28. 500 Hz - 2 kHz, dB re direct sound. Background (4 ms window, random times 5 - 45 ms): -9.5 dB. Random-time control: 1 ms window median -17.3 dB, max within +-1.5 ms median -12.2 dB (bias of the max search +5.1 dB, so the max is used for timing only).

| material | n | pred - point (median) | pred - wide (median) | wide n/a | offset median (ms) | offset IQR (ms) |
|---|---|---|---|---|---|---|
| whitePanels | 16 | +6.3 | +0.2 | 0 | +0.63 | -1.06 ... +1.06 |
| brickwall | 7 | +1.1 | +3.3 | 0 | +0.00 | +0.00 ... +0.25 |
| concrete | 4 | +3.5 | -1.9 | 0 | -1.12 | -1.31 ... -0.81 |
| seating | 1 | +8.9 | +2.1 | 0 | +1.50 | +1.50 ... +1.50 |
| all | 28 | +4.9 | +0.2 | 0 | | |

## Reflections

| pair | t (ms) | material | pred | point | wide | offset (ms) |
|---|---|---|---|---|---|---|
| LS1-MP5 | 18.3 | brickwall | -4.4 | -6.5 | -7.7 | +0.25 |
| LS1-MP2 | 28.9 | brickwall | -5.3 | -6.2 | -5.8 | +0.00 |
| LS1-MP4 | 29.9 | brickwall | -9.6 | -10.8 | -13.5 | +0.00 |
| LS1-MP3 | 34.1 | brickwall | -5.7 | -5.7 | -4.5 | -0.25 |
| LS2-MP4 | 34.9 | brickwall | -6.6 | -6.4 | -5.3 | +0.00 |
| LS1-MP1 | 39.8 | brickwall | -11.2 | -12.8 | -16.2 | +0.25 |
| LS1-MP3 | 44.1 | brickwall | -11.6 | -13.9 | -22.8 | +0.75 |
| LS2-MP3 | 36.2 | concrete | -10.0 | -19.3 | -7.5 | -1.50 |
| LS1-MP2 | 37.7 | concrete | -11.2 | -16.1 | -9.9 | -1.25 |
| LS1-MP5 | 49.8 | concrete | -12.8 | -14.8 | -9.3 | -1.00 |
| LS1-MP3 | 49.8 | concrete | -13.0 | -10.7 | -12.6 | -0.25 |
| LS1-MP4 | 2.5 | seating | -6.8 | -15.7 | -8.9 | +1.50 |
| LS2-MP5 | 15.7 | whitePanels | -3.6 | -9.6 | -7.9 | +0.75 |
| LS1-MP2 | 19.7 | whitePanels | -4.3 | -10.4 | -12.4 | +0.50 |
| LS2-MP2 | 20.4 | whitePanels | -10.2 | -14.1 | -4.8 | +1.00 |
| LS1-MP2 | 21.7 | whitePanels | -3.2 | -13.6 | -3.8 | +1.00 |
| LS1-MP3 | 23.1 | whitePanels | -4.4 | -13.7 | -9.8 | +1.25 |
| LS1-MP3 | 25.8 | whitePanels | -4.8 | -13.9 | -9.4 | -1.25 |
| LS2-MP4 | 26.0 | whitePanels | -7.6 | -14.0 | -6.5 | -1.00 |
| LS1-MP5 | 27.9 | whitePanels | -5.2 | -13.4 | -5.9 | +1.25 |
| LS1-MP1 | 28.7 | whitePanels | -6.8 | -14.5 | -6.6 | -1.25 |
| LS2-MP3 | 28.9 | whitePanels | -7.2 | -16.6 | -13.3 | +1.25 |
| LS1-MP3 | 29.3 | whitePanels | -9.6 | -14.7 | -11.2 | +1.50 |
| LS1-MP4 | 31.7 | whitePanels | -9.1 | -11.8 | -7.1 | +0.50 |
| LS1-MP1 | 35.4 | whitePanels | -12.4 | -20.0 | -9.8 | -1.50 |
| LS1-MP5 | 37.0 | whitePanels | -10.2 | -15.0 | -8.9 | +0.75 |
| LS1-MP4 | 37.3 | whitePanels | -10.7 | -12.4 | -6.1 | +0.50 |
| LS1-MP4 | 39.9 | whitePanels | -10.9 | -13.0 | -9.0 | -1.50 |
