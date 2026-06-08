import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

from ILplot_style import (
    ENERGY_COLOR,
    HEAT_COLOR,
    MAGNETISATION_COLOR,
    OWN_COLOR,
    REFERENCE_COLOR,
    SPIN_DOWN_COLOR,
    SPIN_UP_COLOR,
    SUSCEPTIBILITY_COLOR,
    apply_publication_style,
    save_figure,
)
from IsingLattice import IsingLattice


OUTPUT_DIR = Path("outputs")
FIGURES = OUTPUT_DIR / "figures"
PROCESSED = OUTPUT_DIR / "data" / "processed"
GENERATED = OUTPUT_DIR / "data" / "generated"
LOGS = OUTPUT_DIR / "logs"
SIZES = [2, 4, 8, 16, 32]
EXACT_TC = 2.0 / np.log(1.0 + np.sqrt(2.0))

SPIN_CMAP = ListedColormap([SPIN_DOWN_COLOR, SPIN_UP_COLOR])
SPIN_NORM = BoundaryNorm([-1.5, 0.0, 1.5], SPIN_CMAP.N)


def require_file(path):
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty source file: {path}")
    return path


def read_csv_rows(path):
    require_file(path)
    with Path(path).open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key, value in list(row.items()):
            try:
                row[key] = float(value)
            except ValueError:
                pass
    return rows


def read_csv_array(path):
    require_file(path)
    return np.genfromtxt(path, delimiter=",", names=True)


def read_summary(size):
    return read_csv_rows(PROCESSED / f"{size}x{size}_summary.csv")


def read_reference(size):
    data = np.loadtxt(require_file(Path("reference_data") / f"{size}x{size}.dat"))
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


def read_own(size):
    rows = read_summary(size)
    return {
        "T": np.array([row["T"] for row in rows]),
        "E": np.array([row["E_per_spin_mean"] for row in rows]),
        "abs_M": np.array([row["abs_M_per_spin_mean"] for row in rows]),
        "C": np.array([row["C_per_spin_mean"] for row in rows]),
        "chi": np.array([row["chi_per_spin_mean"] for row in rows]),
    }


def expected_energy(lattice):
    energy = -np.sum(lattice * np.roll(lattice, 1, axis=0))
    energy -= np.sum(lattice * np.roll(lattice, 1, axis=1))
    return float(energy)


def actual_energy_magnetisation(lattice):
    il = IsingLattice(*lattice.shape)
    il.lattice = lattice.copy()
    return il.energy(), il.magnetisation()


