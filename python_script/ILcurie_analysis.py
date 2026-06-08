import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ILplot_style import save_figure


OUTPUT_DIR = Path("outputs")
EXACT_TC = 2.0 / np.log(1.0 + np.sqrt(2.0))
FIT_WINDOWS = {
    2: (1.5, 3.2),
    4: (1.7, 2.9),
    8: (1.9, 2.8),
    16: (2.0, 2.65),
    32: (2.05, 2.6),
}


def read_own(size):
    path = OUTPUT_DIR / "data" / "processed" / f"{size}x{size}_summary.csv"
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    data = {
        "T": np.array([float(row["T"]) for row in rows]),
        "E": np.array([float(row["E_per_spin_mean"]) for row in rows]),
        "abs_M": np.array([float(row["abs_M_per_spin_mean"]) for row in rows]),
        "C": np.array([float(row["C_per_spin_mean"]) for row in rows]),
        "chi": np.array([float(row["chi_per_spin_mean"]) for row in rows]),
    }
    return data


def read_reference(size):
    data = np.loadtxt(Path("reference_data") / f"{size}x{size}.dat")
    temperature = data[:, 0]
    magnetisation = data[:, 3]
    magnetisation2 = data[:, 4]
    spins = size * size
    chi = spins * np.maximum(0.0, magnetisation2 - magnetisation**2) / temperature
    return {
        "T": temperature,
        "E": data[:, 1],
        "abs_M": np.abs(magnetisation),
        "C": np.maximum(0.0, data[:, 5]),
        "chi": chi,
    }


def fit_peak(temperature, values, window, degree):
    selection = np.logical_and(temperature >= window[0], temperature <= window[1])
    fit_temperature = temperature[selection]
    fit_values = values[selection]
    fit_degree = min(degree, len(fit_temperature) - 1)
    coefficients = np.polyfit(fit_temperature, fit_values, fit_degree)
    peak_temperature_grid = np.linspace(window[0], window[1], 2000)
    fitted_values = np.polyval(coefficients, peak_temperature_grid)
    peak_index = int(np.argmax(fitted_values))
    raw_index = int(np.argmax(fit_values))
    return {
        "degree": fit_degree,
        "coefficients": coefficients,
        "peak_T": float(peak_temperature_grid[peak_index]),
        "peak_value": float(fitted_values[peak_index]),
        "raw_peak_T": float(fit_temperature[raw_index]),
        "raw_peak_value": float(fit_values[raw_index]),
        "grid_T": peak_temperature_grid,
        "grid_values": fitted_values,
        "fit_T": fit_temperature,
        "fit_values": fit_values,
    }


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def peak_rows(sizes, degree):
    rows = []
    fit_cache = {}
    for source, reader in (("own", read_own), ("reference", read_reference)):
        for size in sizes:
            dataset = reader(size)
            window = FIT_WINDOWS[size]
            for observable in ("C", "chi"):
                fit = fit_peak(dataset["T"], dataset[observable], window, degree)
                rows.append(
                    {
                        "source": source,
                        "observable": observable,
                        "L": size,
                        "window_min": window[0],
                        "window_max": window[1],
                        "degree": fit["degree"],
                        "raw_peak_T": fit["raw_peak_T"],
                        "raw_peak_value": fit["raw_peak_value"],
                        "fit_peak_T": fit["peak_T"],
                        "fit_peak_value": fit["peak_value"],
                        "coefficients": " ".join(f"{c:.12g}" for c in fit["coefficients"]),
                    }
                )
                fit_cache[(source, size, observable)] = (dataset, fit)
    return rows, fit_cache


def scaling_rows(peak_table, sizes_for_scaling):
    rows = []
    for source in ("own", "reference"):
        for observable in ("C", "chi"):
            selected = [
                row
                for row in peak_table
                if row["source"] == source
                and row["observable"] == observable
                and int(row["L"]) in sizes_for_scaling
            ]
            x = np.array([1.0 / int(row["L"]) for row in selected])
            y = np.array([float(row["fit_peak_T"]) for row in selected])
            slope, intercept = np.polyfit(x, y, 1)
            rows.append(
                {
                    "source": source,
                    "observable": observable,
                    "sizes_used": " ".join(str(row["L"]) for row in selected),
                    "slope_A": slope,
                    "Tc_infinite_fit": intercept,
                    "exact_Tc": EXACT_TC,
                    "fit_minus_exact": intercept - EXACT_TC,
                }
            )
    return rows


def plot_8x8_comparison():
    own = read_own(8)
    reference = read_reference(8)
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 9.0), constrained_layout=True)
    for ax, key, ylabel in (
        (axes[0], "E", "E / spin"),
        (axes[1], "abs_M", "|M| / spin"),
        (axes[2], "C", "C / spin"),
    ):
        ax.plot(reference["T"], reference[key], "-", lw=1.2, label="reference")
        ax.plot(own["T"], own[key], "o", ms=3, label="own")
        ax.set_ylabel(ylabel)
        ax.legend()
    axes[2].set_xlabel("Temperature")
    fig.suptitle("8x8 own data versus reference data")
    save_figure(fig, OUTPUT_DIR / "figures" / "section_8_8x8_own_vs_reference.png")


