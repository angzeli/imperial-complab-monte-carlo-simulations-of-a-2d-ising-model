from pathlib import Path

import matplotlib.pyplot as plt


TITLE_SIZE = 18
LABEL_SIZE = 22
TICK_SIZE = 14
LEGEND_SIZE = 10
SPINE_WIDTH = 1.8

SPIN_DOWN_COLOR = "#2f6fbb"
SPIN_UP_COLOR = "#f2c14e"
ENERGY_COLOR = "#2563eb"
MAGNETISATION_COLOR = "#059669"
HEAT_COLOR = "#dc2626"
SUSCEPTIBILITY_COLOR = "#7c3aed"
REFERENCE_COLOR = "#111827"
OWN_COLOR = "#f97316"


def apply_publication_style():
    plt.rcParams.update(
        {
            "axes.linewidth": SPINE_WIDTH,
            "axes.titleweight": "bold",
            "axes.titlesize": TITLE_SIZE,
            "axes.labelweight": "bold",
            "axes.labelsize": LABEL_SIZE,
            "xtick.labelsize": TICK_SIZE,
            "ytick.labelsize": TICK_SIZE,
            "legend.fontsize": LEGEND_SIZE,
            "legend.title_fontsize": LEGEND_SIZE,
            "lines.linewidth": 2.0,
            "patch.linewidth": 1.0,
            "savefig.dpi": 300,
            "svg.fonttype": "none",
        }
    )


def style_axis(ax):
    for spine in ax.spines.values():
        spine.set_linewidth(SPINE_WIDTH)
    ax.title.set_fontweight("bold")
    ax.title.set_fontsize(TITLE_SIZE)
    ax.xaxis.label.set_fontweight("bold")
    ax.xaxis.label.set_fontsize(LABEL_SIZE)
    ax.yaxis.label.set_fontweight("bold")
    ax.yaxis.label.set_fontsize(LABEL_SIZE)
    ax.tick_params(width=SPINE_WIDTH, length=6)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight("bold")
        label.set_fontsize(TICK_SIZE)
    legend = ax.get_legend()
    if legend is not None:
        style_legend(legend)


def style_legend(legend):
    for text in legend.get_texts():
        text.set_fontweight("bold")
        text.set_fontsize(LEGEND_SIZE)
    title = legend.get_title()
    if title is not None:
        title.set_fontweight("bold")
        title.set_fontsize(LEGEND_SIZE)
    frame = legend.get_frame()
    if frame is not None:
        frame.set_linewidth(1.0)


def style_figure(fig):
    apply_publication_style()
    for ax in fig.axes:
        style_axis(ax)
    if fig._suptitle is not None:
        fig._suptitle.set_fontsize(TITLE_SIZE)
        fig._suptitle.set_fontweight("bold")


def save_figure(fig, path):
    """Save a PNG copy of a Matplotlib figure."""
    style_figure(fig)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stem = path.with_suffix("")
    outputs = [stem.with_suffix(".png")]
    for output in outputs:
        fig.savefig(output, bbox_inches="tight")
    plt.close(fig)
    return outputs
