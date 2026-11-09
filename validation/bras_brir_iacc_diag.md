# BRAS CR4: why the late IACC is lower than measured (diagnosis, 2026-11-09)

Binaural check of validation/check_bras_brir.py (FABIAN head, QSC K8 measured directivity, listener MP6), materials
calibrated on the measured T30 of the BRAS RIRs, 125 Hz - 16 kHz (validation/bras_calibration.py --to-16k).
BRAS: Aspoeck et al. 2020, https://doi.org/10.14279/depositonce-6726.3 (CC BY-SA 4.0).

## Observation

| | IACC_L (80 ms - end), broadband | 10 ms frames 200 - 800 ms with \|ITD\| < 100 us (500 Hz - 2 kHz) |
|---|---|---|
| CR3 measured (LS3 - LS7) | 0.09 - 0.12 | 0.08 (LS7) |
| CR3 simulated | 0.07 - 0.09 | |
| CR4 measured (LS3 - LS7) | 0.23 - 0.38 | 0.30 (LS7) |
| CR4 simulated | 0.06 - 0.10 | 0.12 (LS7) |

CR3 agrees. In CR4 the measured late field stays interaurally coherent (0.25 at 500 - 1000 ms) with a large share of
energy from the median plane, from 80 ms to the end, in all bands from 250 Hz to 4 kHz. Between 80 and 200 ms there are
also discrete median-plane reflections at about 85 and 170 ms (correlation 0.6 - 0.8, ITD 0 - 70 us).

## What was tried (CR4, LS7)

| model | IACC_L broadband | median-plane share | change |
|---|---|---|---|
| calibrated (16 kHz), isotropic late tail | 0.09 | | |
| + ray-guided specular paths, orders 2 - 3, rendered to 250 ms (specpaths.py) | 0.11 | | finds median-plane paths at +77, +116, +174, +202 ms |
| + directional late field (dirrays, 5000 rays) | 0.11 | 0.12 | |
| + scattering coefficients x 0.25 (diagnostic only) | 0.18 | 0.15 | |
| measured | 0.38 | 0.30 | |

None of these reproduces the measured late coherence. The renderer is not the limit: the late energy of the CR4 model
(geometry and fitted materials as published) arrives from all directions, also with much less scattering. Possible
causes not tested here: simplifications of the CR4 geometry (the BRAS model notes list them), surfaces whose real
reflection is more specular or more regular than a flat polygon with a scattering coefficient, or properties of the
measurement set-up. Not resolved.

## Consequence for use

Late spaciousness (IACC_L) of a mesh hall can be overestimated (too wide) where the real late field is anisotropic.
Check this in the measured impulse responses of a hall before relying on simulated late spaciousness there.
