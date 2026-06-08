# Ising Model Assignment Work Log

This log records the evidence workflow for the eight assignment sections. It is
updated after each section with sources, tasks, outputs, commands, numerical
results, validation, commit reference, and draft-writing notes.

## Section 1 - Introduction to the Ising Model

PDF name:
- `script/1_introduction.pdf`
- Background theory from `Introduction.pdf`

Task labels completed:
- Section 1 background theory preparation.

Code/data/figure files produced:
- `outputs/notes/section_1_background.md`
- Output scaffold:
  - `outputs/data/generated/`
  - `outputs/data/processed/`
  - `outputs/figures/`
  - `outputs/logs/`
  - `outputs/notes/`

Commands run:
- Extracted PDF text with bundled `pypdf` runtime into `/private/tmp/ising_pdf_text`.
- `mkdir -p outputs/data/generated outputs/data/processed outputs/figures outputs/logs outputs/notes`

Key numerical results:
- Exact infinite-size 2D square-lattice critical temperature noted for later
  comparison: `T_C = 2 / ln(1 + sqrt(2)) = 2.269185...`.

Validation outcome:
- PDF sources were readable with `pypdf`.
- Notes cover Hamiltonian, periodic boundaries, magnetisation, spontaneous
  magnetisation, reduced units, and critical-temperature context.

Commit reference:
- Section commit message: `Section 1: add Ising model background notes`
- Commit hash: `201091265a34f90890027bdda5680e5d1163db90`

Draft-writing notes:
- Use the background note as the report opening.
- Emphasise finite-size peak temperatures as estimates rather than true
  thermodynamic-limit transitions.

## Section 2 - Calculating the Energy and Magnetisation

PDF name:
- `script/2_calculating_the_energy_and_magnetisation.pdf`

Task labels completed:
- TASK 2a: verified `energy()` and `magnetisation()`.
- TASK 2b: ran `ILcheck.py` non-interactively and ran pytest.

Code/data/figure files produced:
- `python_script/ILcheck.py` now supports optional figure export through
  `ISING_OUTPUT_FIGURE`.
- `outputs/figures/section_2_energy_magnetisation_check.png`
- `outputs/logs/section_2_validation.txt`
- `outputs/logs/section_2_pytest.xml`

Commands run:
- `env MPLBACKEND=Agg ISING_OUTPUT_FIGURE=outputs/figures/section_2_energy_magnetisation_check.png python3 python_script/ILcheck.py`
- `python3 -m pytest python_script --junitxml=outputs/logs/section_2_pytest.xml`
- Generated expected-vs-actual validation log with deterministic lattice cases.

Key numerical results:
- 4x4 all-up state: expected `E = -32`, actual `E = -32`, expected `M = 16`,
  actual `M = 16`.
- 4x4 all-down state: expected `E = -32`, actual `E = -32`, expected
  `M = -16`, actual `M = -16`.
- 4x4 checkerboard state: expected `E = 32`, actual `E = 32`, expected
  `M = 0`, actual `M = 0`.

Validation outcome:
- `python3 -m pytest python_script`: 7 tests passed.
- Figure exists and is non-empty (`39051` bytes).

Commit reference:
- Section commit message: `Section 2: validate energy and magnetisation`
- Commit hash: `56a694a96aa7e4c6352a4950cdf7f6033b830108`

Draft-writing notes:
- Include the saved ILcheck figure as evidence that the periodic-boundary
  energy and magnetisation match known limiting cases.
- Briefly describe the energy as nearest-neighbour products counted once in
  each lattice direction.

## Section 3 - Introduction to Monte Carlo Simulation

PDF name:
- `script/3_introduction_to_monte_carlo_simulation.pdf`

Task labels completed:
- TASK 3a: noted the infeasibility of exhaustive enumeration for 100 spins.
- TASK 3b: verified Metropolis trial moves and running statistics.
- TASK 3c: generated low-temperature equilibrium evidence at `T = 1.0`.

Code/data/figure files produced:
- `outputs/data/generated/section_3_low_temperature_timeseries.csv`
- `outputs/figures/section_3_low_temperature_equilibrium.png`
- `outputs/logs/section_3_statistics.txt`
- `outputs/logs/section_3_validation.txt`
- `outputs/logs/section_3_pytest.xml`

Commands run:
- Generated a deterministic 8x8 run with seed `3003`, `T = 1.0`, and
  `250` Monte Carlo cycles (`16000` attempted spin flips).
- `python3 -m pytest python_script --junitxml=outputs/logs/section_3_pytest.xml`

Key numerical results:
- Number of configurations for 100 spins: `2^100 = 1.27e30`; at `1e9`
  configurations per second this is about `4.02e13` years.
- Low-temperature run: final `E/spin = -2.0`, final `M/spin = 1.0`.
- Running averages: `<E>/spin = -1.973318073870383`,
  `<M>/spin = 0.9842373132929192`.
- Cached final energy and magnetisation matched full recomputation.

Validation outcome:
- `python3 -m pytest python_script`: 7 tests passed.
- Generated CSV has 3 columns, finite values, and strictly increasing cycle
  index.
- Figure exists and is non-empty (`81271` bytes).

Commit reference:
- Section commit message: `Section 3: add Monte Carlo simulation evidence`
- Commit hash: assigned by Git when this section entry is committed.

Draft-writing notes:
- Use the time-series figure to show relaxation into an ordered low-temperature
  state.
- Explain that a cycle is `N_spins` attempted single-spin moves, so a 250-cycle
  8x8 run contains 16000 trial moves.
