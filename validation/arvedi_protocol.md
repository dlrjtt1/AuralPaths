# Arvedi Auditorium: blind check protocol (fixed 2026-11-11, before any measured RIR was opened)

Purpose: one check of AuralPaths on a hall that played no part in its development, with the procedure fixed before
the measurements are seen, so that the result is a prediction and not a fit.

Data: "The Sound of the Violin's Home: A Higher-Order Room Impulse Response Dataset of the Arvedi Auditorium in
Cremona", Politecnico di Milano, https://doi.org/10.5281/zenodo.20098848 (CC BY 4.0): 65 receivers, 5 stage sources
(one omnidirectional at the stage centre, four directional loudspeakers), 8-capsule spherical array, 48 kHz.
Derived outputs stay in `out/` (not in the repository).

## Fixed before the measurements are opened

1. **Code.** Engine as of commit `983daf2` (2026-11-11). Any change to the engine after the measured RIRs have been
   opened is reported separately as "after seeing the data"; the blind result is the one with this commit.
2. **Geometry.** A simplified 3-D model (`validation/arvedi_model.py`) drawn only from published drawings and facts:
   plans and sections on ArchDaily (ARKPABI, https://www.archdaily.com/870937), dimensions, volume, stage, materials
   and reverberation time in Arketipo (https://www.arketipomagazine.it/auditorium-giovanni-arvedi-del-museo-del-violino-di-cremona-studio-arkpabi-e-nagata-acoustics/),
   Beckmann Acoustics poster and the Museo del Violino page. The model is finished before any RIR is opened. The
   dataset's source and receiver coordinates may be read to place the model in the measurement frame (an offset and
   a rotation only; the hall shape is not changed to fit them).
3. **Initial materials.** BRAS CR3 (chamber music hall) "fitted" estimates by analogy (plaster, floor, seating,
   windows, stage), Aspoeck et al., https://doi.org/10.14279/depositonce-6726.3 (CC BY-SA 4.0).
4. **Calibration.** Only absorption, scaled per octave band (125 Hz - 4 kHz) with `calibrate.py` so that the
   simulated T30 matches the measured T30 of the omnidirectional source averaged over all receivers. Nothing else is
   fitted. Scattering stays as initialised.
5. **Compared (omnidirectional source, omnidirectional pressure of the array).** Per receiver and octave band
   (125 Hz - 4 kHz): EDT, T20, C80, D50, Ts (ISO 3382-1); reported as bias and as the share of receivers within one
   JND (ISO 3382-1:2009 Annex A: EDT 5 %, C80 1 dB, D50 5 %, Ts 10 ms) and the mean error in JND, as for Detmold and
   the round robin. T30 is the calibration target and is shown only as a check of the fit.
6. **Settings.** As the Detmold check (`validation/detmold_kh.py`): image-source order 3, 20 000 rays, edge diffraction
   off, seat dip off, binaural settings unused (omnidirectional comparison). Pre-declared secondary runs: seat dip on (default
   seats), and the four directional sources with the generic loudspeaker directivity.
7. **One run.** The comparison is computed once and reported as it comes out, including failures.
