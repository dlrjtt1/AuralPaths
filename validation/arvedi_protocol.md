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

## Added 2026-11-11, after reading the position files only (no RIR opened)

8. **Placement.** The dataset's origin is the stage centre (S0 at z = 1.45 m, S1 - S4 at 1.18 m) and its axes are
   parallel to the model's. The 65 receivers (rows A1 - A5) are on one side of the stage; on the low-end side all of
   them lie 0.5 - 1.4 m above the model floor, on the high-end side 11 of them would lie at or below it. Placement:
   model = dataset + (22.05, 7.0, 0) m, no rotation.
9. **Metrics, both sides with the same functions.** Octave-band energy histograms (measured: `validate_bras_cr.
   measured_hist` of each of the 8 capsules, energies averaged over the capsules; simulated: `brir_proto.energy_hists`
   at the array centre), then `validate_fratoni.criteria` (EDT, T30, C80, C50 -> D50, Ts) and T20 (-5 ... -25 dB) the
   same way. Direct sound at the geometric distance / c.
10. **Materials.** BRAS CR3 fitted values (examples/bras_cr3): seating (aud) <- mat_CR3_seating, plaster walls <-
    mat_CR3_plaster, ceiling <- mat_CR3_ceiling, windows <- mat_CR3_windows, walkway and stage floors <-
    mat_CR3_floor, wood shells <- mat_CR3_stagePanels; their scattering as given there.
11. **Secondary run, directional sources.** S1 - S4 with the generic loudspeaker model (90 degree coverage), aimed
    horizontally along +x (towards the measured audience); the aim is not documented in the dataset.
