#!/usr/bin/env python3
"""
PAPER ANALYSIS SCRIPT: build_fig2_actor_types.py
Description: Figure 2: stacked bar actor type by source with count labels.
Output: figures/fig2.png, figures/fig2.pdf
"""

import csv
import sys
from pathlib import Path

# Base directory: script location → repo root
BASE_DIR = Path(__file__).resolve().parent.parent
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Paths
CORPUS = BASE_DIR / "data" / "corpus_with_actor_type.csv"
OUTPUT = BASE_DIR / "output"

# Colors (colorblind-safe, 6 categories)
ACTOR_COLORS = {
    'state_russian': '#4477AA',
    'state_ukrainian': '#66CCEE',
    'hacktivist_prorussian': '#CCBB44',
    'hacktivist_proukrainian': '#EE6677',
    'hacktivist_other': '#AA3377',
    'unknown': '#BBBBBB',
}
ACTOR_LABELS = {
    'state_russian': 'State: Russia',
    'state_ukrainian': 'State: Ukraine',
    'hacktivist_prorussian': 'Hacktivist: Pro-Russian',
    'hacktivist_proukrainian': 'Hacktivist: Pro-Ukrainian',
    'hacktivist_other': 'Hacktivist: Other',
    'unknown': 'Unknown',
}
ACTOR_ORDER = [
    'state_russian', 'state_ukrainian',
    'hacktivist_prorussian', 'hacktivist_proukrainian', 'hacktivist_other',
    'unknown'
]
SOURCE_LABELS = {'cissm': 'CISSM', 'csis': 'CSIS', 'cfr': 'CFR'}


def load_data():
    """Load corpus and aggregate actor types by source (unweighted counts)."""
    src_actors = {}
    for src in ['cissm', 'csis', 'cfr']:
        src_actors[src] = Counter()

    with open(CORPUS, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('include_in_analysis', '').strip() != 'True':
                continue
            src = row.get('source', '').strip()
            at = row.get('actor_type', '').strip()
            if src in src_actors and at:
                src_actors[src][at] += 1

    return src_actors


def make_figure(src_actors):
    """Create grouped stacked bar chart."""
    sources = ['cissm', 'csis', 'cfr']
    x = np.arange(len(sources))
    width = 0.55

    fig, ax = plt.subplots(figsize=(8, 5))

    # Build stacked bars
    bottoms = np.zeros(len(sources))
    bars = []
    for at in ACTOR_ORDER:
        values = [src_actors[s].get(at, 0) for s in sources]
        bar = ax.bar(x, values, width, bottom=bottoms,
                     label=ACTOR_LABELS[at], color=ACTOR_COLORS[at],
                     edgecolor='white', linewidth=0.5)
        bars.append(bar)
        bottoms += values

    # Add count labels on each stack segment
    bottoms2 = np.zeros(len(sources))
    for at in ACTOR_ORDER:
        values = [src_actors[s].get(at, 0) for s in sources]
        for i, (v, b) in enumerate(zip(values, bottoms2)):
            if v > 0:
                ax.text(x[i], b + v/2, str(int(v)),
                        ha='center', va='center', fontsize=8,
                        fontweight='bold', color='white')
        bottoms2 += values

    # X-axis labels
    ax.set_xticks(x)
    ax.set_xticklabels([SOURCE_LABELS[s] for s in sources], fontsize=12)
    ax.set_xlabel('Database', fontsize=12)

    # Y-axis
    ax.set_ylabel('Number of incidents (unweighted)', fontsize=12)
    ax.set_title('Actor Type Composition by Database', fontsize=13, fontweight='bold')

    # Legend
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Y-axis integer ticks
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # Add total labels above bars
    for i, src in enumerate(sources):
        total = sum(src_actors[src].values())
        ax.text(x[i], bottoms[i] + 5, f'N={total}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    fig.tight_layout()

    # Output
    figures_dir = OUTPUT / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    for fmt, dpi in [('png', 300), ('pdf', 300)]:
        path = figures_dir / f"fig2.{fmt}"
        fig.savefig(path, dpi=dpi, bbox_inches='tight')
        print(f"  Wrote: {path}")

    plt.close(fig)

    # Summary
    for src in sources:
        total = sum(src_actors[src].values())
        print(f"  {SOURCE_LABELS[src]} (N={total}):")
        for at in ACTOR_ORDER:
            c = src_actors[src].get(at, 0)
            if c:
                pct = c / total * 100
                print(f"    {ACTOR_LABELS[at]}: {c} ({pct:.1f}%)")


def main():
    print("[build_fig2_actor_types] Loading data...")
    src_actors = load_data()

    for src in ['cissm', 'csis', 'cfr']:
        total = sum(src_actors[src].values())
        print(f"  {SOURCE_LABELS[src]}: {total} records")

    make_figure(src_actors)
    return 0


if __name__ == "__main__":
    sys.exit(main())
