# /// script
# dependencies = [
#   "matplotlib",
#   "numpy",
# ]
# ///

import matplotlib.pyplot as plt
import numpy as np

plt.style.use("default")
plt.rcParams.update(
    {
        "figure.dpi": 100,
        # "font.family": "Menlo",
    }
)


# Sample data
categories = ["Parser", "Canonicalizer", "Printer"]
values1 = [0.003, 0.0005, 0.0002]  # First set of values
values2 = [0.166, 0.0688, 0.0334]  # Second set of values

# Error data (standard deviations or error margins)
error1 = [0, 0, 0]  # Error values for first series
error2 = [0.00246, 0.000552, 0.000634]  # Error values for second series

# Width of the bars
bar_width = 0.35

# Positions for the bars
r1 = np.arange(len(categories))
r2 = [x + bar_width for x in r1]

# Create the figure and axis objects
fig, ax = plt.subplots(figsize=(10, 6))

# Create the bars with error bars
bar1 = ax.bar(r1, values1, width=bar_width, label='MLIR', color='skyblue',
              edgecolor='black', yerr=error1, capsize=5, error_kw={'ecolor': 'black', 'linewidth': 1})
bar2 = ax.bar(r2, values2, width=bar_width, label='xDSL', color='lightgreen',
              edgecolor='black', yerr=error2, capsize=5, error_kw={'ecolor': 'black', 'linewidth': 1})

# Add labels, title, and custom x-axis tick labels
ax.set_xlabel('Pipeline phase', fontweight='bold')
ax.set_ylabel('Wall time [s]', fontweight='bold')
ax.set_title("Pipeline phase times for canonicalising 1000 constant folds", fontweight='bold')
ax.set_xticks([r + bar_width/2 for r in range(len(categories))])
ax.set_xticklabels(categories)

# Add value labels on top of bars
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

add_labels(bar1)
add_labels(bar2)

# Add a legend
ax.legend()

# Add grid lines for better readability (optional)
ax.grid(True, linestyle='--', alpha=0.7, axis='y')

# Ensure the layout is tight
plt.tight_layout()

# Show the plot
plt.show(block=False)




# Calculate speedup ratios (improved/baseline)
speedup_ratios = [v2/v1 for v1, v2 in zip(values1, values2)]

# Calculate propagated errors for the speedup ratios
# Using error propagation formula for division: δ(A/B) = (A/B) * sqrt((δA/A)^2 + (δB/B)^2)
# Since error1 is all zeros, we simplify to: δ(A/B) = (A/B) * (δA/A)
propagated_errors = [ratio * (error2[i]/values2[i]) if values2[i] > 0 else 0
                    for i, ratio in enumerate(speedup_ratios)]

# Create the figure and axis objects
fig, ax = plt.subplots(figsize=(10, 6))

# Create the bars with error bars
bars = ax.bar(categories, speedup_ratios, width=0.6, color='cornflowerblue',
              edgecolor='black', yerr=propagated_errors, capsize=5,
              error_kw={'ecolor': 'black', 'linewidth': 1})

# Add labels, title
ax.set_xlabel('Benchmarks', fontweight='bold')
ax.set_ylabel('Speedup Factor (×)', fontweight='bold')
ax.set_title('Performance Speedup by Benchmark', fontweight='bold')

# Format y-axis with times symbol
max_y = max(speedup_ratios) + max(propagated_errors) + 10
y_ticks = np.arange(0, max_y, 10)
ax.set_yticks(y_ticks)
ax.set_yticklabels([f'{y:.0f}×' for y in y_ticks])

# Add value labels on top of bars
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax.annotate(f'{height:.1f}×',
                xy=(bar.get_x() + bar.get_width() / 2, height + propagated_errors[i]),
                xytext=(0, 5),  # 5 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom',
                fontweight='bold')

# Adjust layout to make room for table
plt.subplots_adjust(bottom=0.35)

# Add grid lines for better readability
ax.grid(True, linestyle='--', alpha=0.7, axis='y')
ax.set_axisbelow(True)

# Show the plot
plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.show()
