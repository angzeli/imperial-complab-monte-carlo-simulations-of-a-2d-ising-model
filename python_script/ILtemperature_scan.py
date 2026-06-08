import argparse
import csv
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ILplot_style import save_figure
from IsingLattice import IsingLattice


OUTPUT_DIR = Path("outputs")


def default_temperature_grid():
    cold = np.arange(0.25, 1.76, 0.25)
    critical = np.arange(1.8, 2.81, 0.1)
    hot = np.array([3.0, 3.25, 3.5, 4.0, 4.5, 5.0])
    return np.array(sorted(set(np.round(np.concatenate((cold, critical, hot)), 10))))


def prepare_lattice(size, burn_in_cycles):
    il = IsingLattice(size, size, burn_in_cycles=burn_in_cycles)
    il.lattice = np.ones((size, size))
    il.energy()
    il.magnetisation()
    il.total_steps = 0
    il.attempted_moves = 0
    il.accepted_moves = 0
    il.reset_statistics(include_current=il.burn_in_steps == 0)
    return il


def run_temperature(size, temp, repeat, seed, burn_in_cycles, production_cycles):
    np.random.seed(seed)
    il = prepare_lattice(size, burn_in_cycles)
    spins = size * size
    total_steps = (burn_in_cycles + production_cycles) * spins
    for _ in range(total_steps):
        il.montecarlostep(temp)

    aveE, aveE2, aveM, aveM2, n_steps = il.statistics()
    varE = max(0.0, aveE2 - aveE**2)
    varM = max(0.0, aveM2 - aveM**2)
    return {
        "lattice_size": f"{size}x{size}",
        "L": size,
        "repeat": repeat,
        "seed": seed,
        "T": temp,
        "burn_in_cycles": burn_in_cycles,
        "production_cycles": production_cycles,
        "production_steps_recorded": n_steps,
        "acceptance_rate": il.acceptance_rate(),
        "E_per_spin": aveE / spins,
        "E2_per_spin2": aveE2 / (spins**2),
        "M_per_spin": aveM / spins,
        "M2_per_spin2": aveM2 / (spins**2),
        "abs_M_per_spin": abs(aveM) / spins,
        "C_per_spin": varE / (spins * temp**2),
        "chi_per_spin": varM / (spins * temp),
    }


def stderr(values):
    values = np.array(values, dtype=float)
    if len(values) < 2:
        return 0.0
    return float(np.std(values, ddof=1) / np.sqrt(len(values)))


def summarise_repeat_rows(rows):
    by_temperature = {}
    for row in rows:
        by_temperature.setdefault(row["T"], []).append(row)

    summary_rows = []
    for temp in sorted(by_temperature):
        temp_rows = by_temperature[temp]
        summary = {
            "T": temp,
            "n_repeats": len(temp_rows),
            "burn_in_cycles": temp_rows[0]["burn_in_cycles"],
            "production_cycles": temp_rows[0]["production_cycles"],
        }
        for key in (
            "E_per_spin",
            "E2_per_spin2",
            "M_per_spin",
            "M2_per_spin2",
            "abs_M_per_spin",
            "C_per_spin",
            "chi_per_spin",
            "acceptance_rate",
        ):
            values = [row[key] for row in temp_rows]
            summary[f"{key}_mean"] = float(np.mean(values))
            summary[f"{key}_stderr"] = stderr(values)
        summary_rows.append(summary)
    return summary_rows


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_dat(path, summary_rows):
    data = np.array(
        [
            [
                row["T"],
                row["E_per_spin_mean"],
                row["E2_per_spin2_mean"],
                row["M_per_spin_mean"],
                row["M2_per_spin2_mean"],
                row["C_per_spin_mean"],
            ]
            for row in summary_rows
        ]
    )
    np.savetxt(path, data)


def plot_temperature_summary(size, summary_rows, figure_path):
    temps = np.array([row["T"] for row in summary_rows])
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 9.0), constrained_layout=True)
    axes[0].errorbar(
        temps,
        [row["E_per_spin_mean"] for row in summary_rows],
        yerr=[row["E_per_spin_stderr"] for row in summary_rows],
        marker="o",
        ms=3,
        lw=1,
        label="E per spin",
    )
    axes[0].set_ylabel("E / spin")
    axes[0].legend()
    axes[1].errorbar(
        temps,
        [row["abs_M_per_spin_mean"] for row in summary_rows],
        yerr=[row["abs_M_per_spin_stderr"] for row in summary_rows],
        marker="o",
        ms=3,
        lw=1,
        color="tab:green",
        label="|M| per spin",
    )
    axes[1].set_ylabel("|M| / spin")
    axes[1].legend()
    axes[2].errorbar(
        temps,
        [row["C_per_spin_mean"] for row in summary_rows],
        yerr=[row["C_per_spin_stderr"] for row in summary_rows],
        marker="o",
        ms=3,
        lw=1,
        color="tab:red",
        label="C per spin",
    )
    axes[2].set_xlabel("Temperature")
    axes[2].set_ylabel("C / spin")
    axes[2].legend()
    fig.suptitle(f"{size}x{size} temperature dependence")
    save_figure(fig, figure_path)


