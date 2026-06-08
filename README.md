# 🧲 Monte Carlo Simulations of the 2D Ising Model

This repository contains Python scripts for simulating the two-dimensional Ising
model on a square lattice with periodic boundary conditions. The simulation uses
Metropolis Monte Carlo trial spin flips and tracks the system energy and
magnetisation.

The temperature scan script analyses the simulation output to estimate the heat
capacity per spin and a finite-size Curie temperature from the heat-capacity
peak.

## 📁 Repository Layout

```text
.
├── python_script/
│   ├── IsingLattice.py          # Core lattice and Monte Carlo update code
│   ├── ILcheck.py               # Energy and magnetisation visual checks
│   ├── ILfinalframe.py          # Final lattice and time-series plots
│   ├── ILanim.py                # Animated lattice, energy, and magnetisation
│   ├── ILtemperaturerange.py    # Temperature sweep and heat capacity analysis
│   └── test_energy.py           # Pytest checks for core lattice behaviour
├── reference_data/              # Reference temperature-sweep data
├── Introduction.pdf
├── script.pdf
├── README.md
└── LICENSE
```

## ⚙️ Requirements

Use Python 3 with:

- `numpy`
- `matplotlib`
- `pytest`

## ✅ Quick Checks

Run the test suite from the repository root:

```bash
python3 -m pytest python_script
```

Run the temperature sweep:

```bash
python3 python_script/ILtemperaturerange.py
```

The scripts use reduced units with `J = 1` and `k_B = 1`.

## 👤 Author

Angze Li
