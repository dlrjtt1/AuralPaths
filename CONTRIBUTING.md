# Contributing to AuralPaths

AuralPaths is a research and teaching tool maintained by Dong-Gyun You (LABO 1557). Bug reports, questions and
suggestions are welcome as GitHub issues: https://github.com/dlrjtt1/AuralPaths/issues

## Reporting a problem
- Say what you did, what you expected and what happened.
- Attach the config (Save config… on the page): it records the page and engine version, the settings and any
  calibration, so the result can be reproduced.
- For a difference from a measurement, give the hall, the positions and the measured values if you can share them.

## Changing the code
- The page is built from `viewer_template.html` and `engine_geom.js`: edit those, then run `python tools/build_page.py`
  (do not edit `index.html` by hand).
- Run the regression checks before committing: `python tests/regression.py` (needs node, the packages in
  `requirements.txt`, and optionally playwright for the page check). They also run on GitHub for every push to main.
- If a change is meant to alter results (a model change), update the baseline with
  `python tests/regression.py --update` and say in the commit message what changed and why.
- Python and the browser engine implement the same model; changes to one should be mirrored in the other and checked
  with the scripts in `validation/` (`check_*_pyjs.py`).
- Do not add third-party data or code without checking its licence; list it in `NOTICE.md`.
- Code, comments and documentation in English (the documentation is also kept in Korean and Japanese under `docs/`).

## Scientific claims
Results are model estimates. Claims about accuracy in the documentation must point to a check in `validation/` or to a
cited source; please keep it that way.
