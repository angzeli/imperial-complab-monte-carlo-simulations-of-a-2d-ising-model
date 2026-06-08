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
- Commit hash: `5af99120e60313e1e8e8151fb36a4cc441cd6220`

Draft-writing notes:
- Use the time-series figure to show relaxation into an ordered low-temperature
  state.
- Explain that a cycle is `N_spins` attempted single-spin moves, so a 250-cycle
  8x8 run contains 16000 trial moves.

## Section 4 - Accelerating the Code

PDF name:
- `script/4_accelerating_the_code.pdf`

Task labels completed:
- TASK 4a: recorded timing for the pre-optimisation local path.
- TASK 4b: confirmed vectorised energy and magnetisation are implemented.
- TASK 4c: benchmarked vectorised full recomputation.
- TASK 4d: benchmarked local `delta_energy` Monte Carlo updates.

Code/data/figure files produced:
- `python_script/IsingLattice.py` uses `np.random.randint` for random spin
  coordinates and tracks accepted/attempted moves.
- `python_script/ILbenchmark.py`
- `outputs/data/processed/section_4_timing.csv`
- `outputs/figures/section_4_timing_comparison.png`
- `outputs/logs/section_4_timing_summary.txt`
- `outputs/logs/section_4_profile_summary.txt`
- `outputs/logs/section_4_iltimetrial.txt`
- `outputs/logs/section_4_validation.txt`
- `outputs/logs/section_4_pytest.xml`

Commands run:
- `python3 -m pytest python_script --junitxml=outputs/logs/section_4_pytest.xml`
- `env MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp/ising_mpl python3 python_script/ILbenchmark.py`
- `python3 python_script/ILtimetrial.py`

Key numerical results:
- Five-repeat benchmark on a 25x25 lattice at `T = 1.0`:
  - Loop full recomputation: `2.27219194484e-4` s per trial move.
  - Vectorised full recomputation: `1.26364083961e-5` s per trial move.
  - Local `delta_energy`: `3.74015006237e-6` s per trial move.
- In this benchmark, local `delta_energy` was about `3.38x` faster than
  vectorised full recomputation and about `60.8x` faster than loop full
  recomputation.
- `ILtimetrial.py` single-sample continuity check improved from the earlier
  probe of `0.380205` s for 2000 steps to `0.176372` s after replacing
  `np.random.choice(range(...))` with `np.random.randint(...)`.

Validation outcome:
- `python3 -m pytest python_script`: 7 tests passed.
- Timing CSV has 15 rows, finite positive timings, and all three expected
  paths.
- Timing figure and profile summary exist and are non-empty.

Commit reference:
- Section commit message: `Section 4: benchmark and optimise Monte Carlo updates`
- Commit hash: `253677e8d138f9d80ef6889f30be422ba8b28d24`

Draft-writing notes:
- Explain that vectorisation reduces Python-loop overhead for full-lattice
  calculations.
- Explain that local `delta_energy` is faster still because a single-spin flip
  changes only the four neighbouring bonds, avoiding full-lattice energy
  recomputation.

## Section 5 - The Effect of Temperature

PDF name:
- `script/5_effect_of_temperature.pdf`

Task labels completed:
- TASK 5a: added burn-in support and generated equilibration evidence.
- TASK 5b: generated 8x8 temperature dependence data with repeats and error
  bars.

Code/data/figure files produced:
- `python_script/IsingLattice.py` now accepts optional `burn_in_cycles` and has
  `reset_statistics(include_current=True)`.
- `python_script/ILtemperature_scan.py`
- `python_script/test_energy.py` includes burn-in/reset tests.
- `outputs/data/generated/8x8.dat`
- `outputs/data/generated/8x8_repeats.csv`
- `outputs/data/generated/section_5_8x8_equilibration_T2p3.csv`
- `outputs/data/processed/8x8_summary.csv`
- `outputs/figures/section_5_8x8_temperature_dependence.png`
- `outputs/figures/section_5_8x8_equilibration_T2p3.png`
- `outputs/logs/section_5_temperature_scan_timing.txt`
- `outputs/logs/section_5_validation.txt`
- `outputs/logs/section_5_pytest.xml`

Commands run:
- `python3 -m pytest python_script --junitxml=outputs/logs/section_5_pytest.xml`
- `env MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp/ising_mpl python3 python_script/ILtemperature_scan.py --section 5 --sizes 8 --repeats 6 --burn-in-cycles 300 --production-cycles 700 --seed-base 5000 --equilibration-size 8 --equilibration-temp 2.3`

Key numerical results:
- Temperature grid: 24 points from `0.25` to `5.0`, with `0.1` spacing in the
  critical-region interval `1.8 <= T <= 2.8`.
- 8x8 scan: 6 repeats, 300 burn-in cycles, 700 production cycles per repeat.
- Own-data heat-capacity peak: `T = 2.4`, `C/spin = 1.1672682499975673`.
- Own-data susceptibility peak: `T = 2.4`,
  `chi/spin = 11.661105377980101`.
- At `T = 2.3`, `<E>/spin = -1.4596254185267856`,
  `|<M>|/spin = 0.6125906808035714`, and mean acceptance rate is
  `0.18488802083333333`.

Validation outcome:
- `python3 -m pytest python_script`: 9 tests passed.
- `8x8.dat` has shape `(24, 6)`, finite values, sorted temperatures, and
  non-negative heat capacity.
- Rich CSV summaries include repeat index, standard errors, absolute
  magnetisation, susceptibility, acceptance rate, burn-in cycles, production
  cycles, and random seed.
- Temperature-dependence and equilibration figures exist and are non-empty.

