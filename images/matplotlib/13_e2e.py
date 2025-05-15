#!/usr/bin/env python3
# /// script
# dependencies = [
#   "matplotlib",
#   "numpy",
# ]
# ///
"""Template plotting script.

Derived from <https://github.com/opencompl/paper-template/blob/main/plots/plot.py>.
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math

from pathlib import Path

PARENT_DIRECTORY = Path(__file__).parent

from typing import Callable


def setGlobalDefaults():
    ## Use TrueType fonts instead of Type 3 fonts
    #
    # Type 3 fonts embed bitmaps and are not allowed in camera-ready submissions
    # for many conferences. TrueType fonts look better and are accepted.
    # This follows: https://www.conference-publishing.com/Help.php
    matplotlib.rcParams["pdf.fonttype"] = 42
    matplotlib.rcParams["ps.fonttype"] = 42

    ## Enable tight_layout by default
    #
    # This ensures the plot has always sufficient space for legends, ...
    # Without this sometimes parts of the figure would be cut off.
    matplotlib.rcParams["figure.autolayout"] = True

    ## Legend defaults
    matplotlib.rcParams["legend.frameon"] = False

    ## Set high DPI for high resolution outputs
    matplotlib.rcParams["figure.dpi"] = 300

    # Hide the right and top spines
    #
    # This reduces the number of lines in the plot. Lines typically catch
    # a readers attention and distract the reader from the actual content.
    # By removing unnecessary spines, we help the reader to focus on
    # the figures in the graph.
    matplotlib.rcParams["axes.spines.right"] = False
    matplotlib.rcParams["axes.spines.top"] = False


matplotlib.rcParams["figure.figsize"] = 5, 2.5

# Color palette
light_gray = "#cacaca"
dark_gray = "#827b7b"
light_blue = "#a6cee3"
dark_blue = "#1f78b4"
light_green = "#b2df8a"
dark_green = "#33a02c"
light_red = "#fb9a99"
dark_red = "#e31a1c"
black = "#000000"
white = "#ffffff"


def save(figure: Path, name: str):
    # Do not emit a creation date, creator name, or producer. This will make the
    # content of the pdfs we generate more deterministic.
    metadata = {"CreationDate": None, "Creator": None, "Producer": None}

    figure.savefig(name, metadata=metadata)

    # Close figure to avoid warning about too many open figures.
    plt.close(figure)

    print(f"written to {name}")


# helper for str_from_float.
# format float in scientific with at most *digits* digits.
#
# precision of the mantissa will be reduced as necessary,
# as much as possible to get it within *digits*, but this
# can't be guaranteed for very large numbers.
def get_scientific(x: float, digits: int):
    # get scientific without leading zeros or + in exp
    def get(x: float, prec: int) -> str:
        result = f"{x:.{prec}e}"
        result = result.replace("e+", "e")
        while "e0" in result:
            result = result.replace("e0", "e")
        while "e-0" in result:
            result = result.replace("e-0", "e-")
        return result

    result = get(x, digits)
    len_after_e = len(result.split("e")[1])
    prec = max(0, digits - len_after_e - 2)
    return get(x, prec)


# format float with at most *digits* digits.
# if the number is too small or too big,
# it will be formatted in scientific notation,
# optionally a suffix can be passed for the unit.
#
# note: this displays different numbers with different
# precision depending on their length, as much as can fit.
def str_from_float(x: float, digits: int = 3, suffix: str = "") -> str:
    result = f"{x:.{digits}f}"
    before_decimal = result.split(".")[0]
    if len(before_decimal) == digits:
        return before_decimal
    if len(before_decimal) > digits:
        # we can't even fit the integral part
        return get_scientific(x, digits)

    result = result[: digits + 1]  # plus 1 for the decimal point
    if float(result) == 0:
        # we can't even get one significant figure
        return get_scientific(x, digits)

    return result[: digits + 1]


# Attach a text label above each bar in *rects*, displaying its height
def autolabel(
    ax,
    rects,
    label_from_height: Callable[[float], str] = str_from_float,
    xoffset=0,
    yoffset=1,
    **kwargs,
):
    # kwargs is directly passed to ax.annotate and overrides defaults below
    assert "xytext" not in kwargs, "use xoffset and yoffset instead of xytext"
    default_kwargs = dict(
        xytext=(xoffset, yoffset),
        fontsize="smaller",
        rotation=0,
        ha="center",
        va="bottom",
        textcoords="offset points",
    )

    for rect in rects:
        height = rect.get_height()
        ax.annotate(
            label_from_height(height),
            xy=(rect.get_x() + rect.get_width() / 2, height),
            **(default_kwargs | kwargs),
        )


# utility to print times as 1h4m, 1d15h, 143.2ms, 10.3s etc.
def str_from_ms(ms: float | int):
    def maybe_val_with_unit(val: float | int, unit: str):
        return f"{val}{unit}" if val != 0 else ""

    if ms < 1000:
        return f"{ms:.3g}ms"

    s = ms / 1000
    ms = 0
    if s < 60:
        return f"{s:.3g}s"

    m = int(s // 60)
    s -= 60 * m
    if m < 60:
        return f"{m}m{maybe_val_with_unit(math.floor(s), 's')}"

    h = int(m // 60)
    m -= 60 * h
    if h < 24:
        return f"{h}h{maybe_val_with_unit(m, 'm')}"

    d = int(h // 24)
    h -= 24 * d
    return f"{d}d{maybe_val_with_unit(h, 'h')}"


def autolabel_ms(ax, rects, **kwargs):
    autolabel(ax, rects, label_from_height=str_from_ms, **kwargs)


def plot_walltimes():
    labels = ["Parser", "Canonicalizer", "Printer"]
    mlir_means = [0.003, 0.0005, 0.0002]
    _mlir_errors = [0, 0, 0]
    xdsl_means = [0.166, 0.0688, 0.0334]
    xdsl_errors = [0.00246, 0.000552, 0.000634]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(
        x - width / 2,
        mlir_means,
        width,
        label="MLIR",
        color=light_blue,
    )
    rects2 = ax.bar(
        x + width / 2,
        xdsl_means,
        width,
        label="xDSL",
        color=dark_blue,
        yerr=xdsl_errors,
        capsize=5,
        error_kw={"ecolor": "black", "linewidth": 1},
    )

    # Logarithmic Y-Axis
    ax.set_yscale("log")

    # Y-Axis Label
    #
    # Use a horizontal label for improved readability.
    ax.set_ylabel(
        "Wall time [s]",
        rotation="horizontal",
        position=(1, 1.05),
        horizontalalignment="left",
        verticalalignment="bottom",
    )

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.legend(ncol=100, loc="lower right", bbox_to_anchor=(0, 1, 1, 0))

    autolabel(ax, rects1)
    autolabel(ax, rects2)

    save(fig, PARENT_DIRECTORY / "../13_measuring_compiler_performance/walltimes.pdf")


def plot_speedup():
    labels = ["Parser", "Canonicalizer", "Printer"]
    mlir_means = [0.003, 0.0005, 0.0002]
    mlir_errors = [0, 0, 0]
    xdsl_means = [0.166, 0.0688, 0.0334]
    xdsl_errors = [0.00246, 0.000552, 0.000634]

    # Calculate speedup ratios (improved/baseline)
    speedup_ratios = [v2 / v1 for v1, v2 in zip(mlir_means, xdsl_means)]

    # Calculate propagated errors for the speedup ratios
    # Using error propagation formula for division: δ(A/B) = (A/B) * sqrt((δA/A)^2 + (δB/B)^2)
    # Since error1 is all zeros, we simplify to: δ(A/B) = (A/B) * (δA/A)
    propagated_errors = [
        ratio * (xdsl_errors[i] / xdsl_means[i]) if xdsl_means[i] > 0 else 0
        for i, ratio in enumerate(speedup_ratios)
    ]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(
        x,
        speedup_ratios,
        width,
        color=light_blue,
        yerr=propagated_errors,
        capsize=5,
        error_kw={"ecolor": "black", "linewidth": 1},
    )

    # Y-Axis Label
    #
    # Use a horizontal label for improved readability.
    ax.set_ylabel(
        "xDSL slowdown",
        rotation="horizontal",
        position=(1, 1.05),
        horizontalalignment="left",
        verticalalignment="bottom",
    )

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.legend(ncol=100, loc="lower right", bbox_to_anchor=(0, 1, 1, 0))

    autolabel(ax, rects1)

    save(fig, PARENT_DIRECTORY / "../13_measuring_compiler_performance/speedup.pdf")


def main():
    setGlobalDefaults()

    plot_walltimes()
    plot_speedup()


if __name__ == "__main__":
    main()
