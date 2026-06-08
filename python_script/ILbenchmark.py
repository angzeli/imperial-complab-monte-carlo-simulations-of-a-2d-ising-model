import argparse
import cProfile
import csv
import io
import pstats
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ILplot_style import save_figure
from IsingLattice import IsingLattice


OUTPUT_DIR = Path("outputs")


def loop_energy(lattice):
    energy = 0.0
    n_rows, n_cols = lattice.shape
    for i in range(n_rows):
        for j in range(n_cols):
            spin = lattice[i, j]
            energy -= spin * lattice[(i + 1) % n_rows, j]
            energy -= spin * lattice[i, (j + 1) % n_cols]
    return float(energy)


def loop_magnetisation(lattice):
    magnetisation = 0.0
    n_rows, n_cols = lattice.shape
    for i in range(n_rows):
        for j in range(n_cols):
            magnetisation += lattice[i, j]
    return float(magnetisation)


def vectorised_energy(lattice):
    energy = -np.sum(lattice * np.roll(lattice, 1, axis=0))
    energy -= np.sum(lattice * np.roll(lattice, 1, axis=1))
    return float(energy)


def vectorised_magnetisation(lattice):
    return float(np.sum(lattice))


def full_recompute_trial(lattice, temp, energy_func, magnetisation_func, n_steps):
    energy = energy_func(lattice)
    magnetisation = magnetisation_func(lattice)
    n_rows, n_cols = lattice.shape
    accepted = 0
    for _ in range(n_steps):
        i = np.random.randint(n_rows)
        j = np.random.randint(n_cols)
        spin = lattice[i, j]
        lattice[i, j] = -spin
        new_energy = energy_func(lattice)
        delta_en = new_energy - energy
        accept = delta_en <= 0.0 or np.random.random() < np.exp(-delta_en / temp)
        if accept:
            energy = new_energy
            magnetisation = magnetisation_func(lattice)
            accepted += 1
        else:
            lattice[i, j] = spin
    return energy, magnetisation, accepted / n_steps


def local_delta_trial(n_rows, n_cols, temp, n_steps):
    il = IsingLattice(n_rows, n_cols)
    energy = magnetisation = 0.0
    for _ in range(n_steps):
        energy, magnetisation = il.montecarlostep(temp)
    return energy, magnetisation, il.acceptance_rate()


def time_repeats(label, repeats, operation):
    rows = []
    for repeat in range(repeats):
        start = time.perf_counter()
        result = operation(repeat)
        elapsed = time.perf_counter() - start
        rows.append((label, repeat, elapsed, result))
    return rows


def main(args):
    np.random.seed(4004)
    (OUTPUT_DIR / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "logs").mkdir(parents=True, exist_ok=True)

    n_rows = n_cols = 25
    temp = 1.0
    repeats = 5
    loop_steps = 300
    fast_steps = 2000
    benchmark_rows = []

    def loop_operation(repeat):
        np.random.seed(4100 + repeat)
        lattice = np.random.choice([-1, 1], size=(n_rows, n_cols))
        return full_recompute_trial(
            lattice, temp, loop_energy, loop_magnetisation, loop_steps
        )

    def vectorised_operation(repeat):
        np.random.seed(4200 + repeat)
        lattice = np.random.choice([-1, 1], size=(n_rows, n_cols))
        return full_recompute_trial(
            lattice,
            temp,
            vectorised_energy,
            vectorised_magnetisation,
            fast_steps,
        )

    def local_operation(repeat):
        np.random.seed(4300 + repeat)
        return local_delta_trial(n_rows, n_cols, temp, fast_steps)

    for label, steps, operation in (
        ("loop_full_recompute", loop_steps, loop_operation),
        ("vectorised_full_recompute", fast_steps, vectorised_operation),
        ("local_delta_energy", fast_steps, local_operation),
    ):
        for path, repeat, seconds, result in time_repeats(label, repeats, operation):
            energy, magnetisation, acceptance_rate = result
            benchmark_rows.append(
                {
                    "path": path,
                    "repeat": repeat,
                    "lattice": f"{n_rows}x{n_cols}",
                    "temperature": temp,
                    "trial_moves": steps,
                    "seconds": seconds,
                    "seconds_per_trial_move": seconds / steps,
                    "final_energy": energy,
                    "final_magnetisation": magnetisation,
                    "acceptance_rate": acceptance_rate,
                }
            )

    csv_path = OUTPUT_DIR / "data" / "processed" / "section_4_timing.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(benchmark_rows[0]))
        writer.writeheader()
        writer.writerows(benchmark_rows)

    summary = {}
    for row in benchmark_rows:
        summary.setdefault(row["path"], []).append(row["seconds_per_trial_move"])

    summary_lines = [
        "Section 4 timing summary",
        f"seed_base: 4004",
        f"lattice: {n_rows}x{n_cols}",
        f"temperature: {temp}",
        "path,mean_seconds_per_trial_move,std_seconds_per_trial_move",
    ]
    labels = []
    means = []
    stds = []
    for path, values in summary.items():
        values = np.array(values)
        labels.append(path)
        means.append(float(np.mean(values)))
        stds.append(float(np.std(values, ddof=1)))
        summary_lines.append(f"{path},{means[-1]:.12g},{stds[-1]:.12g}")

    summary_path = OUTPUT_DIR / "logs" / "section_4_timing_summary.txt"
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    if not args.skip_render:
        fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
        x = np.arange(len(labels))
        ax.bar(x, means, yerr=stds, color=["#6b7280", "#2563eb", "#059669"], capsize=4)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=15, ha="right")
        ax.set_ylabel("Seconds per trial move")
        ax.set_yscale("log")
        ax.set_title("Monte Carlo update timing comparison")
        save_figure(fig, OUTPUT_DIR / "figures" / "section_4_timing_comparison.png")

    profile = cProfile.Profile()
    np.random.seed(4400)
    profile.enable()
    local_delta_trial(n_rows, n_cols, temp, 5000)
    profile.disable()
    stream = io.StringIO()
    stats = pstats.Stats(profile, stream=stream).strip_dirs().sort_stats("cumtime")
    stats.print_stats(20)
    (OUTPUT_DIR / "logs" / "section_4_profile_summary.txt").write_text(
        stream.getvalue(), encoding="utf-8"
    )
    print(summary_path.read_text())


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark Ising update paths.")
    parser.add_argument("--skip-render", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
