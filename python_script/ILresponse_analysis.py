import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ILplot_style import save_figure


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


def compile_response_table(sizes):
    rows = []
    for size in sizes:
        for row in read_summary(size):
            rows.append(
                {
                    "L": size,
                    "T": row["T"],
                    "C_per_spin": row["C_per_spin_mean"],
                    "C_per_spin_stderr": row["C_per_spin_stderr"],
                    "chi_per_spin": row["chi_per_spin_mean"],
                    "chi_per_spin_stderr": row["chi_per_spin_stderr"],
                    "E_per_spin": row["E_per_spin_mean"],
                    "M_per_spin": row["M_per_spin_mean"],
                    "abs_M_per_spin": row["abs_M_per_spin_mean"],
                }
            )
    return rows


def write_response_table(rows):
    out = OUTPUT_DIR / "data" / "processed" / "section_7_response_functions.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return out


def plot_response(sizes, y_key, yerr_key, ylabel, title, figure_path):
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
    ax.set_title(title)
    ax.legend(title="Lattice")
    save_figure(fig, figure_path)


def main(args):
    (OUTPUT_DIR / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    rows = compile_response_table(args.sizes)
    table = write_response_table(rows)
    if not args.skip_render:
        plot_response(
            args.sizes,
            "C_per_spin_mean",
            "C_per_spin_stderr",
            "C / spin",
            "Heat capacity from energy variance",
            OUTPUT_DIR / "figures" / "section_7_heat_capacity_by_size.png",
        )
        plot_response(
            args.sizes,
            "chi_per_spin_mean",
            "chi_per_spin_stderr",
            "chi / spin",
            "Magnetic susceptibility from magnetisation variance",
            OUTPUT_DIR / "figures" / "section_7_susceptibility_by_size.png",
        )
    print(f"Wrote {table}")


def parse_args():
    parser = argparse.ArgumentParser(description="Plot Ising response functions.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[2, 4, 8, 16, 32])
    parser.add_argument("--skip-render", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
