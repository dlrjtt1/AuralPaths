# Scattering and the simulated effect of a reinforcement condition (2026-11-14, diagnostic)

Question: the absolute EDT and C80 of the simulation depend on the scattering coefficient of the hard surfaces by
about one JND ([arvedi_check.md](arvedi_check.md), [detmold_kh.md](detmold_kh.md), [opera_check.md](opera_check.md)),
and no measured scattering is known for these halls. Does the CHANGE that a reinforcement condition (delay and level
of the loudspeakers) makes to EDT and C80 depend on it as much? Engineering assumption to be tested: errors common to
both conditions cancel in the change.

## Plan (fixed before the run)

- Halls: OperaRIR, Detmold, Arvedi. Per hall the two calibrated configurations of the scattering test (default
  scattering, and 0.5 on the hard surfaces; each calibrated on the measured T30 by itself), the hall's measurement
  receivers (97, 34, 65).
- Sources (omnidirectional, positions in `scatter_delta.py`, chosen without a real installation): A on the stage
  centre line at the height of the measured sources; B_L / B_R at the front of the stage, 5.5 - 6 m to either side,
  2 - 3.5 m above the stage floor.
- Conditions as in `run.py`: delay of B so that it arrives 0, 30, 60 ms after A at the reference receiver (the
  receiver nearest the centroid of the receivers), level of B 0 and +6 dB relative to A there (energy in 500 Hz -
  1 kHz). Change Delta = metric(A + B) - metric(A alone) per receiver, EDT as ratio in %, C80 in dB, 500 Hz - 4 kHz.
- Compared: d = Delta(scattering 0.5) - Delta(default) per receiver. Ray noise: the default configuration again with
  another ray seed. 20000 rays in every run.
- Reading fixed in advance: the change is called robust to the scattering in a hall, condition and band when the
  mean of d is within half a JND (EDT 2.5 %, C80 0.5 dB) and at least 80 % of the receivers are within one JND, or,
  where the ray noise alone gives fewer than 80 %, when d is not further from zero than the noise.
