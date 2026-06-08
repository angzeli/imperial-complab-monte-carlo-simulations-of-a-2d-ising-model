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
- Assigned by Git in commit `Section 2: validate energy and magnetisation`.