def plot_all_size_reference_comparison(sizes):
    fig, axes = plt.subplots(len(sizes), 1, figsize=(7.2, 10.5), sharex=True, constrained_layout=True)
    for ax, size in zip(axes, sizes):
        own = read_own(size)
        reference = read_reference(size)
        ax.plot(reference["T"], reference["C"], "-", lw=1.2, label="reference")
        ax.plot(own["T"], own["C"], "o", ms=2.8, label="own")
        ax.set_ylabel(f"{size}x{size}\nC/spin")
        ax.legend(loc="upper right")
    axes[-1].set_xlabel("Temperature")
    fig.suptitle("Heat-capacity comparison for all lattice sizes")
    save_figure(
        fig,
        OUTPUT_DIR / "figures" / "section_8_reference_comparison_heat_capacity_all_sizes.png",
    )


def plot_peak_fit_example(fit_cache):
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 7.2), constrained_layout=True)
    for ax, observable, ylabel in (
        (axes[0], "C", "C / spin"),
        (axes[1], "chi", "chi / spin"),
    ):
        for source, marker in (("own", "o"), ("reference", ".")):
            dataset, fit = fit_cache[(source, 32, observable)]
            ax.plot(dataset["T"], dataset[observable], marker, ms=3, linestyle="none", label=f"{source} data")
            ax.plot(fit["grid_T"], fit["grid_values"], "-", lw=1.2, label=f"{source} polynomial fit")
        ax.set_xlim(FIT_WINDOWS[32])
        ax.set_ylabel(ylabel)
        ax.legend()
    axes[1].set_xlabel("Temperature")
    fig.suptitle("32x32 critical-window polynomial peak fits")
    save_figure(fig, OUTPUT_DIR / "figures" / "section_8_32x32_peak_fits.png")


def plot_scaling(peak_table, scaling_table, sizes_for_scaling):
    fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    x_line = np.linspace(0.0, 1.0 / min(sizes_for_scaling), 200)
    for source, marker in (("own", "o"), ("reference", "s")):
        selected = [
            row
            for row in peak_table
            if row["source"] == source
            and row["observable"] == "C"
            and int(row["L"]) in sizes_for_scaling
        ]
        x = np.array([1.0 / int(row["L"]) for row in selected])
        y = np.array([float(row["fit_peak_T"]) for row in selected])
        ax.plot(x, y, marker, linestyle="none", label=f"{source} C peaks")
        fit_row = next(
            row
            for row in scaling_table
            if row["source"] == source and row["observable"] == "C"
        )
        ax.plot(
            x_line,
            fit_row["slope_A"] * x_line + fit_row["Tc_infinite_fit"],
            "-",
            lw=1.2,
            label=f"{source} linear fit",
        )
    ax.axhline(EXACT_TC, color="black", ls="--", lw=1, label="exact Tc")
    ax.set_xlabel("1 / L")
    ax.set_ylabel("Fitted heat-capacity peak temperature")
    ax.legend()
    save_figure(fig, OUTPUT_DIR / "figures" / "section_8_curie_scaling.png")


def main(args):
    (OUTPUT_DIR / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "logs").mkdir(parents=True, exist_ok=True)
    peak_table, fit_cache = peak_rows(args.sizes, args.degree)
    scaling_table = scaling_rows(peak_table, args.scaling_sizes)
    write_csv(OUTPUT_DIR / "data" / "processed" / "section_8_peak_table.csv", peak_table)
    write_csv(OUTPUT_DIR / "data" / "processed" / "section_8_scaling_fit.csv", scaling_table)
    if not args.skip_render:
        plot_8x8_comparison()
        plot_all_size_reference_comparison(args.sizes)
        plot_peak_fit_example(fit_cache)
        plot_scaling(peak_table, scaling_table, args.scaling_sizes)

    lines = [
        "Section 8 fit summary",
        f"exact_Tc: {EXACT_TC:.12f}",
        "source,observable,Tc_infinite_fit,fit_minus_exact",
    ]
    for row in scaling_table:
        lines.append(
            f"{row['source']},{row['observable']},{row['Tc_infinite_fit']:.12g},{row['fit_minus_exact']:.12g}"
        )
    (OUTPUT_DIR / "logs" / "section_8_fit_summary.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print("\n".join(lines))


def parse_args():
    parser = argparse.ArgumentParser(description="Fit finite-size Curie temperature estimates.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[2, 4, 8, 16, 32])
    parser.add_argument("--scaling-sizes", type=int, nargs="+", default=[4, 8, 16, 32])
    parser.add_argument("--degree", type=int, default=4)
    parser.add_argument("--skip-render", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