def plot_equilibration(size, temp, seed, burn_in_cycles, production_cycles, figure_path, csv_path, render=True):
    np.random.seed(seed)
    il = prepare_lattice(size, burn_in_cycles=0)
    spins = size * size
    total_cycles = burn_in_cycles + production_cycles
    rows = []
    for step in range(1, total_cycles * spins + 1):
        energy, magnetisation = il.montecarlostep(temp)
        if step % spins == 0:
            rows.append((step // spins, energy / spins, magnetisation / spins))

    csv_path.write_text(
        "cycle,E_per_spin,M_per_spin\n"
        + "\n".join(f"{cycle},{energy:.12g},{magnetisation:.12g}" for cycle, energy, magnetisation in rows)
        + "\n",
        encoding="utf-8",
    )
    if not render:
        return

    cycles = np.array([row[0] for row in rows])
    energies = np.array([row[1] for row in rows])
    magnetisations = np.array([row[2] for row in rows])

    fig, axes = plt.subplots(3, 1, figsize=(7.2, 8.4), constrained_layout=True)
    axes[0].imshow(il.lattice, cmap="gray", vmin=-1, vmax=1)
    axes[0].set_title(f"Final {size}x{size} lattice at T={temp}")
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    axes[1].plot(cycles, energies, label="E per spin")
    axes[1].axvline(burn_in_cycles, color="black", ls="--", lw=1, label="burn-in cutoff")
    axes[1].set_ylabel("E / spin")
    axes[1].legend()
    axes[2].plot(cycles, magnetisations, color="tab:green", label="M per spin")
    axes[2].axvline(burn_in_cycles, color="black", ls="--", lw=1, label="burn-in cutoff")
    axes[2].set_xlabel("Monte Carlo cycle")
    axes[2].set_ylabel("M / spin")
    axes[2].legend()
    save_figure(fig, figure_path)


def run_scan(args):
    temps = default_temperature_grid()
    generated = OUTPUT_DIR / "data" / "generated"
    processed = OUTPUT_DIR / "data" / "processed"
    figures = OUTPUT_DIR / "figures"
    logs = OUTPUT_DIR / "logs"
    for path in (generated, processed, figures, logs):
        path.mkdir(parents=True, exist_ok=True)

    timing_lines = [
        "Temperature scan timing log",
        f"sizes: {args.sizes}",
        f"temperatures: {len(temps)}",
        f"temperature_min: {temps.min()}",
        f"temperature_max: {temps.max()}",
        f"repeats: {args.repeats}",
        f"burn_in_cycles: {args.burn_in_cycles}",
        f"production_cycles: {args.production_cycles}",
    ]

    for size in args.sizes:
        start = time.perf_counter()
        repeat_rows = []
        for repeat in range(args.repeats):
            for temp_index, temp in enumerate(temps):
                seed = args.seed_base + size * 100000 + repeat * 1000 + temp_index
                repeat_rows.append(
                    run_temperature(
                        size,
                        float(temp),
                        repeat,
                        seed,
                        args.burn_in_cycles,
                        args.production_cycles,
                    )
                )

        summary_rows = summarise_repeat_rows(repeat_rows)
        write_csv(generated / f"{size}x{size}_repeats.csv", repeat_rows)
        write_csv(processed / f"{size}x{size}_summary.csv", summary_rows)
        write_dat(generated / f"{size}x{size}.dat", summary_rows)
        if not args.skip_render:
            plot_temperature_summary(
                size,
                summary_rows,
                figures / f"section_{args.section}_{size}x{size}_temperature_dependence.png",
            )
        elapsed = time.perf_counter() - start
        timing_lines.append(f"{size}x{size}_elapsed_seconds: {elapsed:.6f}")
        print(f"{size}x{size} complete in {elapsed:.2f} s")

    if args.equilibration_size:
        plot_equilibration(
            args.equilibration_size,
            args.equilibration_temp,
            args.seed_base + 999,
            args.burn_in_cycles,
            min(args.production_cycles, 400),
            figures
            / f"section_{args.section}_{args.equilibration_size}x{args.equilibration_size}_equilibration_T{str(args.equilibration_temp).replace('.', 'p')}.png",
            generated
            / f"section_{args.section}_{args.equilibration_size}x{args.equilibration_size}_equilibration_T{str(args.equilibration_temp).replace('.', 'p')}.csv",
            render=not args.skip_render,
        )

    log_path = logs / f"section_{args.section}_temperature_scan_timing.txt"
    log_path.write_text("\n".join(timing_lines) + "\n", encoding="utf-8")
    print(log_path.read_text())


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Ising temperature scan data.")
    parser.add_argument("--section", type=int, default=5)
    parser.add_argument("--sizes", type=int, nargs="+", default=[8])
    parser.add_argument("--repeats", type=int, default=6)
    parser.add_argument("--burn-in-cycles", type=int, default=300)
    parser.add_argument("--production-cycles", type=int, default=700)
    parser.add_argument("--seed-base", type=int, default=5000)
    parser.add_argument("--equilibration-size", type=int, default=8)
    parser.add_argument("--equilibration-temp", type=float, default=2.3)
    parser.add_argument("--skip-render", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_scan(parse_args())
