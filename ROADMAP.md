# Ising Model Assignment Roadmap

## Section 1 - Background

Status: complete.

Objective: summarise the 2D Ising model theory needed for the report.

Main outputs:
- `outputs/notes/section_1_background.md`
- `outputs/WORKLOG.md`
- Output directory scaffold.

Validation result:
- `Introduction.pdf` and `script/1_introduction.pdf` reviewed through extracted
  text. Required theory points are covered.

Commit hash:
- `201091265a34f90890027bdda5680e5d1163db90`

## Section 2 - Energy and Magnetisation

Status: complete.

Objective: validate total energy and total magnetisation for known 4x4
configurations.

Main outputs:
- `outputs/figures/section_2_energy_magnetisation_check.png`
- `outputs/logs/section_2_validation.txt`
- `outputs/logs/section_2_pytest.xml`

Validation result:
- All expected-vs-actual checks passed.
- `python3 -m pytest python_script`: 7 passed.

Commit hash:
- `56a694a96aa7e4c6352a4950cdf7f6033b830108`

## Section 3 - Monte Carlo Simulation

Status: complete.

Objective: verify Metropolis spin flips and running statistics with
low-temperature equilibrium evidence.

Main outputs:
- `outputs/data/generated/section_3_low_temperature_timeseries.csv`
- `outputs/figures/section_3_low_temperature_equilibrium.png`
- `outputs/logs/section_3_statistics.txt`

Validation result:
- Cached final energy and magnetisation matched full recomputation.
- `python3 -m pytest python_script`: 7 passed.

Commit hash:
- Assigned by Git in commit `Section 3: add Monte Carlo simulation evidence`.
