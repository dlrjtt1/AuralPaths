# Third-party data and software

AuralPaths source code is MIT-licensed (see `LICENSE`). The following third-party material is included or
loaded and keeps its own licence.

## Included data

### Neumann KU100 HRIRs (embedded in `index.html`)
- Source: B. Bernschütz, *Spherical Far-Field HRIR Compilation of the Neumann KU100*, TH Köln / TU Berlin,
  Zenodo record 3928297 (file `HRIR_FULL2DEG.sofa`), https://zenodo.org/records/3928297
- Paper: B. Bernschütz (2013), "A Spherical Far Field HRIR/HRTF Compilation of the Neumann KU 100",
  Proc. AIA-DAGA 2013, Merano, pp. 592–595.
- Licence: Creative Commons Attribution 3.0 Unported (CC BY 3.0), https://creativecommons.org/licenses/by/3.0/
- **Changes made:** resampled to 48 kHz; every other elevation and azimuth kept (about 4° spacing); quantised to
  16-bit integers and base64-encoded inside the page. Diffuse-field band gains, interaural coherence and
  direction-bin tables computed from the full set are also embedded.

### Headphone compensation filter (`hrir/HPCF_Sennheiser-HD600.mat`, also embedded in `index.html`)
- Source: same Zenodo record 3928297 (`HPCF.zip`), B. Bernschütz.
- Licence: CC BY 3.0. Measured on the KU100 dummy head; changes: resampled to 48 kHz, stored as float32 in the page.

### BRAS-derived validation results (`validation/`)
- Derived from: L. Aspöck, F. Brinkmann, D. Ackermann, S. Weinzierl, M. Vorländer (2020), *BRAS – Benchmark for
  Room Acoustical Simulation*, version 3, TU Berlin DepositOnce, https://doi.org/10.14279/depositonce-6726.3
  (scenes RS5, CR3, CR4; results `validation/bras_*` and the converted halls `validation/bras_CR*_2p5d_config.json`;
  the demo `examples/bras_cr3/`: CR3 geometry, fitted materials and positions in `bras_cr3_config.json`, T30 / EDT
  evaluated from the measured RIRs in `bras_cr3_measured_T30.csv`). The measured RIRs themselves are not included.
- Licence of the derived files: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0), as required by the
  source licence, https://creativecommons.org/licenses/by-sa/4.0/

### Fratoni-derived validation results and converted halls (`validation/fratoni_*`)
- Derived from: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic
  simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (halls ULH and STC: 3D models, boundary
  conditions, measured room criteria). The dataset's files themselves are not included.
- Licence of the derived files: Creative Commons Attribution 4.0 (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
- **Changes made:** models exported from SketchUp to OBJ (via Blender), decimated (STC) and converted to 2.5D
  drawn halls with merged materials; source and receiver positions read from the dataset's figures; simulated
  room criteria computed with AuralPaths. The measured values in the tables are the dataset's.

### Loudspeaker directivity files (`directivity/`)
- `dodeca_HBK_4292L.csv`, `dodeca_NTi_DS3.csv`: values read from the polar plots in the manufacturers' public
  data sheets (Brüel & Kjær BP 1689; NTi Audio DS3). **Not official manufacturer data**; reading method and
  uncertainty are given in each file's header.
- `meyer_CQ-1_nominal.csv`, `meyer_UPM-1P_nominal.csv`: a generic pattern applied to the nominal coverage angles
  stated in Meyer Sound data sheets. **Not measured and not manufacturer data.**
- Product names are trademarks of their owners; their use here only identifies the products.

## Loaded at run time (not included)
- pdf.js 3.11.174 (Mozilla, Apache License 2.0), from cdnjs, only when a PDF drawing is opened.
- h5wasm 0.10.3 (NIST software licence; includes HDF5), from jsDelivr, only when a SOFA directivity file is opened or BRIRs are exported as SOFA.
- IBM Plex Sans (SIL Open Font License 1.1), from Google Fonts.

## Not included (download separately)
- I-Simpa (Université Gustave Eiffel, GPL-3.0) for `validation/check_isimpa.py`: run as a separate program from a local build
  (https://github.com/Universite-Gustave-Eiffel/I-Simpa); not bundled, not linked.
- `hrir/KU100.sofa` for the Python tools: `HRIR_FULL2DEG.sofa` from Zenodo record 3928297 (CC BY 3.0).
- BRAS data for `validate_bras.py`: see above.
- Fratoni dataset for `validate_fratoni.py`: see above.
- fast-simplification (MIT licence, Python, optional) for decimating large OBJ meshes; openpyxl (MIT) for the
  dataset sheets.
