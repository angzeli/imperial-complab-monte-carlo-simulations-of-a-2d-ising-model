import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUTPUT_DIR = Path("outputs")


def read_summary(size):
    path = OUTPUT_DIR / "data" / "processed" / f"{size}x{size}_summary.csv"
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key, value in list(row.items()):
            try:
                row[key] = float(value)
            except ValueError:
                pass
    return rows


def write_compiled_table(sizes):
    rows = []
    for size in sizes:
        for row in read_summary(size):
            rows.append(
                {
                    "L": size,
                    "T": row["T"],
                    "E_per_spin_mean": row["E_per_spin_mean"],
                    "E_per_spin_stderr": row["E_per_spin_stderr"],
                    "abs_M_per_spin_mean": row["abs_M_per_spin_mean"],
                    "abs_M_per_spin_stderr": row["abs_M_per_spin_stderr"],
                    "acceptance_rate_mean": row["acceptance_rate_mean"],
                }
            )
    out = OUTPUT_DIR / "data" / "processed" / "section_6_size_effects_table.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return out


def plot_quantity(sizes, y_key, yerr_key, ylabel, figure_path):
    fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    for size in sizes:
        rows = read_summary(size)
        temps = np.array([row["T"] for row in rows])
        values = np.array([row[y_key] for row in rows])
        errors = np.array([row[yerr_key] for row in rows])
        ax.errorbar(
            temps,
            values,
            yerr=errors,
            marker="o",
            ms=2.5,
            lw=1,
            capsize=2,
            label=f"{size}x{size}",
        )
    ax.set_xlabel("Temperature")
    ax.set_ylabel(ylabel)
    ax.legend(title="Lattice")
    fig.savefig(figure_path, dpi=200)
    plt.close(fig)


def write_reference_inventory(sizes):
    lines = ["Section 6 reference-data inventory"]
    for size in sizes:
        path = Path("reference_data") / f"{size}x{size}.dat"
        if path.exists():
            data = np.loadtxt(path)
            lines.append(
                f"{size}x{size}: rows={data.shape[0]}, columns={data.shape[1]}, "
                f"T_min={data[:,0].min():.12g}, T_max={data[:,0].max():.12g}"
            )
        else:
            lines.append(f"{size}x{size}: missing")
    out = OUTPUT_DIR / "logs" / "section_6_reference_inventory.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main(args):
    (OUTPUT_DIR / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "logs").mkdir(parents=True, exist_ok=True)
    table = write_compiled_table(args.sizes)
    plot_quantity(
        args.sizes,
        "E_per_spin_mean",
        "E_per_spin_stderr",
        "E / spin",
        OUTPUT_DIR / "figures" / "section_6_energy_vs_temperature_by_size.png",
    )
    plot_quantity(
        args.sizes,
        "abs_M_per_spin_mean",
        "abs_M_per_spin_stderr",
        "|M| / spin",
        OUTPUT_DIR / "figures" / "section_6_magnetisation_vs_temperature_by_size.png",
    )
    inventory = write_reference_inventory(args.sizes)
    print(f"Wrote {table}")
    print(f"Wrote {inventory}")


def parse_args():
    parser = argparse.ArgumentParser(description="Plot Ising system-size effects.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[2, 4, 8, 16, 32])
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