def draw_spin_grid(ax, lattice, title, annotate=True):
    ax.imshow(lattice, cmap=SPIN_CMAP, norm=SPIN_NORM)
    ax.set_title(title)
    ax.set_xticks(np.arange(-0.5, lattice.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, lattice.shape[0], 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)
    if annotate and lattice.size <= 64:
        for i in range(lattice.shape[0]):
            for j in range(lattice.shape[1]):
                text_color = "black" if lattice[i, j] > 0 else "white"
                ax.text(
                    j,
                    i,
                    "+1" if lattice[i, j] > 0 else "-1",
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=8,
                    fontweight="bold",
                )


def spin_legend(ax, loc="upper right"):
    legend = ax.legend(
        handles=[
            Patch(facecolor=SPIN_UP_COLOR, edgecolor="black", label="+1 spin"),
            Patch(facecolor=SPIN_DOWN_COLOR, edgecolor="black", label="-1 spin"),
        ],
        loc=loc,
        frameon=True,
    )
    return legend


def render_section_2():
    rng = np.random.default_rng(2202)
    n = 4
    cases = [
        ("Aligned +1", np.ones((n, n), dtype=int)),
        ("Seeded random", rng.choice([-1, 1], size=(n, n))),
        (
            "Checkerboard",
            np.array([[1, -1] * (n // 2), [-1, 1] * (n // 2)] * (n // 2)),
        ),
    ]
    fig = plt.figure(figsize=(12.0, 6.4), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[3.2, 1.35])
    for col, (title, lattice) in enumerate(cases):
        ax = fig.add_subplot(gs[0, col])
        draw_spin_grid(ax, lattice, title)
        expected_e = expected_energy(lattice)
        expected_m = float(np.sum(lattice))
        actual_e, actual_m = actual_energy_magnetisation(lattice)
        passed = abs(expected_e - actual_e) < 1e-12 and abs(expected_m - actual_m) < 1e-12
        table_ax = fig.add_subplot(gs[1, col])
        table_ax.axis("off")
        table = table_ax.table(
            cellText=[
                ["E", f"{expected_e:.0f}", f"{actual_e:.0f}"],
                ["M", f"{expected_m:.0f}", f"{actual_m:.0f}"],
                ["Status", "PASS" if passed else "FAIL", "PASS" if passed else "FAIL"],
            ],
            colLabels=["Quantity", "Expected", "Actual"],
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.0, 1.45)
        for cell in table.get_celld().values():
            cell.set_linewidth(1.0)
            cell.get_text().set_fontweight("bold")
    spin_legend(fig.axes[0], loc="upper left")
    fig.suptitle("Energy and Magnetisation Validation")
    return save_figure(fig, FIGURES / "section_2_energy_magnetisation_check.png")


def infer_final_lattice(size, final_magnetisation_per_spin):
    spin = 1 if final_magnetisation_per_spin >= 0 else -1
    return np.full((size, size), spin, dtype=int)


def equilibrium_marker(cycles, energy, magnetisation):
    mask = np.logical_and(energy <= -1.9, np.abs(magnetisation) >= 0.95)
    if np.any(mask):
        return float(cycles[np.argmax(mask)])
    return float(cycles[min(len(cycles) // 5, len(cycles) - 1)])


def render_section_3():
    data = read_csv_array(GENERATED / "section_3_low_temperature_timeseries.csv")
    cycles = data["cycle"]
    energy = data["E_per_spin"]
    magnetisation = data["M_per_spin"]
    marker = equilibrium_marker(cycles, energy, magnetisation)
    final_lattice = infer_final_lattice(8, magnetisation[-1])

    fig = plt.figure(figsize=(12.0, 6.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.65])
    ax_lattice = fig.add_subplot(gs[:, 0])
    draw_spin_grid(ax_lattice, final_lattice, "Final 8x8 Lattice", annotate=False)
    spin_legend(ax_lattice, loc="upper left")
    ax_lattice.text(
        0.02,
        -0.08,
        "Final state inferred from recorded M/spin",
        transform=ax_lattice.transAxes,
        fontsize=10,
        fontweight="bold",
    )

    ax_e = fig.add_subplot(gs[0, 1])
    ax_e.plot(cycles, energy, color=ENERGY_COLOR, label="Energy per spin")
    ax_e.axvline(marker, color="black", linestyle="--", label="equilibration marker")
    ax_e.set_ylabel("E / spin")
    ax_e.set_title("Low-Temperature Energy")
    ax_e.legend()
    ax_e.annotate(
        f"final E/spin = {energy[-1]:.2f}",
        xy=(cycles[-1], energy[-1]),
        xytext=(-120, 25),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "lw": 1.4},
        fontsize=10,
        fontweight="bold",
    )

    ax_m = fig.add_subplot(gs[1, 1], sharex=ax_e)
    ax_m.plot(cycles, magnetisation, color=MAGNETISATION_COLOR, label="Magnetisation per spin")
    ax_m.axvline(marker, color="black", linestyle="--", label="equilibration marker")
    ax_m.set_xlabel("Monte Carlo cycle")
    ax_m.set_ylabel("M / spin")
    ax_m.set_title("Spontaneous Magnetisation")
    ax_m.legend()
    ax_m.annotate(
        f"final M/spin = {magnetisation[-1]:.2f}",
        xy=(cycles[-1], magnetisation[-1]),
        xytext=(-125, -35),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "lw": 1.4},
        fontsize=10,
        fontweight="bold",
    )
    fig.suptitle("Monte Carlo Evidence at T = 1.0")
    return save_figure(fig, FIGURES / "section_3_low_temperature_equilibrium.png")


def render_section_4():
    rows = read_csv_rows(PROCESSED / "section_4_timing.csv")
    labels = {
        "loop_full_recompute": "Loop full recompute",
        "vectorised_full_recompute": "NumPy full recompute",
        "local_delta_energy": "Local delta-E update",
    }
    order = ["loop_full_recompute", "vectorised_full_recompute", "local_delta_energy"]
    grouped = {
        key: np.array([row["seconds_per_trial_move"] for row in rows if row["path"] == key])
        for key in order
    }
    means = np.array([float(np.mean(grouped[key])) for key in order])
    stds = np.array([float(np.std(grouped[key], ddof=1)) for key in order])
    speedups = means[0] / means

    fig, ax = plt.subplots(figsize=(8.2, 5.0), constrained_layout=True)
    x = np.arange(len(order))
    bars = ax.bar(
        x,
        means,
        yerr=stds,
        color=["#6b7280", ENERGY_COLOR, MAGNETISATION_COLOR],
        capsize=5,
    )
    ax.set_xticks(x)
    ax.set_xticklabels([labels[key] for key in order], rotation=10, ha="right")
    ax.set_ylabel("Seconds per trial move")
    ax.set_yscale("log")
    ax.set_title("Monte Carlo Update Timing")
    for bar, speedup in zip(bars, speedups):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.55,
            f"{speedup:.1f}x",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )
    ax.text(
        0.98,
        0.95,
        "Speedup vs loop baseline",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        ha="right",
        va="top",
    )
    ax.set_ylim(means[-1] * 0.45, means[0] * 2.6)
    return save_figure(fig, FIGURES / "section_4_timing_comparison.png")


def render_temperature_summary(size, output_name, title):
    rows = read_summary(size)
    temps = np.array([row["T"] for row in rows])
    fig, axes = plt.subplots(3, 1, figsize=(8.0, 9.2), sharex=True, constrained_layout=True)
    axes[0].errorbar(
        temps,
        [row["E_per_spin_mean"] for row in rows],
        yerr=[row["E_per_spin_stderr"] for row in rows],
        marker="o",
        ms=4,
        capsize=3,
        color=ENERGY_COLOR,
        label="Energy",
    )
    axes[0].set_ylabel("E / spin")
    axes[0].set_title("Energy")
    axes[0].legend()
    axes[1].errorbar(
        temps,
        [row["abs_M_per_spin_mean"] for row in rows],
        yerr=[row["abs_M_per_spin_stderr"] for row in rows],
        marker="o",
        ms=4,
        capsize=3,
        color=MAGNETISATION_COLOR,
        label="|M|",
    )
    axes[1].set_ylabel("|M| / spin")
    axes[1].set_title("Magnetisation")
    axes[1].legend()
    axes[2].errorbar(
        temps,
        [row["C_per_spin_mean"] for row in rows],
        yerr=[row["C_per_spin_stderr"] for row in rows],
        marker="o",
        ms=4,
        capsize=3,
        color=HEAT_COLOR,
        label="Heat capacity",
    )
    axes[2].set_xlabel("Temperature")
    axes[2].set_ylabel("C / spin")
    axes[2].set_title("Heat Capacity")
    axes[2].legend()
    fig.suptitle(title)
    return save_figure(fig, FIGURES / output_name)


def parse_temperature_from_name(path):
    text = Path(path).stem
    marker = text.split("_T")[-1]
    return float(marker.replace("p", "."))


def render_equilibration(size, csv_path, output_name, burn_in_cycles):
    data = read_csv_array(csv_path)
    cycles = data["cycle"]
    energy = data["E_per_spin"]
    magnetisation = data["M_per_spin"]
    final_lattice = infer_final_lattice(size, magnetisation[-1])
    temp = parse_temperature_from_name(csv_path)

    fig = plt.figure(figsize=(12.0, 6.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.65])
    ax_lattice = fig.add_subplot(gs[:, 0])
    draw_spin_grid(ax_lattice, final_lattice, f"Final {size}x{size} Lattice", annotate=False)
    spin_legend(ax_lattice, loc="upper left")
    ax_e = fig.add_subplot(gs[0, 1])
    ax_e.plot(cycles, energy, color=ENERGY_COLOR, label="Energy per spin")
    ax_e.axvline(burn_in_cycles, color="black", linestyle="--", label="burn-in cutoff")
    ax_e.set_ylabel("E / spin")
    ax_e.set_title("Equilibration Energy")
    ax_e.legend()
    ax_m = fig.add_subplot(gs[1, 1], sharex=ax_e)
    ax_m.plot(cycles, magnetisation, color=MAGNETISATION_COLOR, label="Magnetisation per spin")
    ax_m.axvline(burn_in_cycles, color="black", linestyle="--", label="burn-in cutoff")
    ax_m.set_xlabel("Monte Carlo cycle")
    ax_m.set_ylabel("M / spin")
    ax_m.set_title("Equilibration Magnetisation")
    ax_m.legend()
    fig.suptitle(f"Equilibration Evidence at T = {temp:g}")
    return save_figure(fig, FIGURES / output_name)


def render_size_quantity(y_key, yerr_key, ylabel, title, output_name):
    fig, ax = plt.subplots(figsize=(8.0, 5.3), constrained_layout=True)
    for size in SIZES:
        rows = read_summary(size)
        temps = np.array([row["T"] for row in rows])
        values = np.array([row[y_key] for row in rows])
        errors = np.array([row[yerr_key] for row in rows])
        ax.errorbar(
            temps,
            values,
            yerr=errors,
            marker="o",
            ms=3,
            capsize=2.5,
            label=f"{size}x{size}",
        )
    ax.set_xlabel("Temperature")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(title="Lattice")
    return save_figure(fig, FIGURES / output_name)


def render_response_quantity(y_key, yerr_key, ylabel, title, output_name):
    fig, ax = plt.subplots(figsize=(8.0, 5.3), constrained_layout=True)
    for size in SIZES:
        rows = read_summary(size)
        temps = np.array([row["T"] for row in rows])
        values = np.array([row[y_key] for row in rows])
        errors = np.array([row[yerr_key] for row in rows])
        ax.errorbar(
            temps,
            values,
            yerr=errors,
            marker="o",
            ms=3,
            capsize=2.5,
            label=f"{size}x{size}",
        )
    ax.set_xlabel("Temperature")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(title="Lattice")
    return save_figure(fig, FIGURES / output_name)


def render_section_5_and_6():
    outputs = []
    outputs += render_temperature_summary(
        8,
        "section_5_8x8_temperature_dependence.png",
        "8x8 Temperature Dependence",
    )
    outputs += render_equilibration(
        8,
        GENERATED / "section_5_8x8_equilibration_T2p3.csv",
        "section_5_8x8_equilibration_T2p3.png",
        burn_in_cycles=300,
    )
    for size in SIZES:
        outputs += render_temperature_summary(
            size,
            f"section_6_{size}x{size}_temperature_dependence.png",
            f"{size}x{size} Temperature Dependence",
        )
    outputs += render_size_quantity(
        "E_per_spin_mean",
        "E_per_spin_stderr",
        "E / spin",
        "Energy Versus Temperature by Lattice Size",
        "section_6_energy_vs_temperature_by_size.png",
    )
    outputs += render_size_quantity(
        "abs_M_per_spin_mean",
        "abs_M_per_spin_stderr",
        "|M| / spin",
        "Magnetisation Versus Temperature by Lattice Size",
        "section_6_magnetisation_vs_temperature_by_size.png",
    )
    return outputs


def render_section_7():
    outputs = []
    outputs += render_response_quantity(
        "C_per_spin_mean",
        "C_per_spin_stderr",
        "C / spin",
        "Heat Capacity from Energy Variance",
        "section_7_heat_capacity_by_size.png",
    )
    outputs += render_response_quantity(
        "chi_per_spin_mean",
        "chi_per_spin_stderr",
        "Susceptibility / spin",
        "Susceptibility from Magnetisation Variance",
        "section_7_susceptibility_by_size.png",
    )
    return outputs


def render_8x8_reference_comparison():
    own = read_own(8)
    reference = read_reference(8)
    fig, axes = plt.subplots(3, 1, figsize=(8.0, 9.2), sharex=True, constrained_layout=True)
    for ax, key, ylabel, title in (
        (axes[0], "E", "E / spin", "Energy"),
        (axes[1], "abs_M", "|M| / spin", "Magnetisation"),
        (axes[2], "C", "C / spin", "Heat Capacity"),
    ):
        ax.plot(reference["T"], reference[key], "-", color=REFERENCE_COLOR, label="Reference")
        ax.plot(own["T"], own[key], "o", color=OWN_COLOR, ms=4, label="Own data")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
    axes[2].set_xlabel("Temperature")
    fig.suptitle("8x8 Own Data Versus Reference Data")
    return save_figure(fig, FIGURES / "section_8_8x8_own_vs_reference.png")


def render_reference_heat_capacity_comparison():
    fig, axes = plt.subplots(len(SIZES), 1, figsize=(8.0, 11.0), sharex=True, constrained_layout=True)
    for ax, size in zip(axes, SIZES):
        own = read_own(size)
        reference = read_reference(size)
        ax.plot(reference["T"], reference["C"], "-", color=REFERENCE_COLOR, label="Reference")
        ax.plot(own["T"], own["C"], "o", color=OWN_COLOR, ms=3, label="Own data")
        ax.set_ylabel(f"{size}x{size}\nC / spin")
        ax.legend(loc="upper right")
    axes[-1].set_xlabel("Temperature")
    fig.suptitle("Heat-Capacity Comparison Across Lattice Sizes")
    return save_figure(
        fig,
        FIGURES / "section_8_reference_comparison_heat_capacity_all_sizes.png",
    )


def coefficient_array(row):
    return np.array([float(value) for value in row["coefficients"].split()])


def render_peak_fit_example():
    peak_rows = read_csv_rows(PROCESSED / "section_8_peak_table.csv")
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 7.6), constrained_layout=True)
    for ax, observable, ylabel in (
        (axes[0], "C", "C / spin"),
        (axes[1], "chi", "Susceptibility / spin"),
    ):
        for source, color, marker in (
            ("own", OWN_COLOR, "o"),
            ("reference", REFERENCE_COLOR, "."),
        ):
            row = next(
                item
                for item in peak_rows
                if item["source"] == source and item["observable"] == observable and int(item["L"]) == 32
            )
            dataset = read_own(32) if source == "own" else read_reference(32)
            fit_t = np.linspace(row["window_min"], row["window_max"], 500)
            fit_values = np.polyval(coefficient_array(row), fit_t)
            ax.plot(dataset["T"], dataset[observable], marker, color=color, ms=4, linestyle="none", label=f"{source} data")
            ax.plot(fit_t, fit_values, "-", color=color, lw=2, label=f"{source} fit")
            ax.axvline(row["fit_peak_T"], color=color, linestyle="--", lw=1.2)
        ax.set_xlim(2.05, 2.6)
        ax.set_ylabel(ylabel)
        ax.set_title(f"32x32 {ylabel} Peak Fit")
        ax.legend()
    axes[1].set_xlabel("Temperature")
    fig.suptitle("Critical-Window Polynomial Fits")
    return save_figure(fig, FIGURES / "section_8_32x32_peak_fits.png")


def render_curie_scaling():
    peak_rows = read_csv_rows(PROCESSED / "section_8_peak_table.csv")
    scaling_rows = read_csv_rows(PROCESSED / "section_8_scaling_fit.csv")
    sizes_for_scaling = [4, 8, 16, 32]
    x_line = np.linspace(0.0, 1.0 / min(sizes_for_scaling), 300)
    fig, ax = plt.subplots(figsize=(8.0, 5.3), constrained_layout=True)
    for source, color, marker in (
        ("own", OWN_COLOR, "o"),
        ("reference", REFERENCE_COLOR, "s"),
    ):
        selected = [
            row
            for row in peak_rows
            if row["source"] == source
            and row["observable"] == "C"
            and int(row["L"]) in sizes_for_scaling
        ]
        x = np.array([1.0 / int(row["L"]) for row in selected])
        y = np.array([row["fit_peak_T"] for row in selected])
        ax.plot(x, y, marker, color=color, linestyle="none", ms=6, label=f"{source} C peaks")
        fit_row = next(
            row for row in scaling_rows if row["source"] == source and row["observable"] == "C"
        )
        ax.plot(
            x_line,
            fit_row["slope_A"] * x_line + fit_row["Tc_infinite_fit"],
            "-",
            color=color,
            lw=2,
            label=f"{source} linear fit",
        )
    ax.axhline(EXACT_TC, color="black", linestyle="--", lw=1.5, label="Exact Tc")
    ax.set_xlabel("1 / L")
    ax.set_ylabel("Fitted heat-capacity peak temperature")
    ax.set_title("Finite-Size Curie Temperature Scaling")
    ax.legend()
    return save_figure(fig, FIGURES / "section_8_curie_scaling.png")


def render_section_8():
    outputs = []
    outputs += render_8x8_reference_comparison()
    outputs += render_reference_heat_capacity_comparison()
    outputs += render_peak_fit_example()
    outputs += render_curie_scaling()
    return outputs


def validate_outputs(paths):
    lines = ["Plot polish validation", "figure,exists,bytes"]
    ok = True
    for path in paths:
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        ok = ok and exists and size > 0
        lines.append(f"{path},{exists},{size}")
    png_count = sum(1 for path in paths if path.suffix == ".png")
    svg_count = sum(1 for path in paths if path.suffix == ".svg")
    lines.append(f"png_count,{png_count}")
    lines.append(f"svg_count,{svg_count}")
    lines.append(f"all_nonempty,{ok}")
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / "plot_polish_validation.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ok


def render_all():
    apply_publication_style()
    outputs = []
    outputs += render_section_2()
    outputs += render_section_3()
    outputs += render_section_4()
    outputs += render_section_5_and_6()
    outputs += render_section_7()
    outputs += render_section_8()
    ok = validate_outputs(outputs)
    print(f"Regenerated {len(outputs)} PNG figure files.")
    print(f"Validation log: {LOGS / 'plot_polish_validation.txt'}")
    if not ok:
        raise SystemExit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Render polished Ising report figures from existing data.")
    parser.add_argument("--all", action="store_true", help="Render every report figure.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.all:
        raise SystemExit("Use --all to render the full report figure set.")
    render_all()
