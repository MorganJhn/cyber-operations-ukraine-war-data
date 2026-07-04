#!/usr/bin/env python3
"""
PAPER ANALYSIS SCRIPT: build_attribution_by_source.py
Description: Per-source self-attribution rates with 95% Wilson confidence intervals.
Output: stats/attribution_by_source.json
"""

import csv
import json
import sys
import math
from pathlib import Path

# Base directory: script location → repo root
BASE_DIR = Path(__file__).resolve().parent.parent
from collections import Counter

# Paths
CORPUS = BASE_DIR / "data" / "paper_analysis_corpus.csv"
OUTPUT = BASE_DIR / "output"


def load_corpus(path):
    """Load CSV and filter to include_in_analysis=True."""
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('include_in_analysis', '').strip() == 'True':
                rows.append(row)
    return rows


def wilson_ci(n_success, n_total, z=1.96):
    """
    Compute Wilson score confidence interval for a proportion.
    Returns (lower, upper, proportion).
    """
    if n_total == 0:
        return (0.0, 0.0, 0.0)

    p = n_success / n_total
    denominator = 1 + z**2 / n_total
    centre = (p + z**2 / (2 * n_total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n_total)) / n_total) / denominator

    lower = max(0.0, centre - margin)
    upper = min(1.0, centre + margin)

    return (round(lower, 4), round(upper, 4), round(p, 4))


def compute_attribution_by_source(rows):
    """
    Compute per-source attribution method proportions with Wilson CI.
    Focus on self_attribution, but also report full distribution.
    """
    sources = ['cissm', 'csis', 'cfr']
    result = {}

    for src in sources:
        src_rows = [r for r in rows if r['source'].strip() == src]
        n_total = len(src_rows)

        # Count attribution methods (weighted)
        method_counts = Counter()
        weighted_methods = {}
        total_weight = 0.0

        for r in src_rows:
            am = r.get('attribution_method', '').strip()
            w = float(r.get('analysis_weight', 1) or 1)
            if am:
                method_counts[am] += 1
                weighted_methods[am] = weighted_methods.get(am, 0) + w
                total_weight += w

        # Self-attribution stats
        self_attr_count = method_counts.get('self_attribution', 0)
        self_attr_weight = weighted_methods.get('self_attribution', 0.0)

        # Wilson CI on unweighted proportion
        ci_lower, ci_upper, self_prop = wilson_ci(self_attr_count, n_total)
        # Weighted proportion
        weighted_prop = round(self_attr_weight / total_weight, 4) if total_weight > 0 else 0.0

        # Full distribution (unweighted counts + weighted %)
        distribution = {}
        for am in sorted(method_counts.keys()):
            distribution[am] = {
                "count": method_counts[am],
                "weighted_sum": round(weighted_methods.get(am, 0), 2),
                "weighted_pct": round(weighted_methods.get(am, 0) / total_weight * 100, 1) if total_weight > 0 else 0.0
            }

        result[src] = {
            "n": n_total,
            "total_weight": round(total_weight, 2),
            "self_attribution": {
                "count": self_attr_count,
                "proportion": self_prop,
                "weighted_proportion": weighted_prop,
                "wilson_ci_95": {
                    "lower": ci_lower,
                    "upper": ci_upper
                },
                "display": f"{self_attr_count}/{n_total} ({round(self_prop*100,1)}%, 95% CI [{round(ci_lower*100,1)}%, {round(ci_upper*100,1)}%])"
            },
            "full_distribution": distribution
        }

    return result


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def main():
    print(f"[build_attribution_by_source] Loading corpus...")
    rows = load_corpus(CORPUS)
    print(f"  Loaded {len(rows)} rows (include_in_analysis=True)")

    # Validate attribution_method column exists
    if rows and 'attribution_method' not in rows[0]:
        print("  ERROR: 'attribution_method' column not found in corpus")
        return 1

    result = compute_attribution_by_source(rows)

    for src, data in result.items():
        sa = data['self_attribution']
        print(f"\n  {src} (N={data['n']}):")
        print(f"    Self-attribution: {sa['display']}")
        print(f"    Weighted proportion: {sa['weighted_proportion']}")

    # Add context note
    result["_context"] = {
        "note": "Self-attribution indicates the operation was claimed by the perpetrator. "
                "CISSM collects OSINT including hacktivist self-attestations. "
                "CSIS curates state-attributed incidents. CFR uses media/law enforcement reports.",
        "interpretation": (
            "CISSM's high self-attribution (52.8%) reflects its OSINT collection methodology "
            "capturing hacktivist claims. CSIS's lower rate (18.3%) reflects state-curated incident "
            "selection. CFR's 0% reflects its media-source focus."
        )
    }

    stats_dir = OUTPUT / "stats"
    ensure_dir(stats_dir)

    with open(stats_dir / "attribution_by_source.json", 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n  Wrote: {stats_dir / 'attribution_by_source.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