Commit reference:
- Section commit message: `Section 5: generate temperature dependence data`
- Commit hash: `f227978d3e53c95dce2b46d97cb46f9c381f22f1`

Draft-writing notes:
- Use the equilibration figure to justify ignoring the first 300 cycles.
- Use the temperature-dependence figure to describe the energy rise and
  magnetisation loss through the transition region.

## Section 6 - The Effect of System Size

PDF name:
- `script/6_effect_of_system_size.pdf`

Task labels completed:
- TASK 6: generated or collected own temperature-scan data for `2x2`, `4x4`,
  `8x8`, `16x16`, and `32x32`; plotted energy and magnetisation versus
  temperature for each size.

Code/data/figure files produced:
- `python_script/ILsystem_size_analysis.py`
- New own-data files:
  - `outputs/data/generated/2x2.dat`
  - `outputs/data/generated/4x4.dat`
  - `outputs/data/generated/16x16.dat`
  - `outputs/data/generated/32x32.dat`
  - repeat CSVs and processed summaries for `2x2`, `4x4`, `16x16`, `32x32`
- Reused own 8x8 data from Section 5:
  - `outputs/data/generated/8x8.dat`
  - `outputs/data/processed/8x8_summary.csv`
- `outputs/data/processed/section_6_size_effects_table.csv`
- `outputs/figures/section_6_energy_vs_temperature_by_size.png`
- `outputs/figures/section_6_magnetisation_vs_temperature_by_size.png`
- Individual Section 6 temperature-dependence figures for `2x2`, `4x4`,
  `16x16`, and `32x32`
- `outputs/logs/section_6_temperature_scan_timing.txt`
- `outputs/logs/section_6_reference_inventory.txt`
- `outputs/logs/section_6_validation.txt`
- `outputs/logs/section_6_pytest.xml`

Commands run:
- `python3 -m pytest python_script --junitxml=outputs/logs/section_6_pytest.xml`
- `env MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp/ising_mpl python3 python_script/ILtemperature_scan.py --section 6 --sizes 2 4 16 32 --repeats 3 --burn-in-cycles 100 --production-cycles 300 --seed-base 6000 --equilibration-size 0`
- `env MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp/ising_mpl python3 python_script/ILsystem_size_analysis.py --sizes 2 4 8 16 32`

Key numerical results:
- Own-data scan timings:
  - `2x2`: `0.600335` s
  - `4x4`: `1.592313` s
  - `16x16`: `22.745570` s
  - `32x32`: `90.762074` s
- Near `T = 2.3`, own-data `|M|/spin` values were:
  - `2x2`: `0.18458333333333332`
  - `4x4`: `0.5278211805555556`
  - `8x8`: `0.6125906808035714`
  - `16x16`: `0.6476262410481771`
  - `32x32`: `0.6426761711968316`
- Reference data are available for all five assignment sizes and are logged as
  long-run comparison support.

Validation outcome:
- `python3 -m pytest python_script`: 9 tests passed.
- All five own-data `.dat` files have shape `(24, 6)`, finite values, sorted
  temperatures, and non-negative heat capacity.
- Compiled system-size table has 120 rows.
- Cross-size energy and magnetisation figures exist and are non-empty.

Commit reference:
- Section commit message: `Section 6: analyse system size effects`
- Commit hash: `73597fca6df73f6bd08d69f933fd6962c3891580`

Draft-writing notes:
- Emphasise that the transition sharpens with lattice size.
- The small 2x2 lattice is visibly too small to capture long-range
  correlations; larger lattices retain stronger order near the critical region.

## Section 7 - Determining the Heat Capacity

PDF name:
- `script/7_determining_the_heat_capacity.pdf`

Task labels completed:
- TASK 7a: recorded the variance formula for heat capacity.
- TASK 7b: generated heat-capacity and susceptibility plots for all lattice
  sizes.

Code/data/figure files produced:
- `python_script/ILresponse_analysis.py`
- `outputs/notes/section_7_response_formula.md`
- `outputs/data/processed/section_7_response_functions.csv`
- `outputs/figures/section_7_heat_capacity_by_size.png`
- `outputs/figures/section_7_susceptibility_by_size.png`
- `outputs/logs/section_7_validation.txt`
- `outputs/logs/section_7_pytest.xml`

Commands run:
- `python3 -m pytest python_script --junitxml=outputs/logs/section_7_pytest.xml`
- `env MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp/ising_mpl python3 python_script/ILresponse_analysis.py --sizes 2 4 8 16 32`

Key numerical results:
- Peak summary from own data:
  - `2x2`: `C` peak at `T = 2.4`, susceptibility peak at `T = 1.5`.
  - `4x4`: `C` peak at `T = 2.2`, susceptibility peak at `T = 2.1`.
  - `8x8`: `C` peak at `T = 2.4`, susceptibility peak at `T = 2.4`.
  - `16x16`: `C` peak at `T = 2.2`, susceptibility peak at `T = 2.5`.
  - `32x32`: `C` peak at `T = 2.2`, susceptibility peak at `T = 2.5`.

Validation outcome:
- `python3 -m pytest python_script`: 9 tests passed.
- Response-function table has 120 rows, finite heat capacity and
  susceptibility, and non-negative variance-derived values.
- Heat-capacity and susceptibility figures exist and are non-empty.

Commit reference:
- Section commit message: `Section 7: compute heat capacity and susceptibility`
- Commit hash: assigned by Git when this section entry is committed.

Draft-writing notes:
- Derive `C_per_spin = (<E^2> - <E>^2) / (N T^2)` with `k_B = 1`.
- Derive `chi_per_spin = (<M^2> - <M>^2) / (N T)`.
- Note that finite simulation noise is largest near the response peaks.
