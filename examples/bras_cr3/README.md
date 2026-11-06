# Demo: BRAS CR3 with measured T30

A real hall (BRAS scene CR3, a chamber music hall) with its measured reverberation times, to try every part of the
page and of the Python tools on one example.

| file | content |
|---|---|
| `bras_cr3_config.json` | config with the 3D model embedded (`geometry.mesh.obj_text`), BRAS "fitted" absorption and scattering (not calibrated), receivers MP1–MP5 at the BRAS measurement positions, `S_amp` at the BRAS loudspeaker position LS1, plan turned 270° so that the seats face the stage |
| `bras_cr3_measured_T30.csv` | measured T30 / EDT for LS1 and LS2 × MP1–MP5, 125 Hz – 4 kHz (from the BRAS dodecahedron RIRs, as in `validation/bras_CR3.csv`); LS1 rows `role=calibrate`, LS2 rows `role=check` |

The PA pair `B_L` / `B_R` is an invented position for the demo; BRAS has no PA.

In the page:

1. **Load config…** → `bras_cr3_config.json` (about 1–2 min to compute at 10 000 rays per source).
2. Read *How far to trust these values*: 3D model, materials not calibrated.
3. **Ray-tracing spread…** for the seat on display.
4. **Calibrate…** → `bras_cr3_measured_T30.csv` (30 000 rays per source for the calibration, several minutes):
   the table shows the T30 error before → after for the LS1 positions (fit) and the LS2 positions (check).
5. **Save config…** (carries `_calibration` and `_provenance`), **Export BRIRs (SOFA)…**, **Export WAV…**.

In Python: `python calibrate.py examples/bras_cr3/bras_cr3_config.json examples/bras_cr3/bras_cr3_measured_T30.csv`
(reads the OBJ from `obj_text`; the `role` column is ignored there, so all ten pairs are fitted), then
`python run.py examples/bras_cr3/bras_cr3_config_calibrated.json` (needs `hrir/KU100.sofa`).

Data: BRAS database v3, L. Aspöck, F. Brinkmann, D. Ackermann, S. Weinzierl, M. Vorländer (2020),
https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0. Both files are derived from it (geometry, materials,
positions, T30 / EDT evaluated from the RIRs) and are under the same licence.
