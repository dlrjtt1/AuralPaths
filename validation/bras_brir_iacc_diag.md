# BRAS CR4: why the late IACC is lower than measured (diagnosis, 2026-11-09 / 10)

Binaural check of validation/check_bras_brir.py (FABIAN head, QSC K8 measured directivity, listener MP6 on the
centre line of the hall), materials calibrated on the measured T30 of the BRAS RIRs, 125 Hz - 16 kHz
(validation/bras_calibration.py --to-16k). BRAS: Aspoeck et al. 2020, https://doi.org/10.14279/depositonce-6726.3
(CC BY-SA 4.0).

## 1. Where the difference is

IACC (+-1 ms, broadband) per window after the direct sound, measured / simulated:

| | 80 - 200 ms | 200 ms - 1.5 s | IACC_L |
|---|---|---|---|
| CR3 LS3 - LS7 | 0.09 - 0.13 / 0.08 - 0.10 | 0.08 - 0.10 / 0.08 - 0.13 | 0.09 - 0.12 / 0.07 - 0.10 |
| CR4 LS3 - LS6 | 0.30 - 0.42 / 0.09 - 0.10 | 0.13 - 0.19 / 0.09 - 0.12 | 0.23 - 0.33 / 0.09 - 0.10 |
| CR4 LS7 (on the centre line) | 0.43 / 0.10 | 0.28 / 0.12 | 0.38 / 0.09 |

The 80 - 200 ms window carries the same share of the late energy in measurement and simulation (CR4: -1.7 ... -2.1 dB
measured, -1.3 ... -2.2 dB simulated); in the measurement it arrives as interaurally coherent median-plane
reflections, in the simulation mostly as incoherent noise. After 200 ms the difference is small except for LS7,
where source and listener are both on the symmetry plane of the hall.

## 2. The mechanism: a flutter echo between the ceiling panels and the aisle floor

Strongest measured 4 ms frames (500 Hz - 4 kHz, LS7): 84 - 98 ms and 170 - 174 ms after the direct sound,
-16 ... -19 dB re direct, interaural correlation 0.6 - 0.84 at lag 0 - 45 us (from the median plane). The listener sits
in the centre aisle (linoleum) under the suspended ceiling panels. The ray-guided path search (specpaths.py, orders up
to 6) finds vertical paths between the ceiling panels and the aisle floor arriving from straight above at
+95 ms (whitePanels - linoleum - whitePanels), +103 ms (parquet - whitePanels - linoleum - whitePanels), +165, +172 and
+180 ms (orders 5 - 6), i.e. the same two clusters as measured (the model's ceiling height shifts them by a few ms).

## 3. Why the simulation renders them too weak

- The first of these paths leave the loudspeaker steeply upwards, where the QSC K8 radiates little: as rendered they
  are 5 - 10 dB weaker than measured (e.g. +95 ms: -24 dB rendered, -19 dB measured).
- The rest of the 80 - 200 ms energy of the model is scattered energy with an almost uniform direction distribution
  (ray tracer, LS7: 53 % within 30 degrees of the median plane vs 48 % for a uniform field; 20 % from above vs 16 %),
  rendered as incoherent noise.
- Tried, each with a small effect on IACC (80 - 200 ms): specular paths of order 3 (0.13), order 6 (0.17), order 6
  without finite-reflector losses (0.19), directional late field (0.12), scattering x 0.25 with order 3 (IACC_L 0.18).

So the renderer is not the main limit: in the real hall the flutter between ceiling and aisle carries much more of
the 80 - 200 ms energy than in the model. Candidates (not separable with these data): the ceiling panel array and the
aisle reflect more coherently than the model's small panels with their scattering coefficients; the measured
loudspeaker radiates more upwards than its directivity data; geometry differences above the listener (the BRAS notes
list the unmodelled steel structure behind the ceiling panels).

## 4. Can it be corrected by fitting the model? (2026-11-10: no)

- Reflection matching in the omnidirectional RIRs (validation/bras_reflection_match.py, LS1 -> MP1 - MP5, 1 and
  2 kHz, model paths of orders 1 - 6): reflections 14 - 70 ms after the direct sound agree, median measured - model
  -1.1 dB in both halls (CR3 19 of 20 matched, CR4 32 of 37). After 70 ms the "peaks" of the measured RIRs are mostly
  fluctuations of the dense reverberation (same picture in CR3, where the late IACC agrees): +16 ... +17 dB above any
  model path at the same time, so a per-surface reflection-strength fit has nothing consistent to fit.
- No parameter of the model brings the 80 - 200 ms IACC of CR4 LS7 near the measured 0.43: K8 directivity 0.17,
  omnidirectional source 0.12, orders 3 / 6 0.13 / 0.17, no finite-reflector loss 0.19, scattering x 0.25 (order 3)
  IACC_L 0.18, directional late field 0.12.
- The missing coherent median-plane energy therefore comes from features the model geometry does not contain
  (not from materials, loudspeaker directivity or the renderer). Fitting parameters would not make the model
  predictive. The ways to get it right at such a position are geometry detail or measured data (e.g. a measured
  binaural late part).

## 5. Is CR4 typical? Another concert hall (2026-11-10)

Detmold Konzerthaus (about 600 seats), dummy-head BRIRs of the dense receiver grid, Set C of the Detmold SRIR
database (Detmold University of Music, https://zenodo.org/records/4116247, CC BY 4.0), stage sources S2 (35 seats)
and S3 (12 seats), same analysis as above:

| | IACC 80 - 200 ms | same, above 400 Hz | IACC_L |
|---|---|---|---|
| Detmold, seats near the centre line | 0.15 - 0.18 (0.10 - 0.20) | 0.06 - 0.07 | 0.15 - 0.17 |
| Detmold, other seats | 0.16 - 0.17 (0.09 - 0.26) | 0.07 - 0.08 | 0.16 - 0.17 |
| BRAS CR3 measured | 0.09 - 0.13 | | 0.09 - 0.12 |
| BRAS CR4 measured | 0.30 - 0.43 | 0.19 - 0.33 | 0.23 - 0.38 |
| AuralPaths (CR3, CR4) | 0.08 - 0.10 | 0.04 - 0.06 | 0.07 - 0.10 |

No Detmold seat reaches 0.30 in the 80 - 200 ms window; above 400 Hz the late field there is close to diffuse, like
CR3 and like the simulation. CR4 is the exception (two halls of three), not the rule. The broadband values of
Detmold are somewhat higher than the simulation (0.15 - 0.17 vs 0.07 - 0.10), mostly below 400 Hz; different
dummy heads (Detmold vs FABIAN) make a part of that.

## 6. Consequence for use

A listener in an aisle under a flat hard ceiling can hear a vertical flutter echo (here about 85 - 100 ms and
170 ms) that the simulation reproduces in timing but underestimates in level; late spaciousness (IACC_L) is then
overestimated (too wide). Check measured impulse responses at such positions before relying on simulated echoes or
late spaciousness there.
