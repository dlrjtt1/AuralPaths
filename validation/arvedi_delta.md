# Arvedi: change of the room criteria between two sources, measured vs simulated (2026-11-12, post hoc)

Question: when the source changes, does the simulation get the size of the change of EDT, C80, D50 and Ts right, even
where the absolute values are off? Delta = metric(S_k) - metric(S0) at the same receiver (S0: dodecahedron at the stage
centre; S1 - S4: Genelec 8020C loudspeakers at the quartet positions, aimed at the audience; EDT as ratio in %), for
the 65 receivers. Engine after the directional-source fixes of 2026-11-12 (CHANGELOG). Script:
[arvedi_delta.py](arvedi_delta.py); data and model as [arvedi_check.md](arvedi_check.md) (post hoc run, simplified
model, uniform calibration). **This is a change of source (type and position), not of a reinforcement delay or level.**

Means over S1 - S4 of the per-source values (ranges over the four sources in brackets); error = simulated - measured
delta; "within" = share of receivers within one JND (EDT 5 %, C80 1 dB, D50 0.05, Ts 10 ms); r = correlation of
measured and simulated delta over the receivers.

| | band | measured delta | simulated delta | mean error | rms error | within 1 JND | r |
|---|---|---|---|---|---|---|---|
| C80 | 500 Hz | +1.3 ... +1.6 dB | +1.2 ... +1.8 dB | -0.2 ... +0.3 dB | 1.0 - 1.3 dB | 51 - 69 % | 0.45 - 0.73 |
| C80 | 1 kHz | +2.8 ... +3.1 dB | +2.4 ... +3.1 dB | -0.5 ... +0.0 dB | 1.0 - 1.3 dB | 57 - 77 % | 0.40 - 0.69 |
| C80 | 2 kHz | +5.0 ... +5.3 dB | +3.8 ... +4.5 dB | -1.5 ... -0.6 dB | 1.5 - 2.1 dB | 34 - 46 % | 0.34 - 0.76 |
| C80 | 4 kHz | +5.3 ... +6.2 dB | +4.0 ... +4.9 dB | -2.2 ... -0.6 dB | 1.4 - 2.5 dB | 14 - 54 % | 0.40 - 0.86 |
| D50 | 500 Hz - 1 kHz | +0.08 ... +0.18 | +0.07 ... +0.16 | -0.04 ... +0.00 | 0.05 - 0.08 | 40 - 66 % | 0.52 - 0.71 |
| D50 | 2 - 4 kHz | +0.24 ... +0.27 | +0.19 ... +0.23 | -0.08 ... -0.01 | 0.07 - 0.13 | 31 - 52 % | 0.20 - 0.82 |
| Ts | 500 Hz - 1 kHz | -11 ... -28 ms | -12 ... -28 ms | -3 ... +4 ms | 7 - 10 ms | 66 - 89 % | 0.61 - 0.80 |
| EDT | 2 kHz | -32 ... -35 % | -5 ... -17 % | +18 ... +29 % | 30 - 35 % | 5 - 15 % | 0.07 - 0.50 |
| EDT | 4 kHz | -37 ... -54 % | -18 ... -28 % | +16 ... +34 % | 29 - 41 % | 10 - 17 % | 0.27 - 0.68 |
| C80, D50, Ts, EDT | 125 - 250 Hz | C80 +2.5 ... +3.2 dB (125), -2.1 ... -2.5 dB (250) | about 0 | | | 11 - 25 % | about 0 |

The detailed diagnostic model (out/arvedi_detail) gives a C80 delta at 2 - 4 kHz closer to the measurement (mean
error -1.4 ... +0.1 dB) but larger EDT errors at 500 Hz - 2 kHz.

Reading:
- **C80, D50 and Ts change correctly in direction and, at 500 Hz - 1 kHz, in size** (mean error within 0.5 dB,
  0.04, 4 ms; per receiver about 1 JND rms). At 2 - 4 kHz the simulated C80 change is about 70 - 85 % of the measured
  one (1 - 2 dB short of +5 ... +6 dB); its ranking over the receivers follows the measurement (r up to 0.86).
- **EDT changes are not reproduced at 2 - 4 kHz**: measured -32 ... -54 %, simulated -5 ... -28 %, and not per
  receiver. EDT of a direct-sound-dominated decay is very sensitive to the direct-to-reverberant ratio.
- **125 - 250 Hz**: the measured changes (C80 +3 dB at 125 Hz, -2 dB at 250 Hz, Ts +23 ... +28 ms at 250 Hz) do not
  appear in the simulation at all. Not explained; a candidate is the loudspeaker itself (a small two-way box near
  its low-frequency limit, whose own impulse response the model, a point source with octave-band polars, does not
  contain). Not tested.
- **For a study of reinforcement delay and level**: this supports using simulated changes of C80, D50 and Ts at
  500 Hz - 1 kHz as about right, and at 2 - 4 kHz as somewhat too small; it does not support simulated EDT changes
  at high frequencies or any change below 500 Hz. It is one hall and a change of source, not of delay; a delay sweep
  of a reinforcement loudspeaker against measurements has not been checked.

## After the diffuse-rain fix (2026-11-12, later)

Same comparison with the recalibrated run after the third engine fix (out/arvedi_posthoc_norain):

| | band | measured delta | simulated delta | mean error | within 1 JND | r |
|---|---|---|---|---|---|---|
| C80 | 500 Hz | +1.3 ... +1.6 dB | +1.3 ... +1.8 dB | -0.2 ... +0.3 dB | 51 - 71 % | 0.34 - 0.74 |
| C80 | 1 kHz | +2.8 ... +3.1 dB | +2.4 ... +3.1 dB | -0.5 ... +0.0 dB | 48 - 69 % | 0.46 - 0.64 |
| C80 | 2 kHz | +5.0 ... +5.3 dB | +3.8 ... +4.5 dB | -1.5 ... -0.6 dB | 37 - 52 % | 0.45 - 0.77 |
| C80 | 4 kHz | +5.3 ... +6.2 dB | +4.2 ... +4.9 dB | -2.0 ... -0.5 dB | 20 - 49 % | 0.42 - 0.84 |
| EDT | 2 - 4 kHz | -32 ... -54 % | +2 ... -31 % | +17 ... +34 % | 6 - 18 % | 0.08 - 0.74 |

Practically the same as before the fix: the rain fix moved S0 and the loudspeakers by similar amounts, so the
changes between them barely moved. The reading above stands.
