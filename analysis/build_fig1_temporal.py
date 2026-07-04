#!/usr/bin/env python3
"""
PAPER ANALYSIS SCRIPT: build_fig1_temporal.py
Description: Figure 1: stacked area temporal distribution by source (Feb 2022-Jun 2025).
Output: figures/fig1.png, figures/fig1.pdf
"""

import csv
import sys
from pathlib import Path

# Base directory: script location → repo root
BASE_DIR = Path(__file__).resolve().parent.parent
from collections import defaultdict, Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Paths
CORPUS = BASE_DIR / "data" / "paper_analysis_corpus.csv"
OUTPUT = BASE_DIR / "output"

# Colors (colorblind-safe palette)
COLORS = {
    'cissm': '#4477AA',  # blue
    'csis': '#CCBB44',   # yellow
    'cfr': '#AA3377',    # purple
}
SOURCE_LABELS = {
    'cissm': 'CISSM',
    'csis': 'CSIS',
    'cfr': 'CFR',
}


def load_data():
    """Load corpus and aggregate monthly counts by source."""
    monthly_counts = defaultdict(lambda: defaultdict(float))
    all_months = set()
    date_errors = 0

    with open(CORPUS, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('include_in_analysis', '').strip() != 'True':
                continue

            date_str = row.get('date', '').strip()
            src = row.get('source', '').strip()
            w = float(row.get('analysis_weight', 1) or 1)

            # Parse month from date
            try:
                if len(date_str) == 4 and date_str.isdigit():
                    # Year-only: use January
                    dt = datetime(int(date_str), 1, 1)
                elif len(date_str) == 7:
                    # YYYY-MM
                    dt = datetime.strptime(date_str, '%Y-%m')
                elif len(date_str) >= 10:
                    # Full date
                    dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
                else:
                    date_errors += 1
                    continue

                month_key = dt.strftime('%Y-%m')
                monthly_counts[src][month_key] += w
                all_months.add(month_key)
            except (ValueError, IndexError):
                date_errors += 1
                continue

    if date_errors:
        print(f"  Warning: {date_errors} rows with unparseable dates skipped")

    sorted_all = sorted(all_months)

    # Filter to paper scope: Feb 2022 onward
    scope_start = '2022-02'
    filtered_months = [m for m in sorted_all if m >= scope_start]

    omitted = len(sorted_all) - len(filtered_months)
    if omitted:
        print(f"  Note: omitted {omitted} pre-scope month(s) (before {scope_start})")

    if len(filtered_months) == 0:
        print("  ERROR: no months after 2022-02")
        return monthly_counts, []

    return monthly_counts, filtered_months


def make_figure(monthly_counts, sorted_months):
    """Create the stacked area chart."""
    sources = ['cissm', 'csis', 'cfr']
    month_dates = [datetime.strptime(m, '%Y-%m') for m in sorted_months]

    # Build stacked data
    data = {src: [] for src in sources}
    for m in sorted_months:
        for src in sources:
            data[src].append(monthly_counts[src].get(m, 0.0))

    fig, ax = plt.subplots(figsize=(10, 4.5))

    # Stacked area
    ax.stackplot(month_dates, [data[s] for s in sources],
                 labels=[SOURCE_LABELS[s] for s in sources],
                 colors=[COLORS[s] for s in sources],
                 alpha=0.85)

    # Formatting
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Monthly incident count (weighted)', fontsize=11)
    ax.set_title('Temporal Distribution of Cyber Operations by Database',
                 fontsize=13, fontweight='bold')

    # Date axis
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate(rotation=45, ha='right')

    # Y-axis: integer ticks
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # Legend
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)

    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Trim whitespace
    ax.set_xlim(month_dates[0], month_dates[-1])
    fig.tight_layout()

    # Output
    figures_dir = OUTPUT / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    for fmt, dpi in [('png', 300), ('pdf', 300)]:
        path = figures_dir / f"fig1.{fmt}"
        fig.savefig(path, dpi=dpi, bbox_inches='tight')
        print(f"  Wrote: {path}")

    plt.close(fig)

    # Stats summary
    print(f"  Date range: {sorted_months[0]} to {sorted_months[-1]} ({len(sorted_months)} months)")
    for src in sources:
        total = sum(data[src])
        print(f"  {SOURCE_LABELS[src]}: {total:.0f} weighted incidents across {len(sorted_months)} months")


def main():
    print("[build_fig1_temporal] Loading data...")
    monthly_counts, sorted_months = load_data()
    print(f"  Loaded {len(sorted_months)} months of data")

    if len(sorted_months) < 2:
        print("  ERROR: insufficient months for temporal plot")
        return 1

    make_figure(monthly_counts, sorted_months)
    return 0


if __name__ == "__main__":
    sys.exit(main())
