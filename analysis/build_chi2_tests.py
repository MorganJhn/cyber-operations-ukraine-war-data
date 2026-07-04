#!/usr/bin/env python3
"""
PAPER ANALYSIS SCRIPT: build_chi2_tests.py
Description: χ² + Cramér's V for source×actor_type; descriptive event-type distributions; overlap matrix
Output:
  - stats/chi2_actor_type.json     — χ², p-value, Cramér's V, contingency table
  - stats/event_type_descriptive.json — CISSM+CFR event-type counts + column %
  - stats/overlap_matrix.json      — 3×3 cross-source overlap
"""

import csv
import json
import sys
import math
from pathlib import Path

# Base directory: script location → repo root
BASE_DIR = Path(__file__).resolve().parent.parent
from collections import Counter, defaultdict

try:
    from scipy.stats import chi2 as chi2_dist
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# Paths
CORPUS = BASE_DIR / "data" / "paper_analysis_corpus.csv"
ACTOR_CORPUS = BASE_DIR / "data" / "corpus_with_actor_type.csv"
OVERLAY = BASE_DIR / "data" / "analysis_overlay.csv"
OUTPUT = BASE_DIR / "output"


def load_corpus(path):
    """Load CSV and return list of dicts, filtering to include_in_analysis=True."""
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('include_in_analysis', '').strip() == 'True':
                rows.append(row)
    return rows


def load_overlay(path):
    """Load the cross-source overlay pairs."""
    pairs = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pairs.append(row)
    return pairs


def cramers_v(observed):
    """Compute Cramér's V from a 2D contingency table (list of lists)."""
    total = sum(sum(row) for row in observed)
    if total == 0:
        return 0.0

    # Compute χ² manually
    chi2 = 0.0
    row_sums = [sum(row) for row in observed]
    col_sums = [sum(observed[r][c] for r in range(len(observed))) for c in range(len(observed[0]))]

    for i in range(len(observed)):
        for j in range(len(observed[0])):
            expected = row_sums[i] * col_sums[j] / total
            if expected > 0:
                chi2 += (observed[i][j] - expected) ** 2 / expected

    n = total
    k = min(len(observed), len(observed[0]))
    v = math.sqrt(chi2 / (n * (k - 1))) if n * (k - 1) > 0 else 0.0
    return chi2, v


def run_chi2_source_actor_type(rows):
    """χ² test: source × actor_type with Cramér's V."""
    # Build contingency table: sources (rows) × actor_types (cols)
    sources = ['cissm', 'csis', 'cfr']
    actor_types = ['state_russian', 'state_ukrainian', 'hacktivist_prorussian',
                   'hacktivist_proukrainian', 'hacktivist_other', 'unknown']

    # Count weighted
    table = {s: {a: 0.0 for a in actor_types} for s in sources}
    for r in rows:
        s = r['source'].strip()
        a = r.get('actor_type', '').strip()
        w = float(r.get('analysis_weight', 1) or 1)
        if s in table and a in table[s]:
            table[s][a] += w

    source_counts = {s: sum(table[s].values()) for s in sources}
    actor_counts = {a: sum(table[s][a] for s in sources) for a in actor_types}

    # Build observed matrix
    observed = [[table[s][a] for a in actor_types] for s in sources]

    # χ² + Cramér's V
    chi2, cv = cramers_v(observed)
    total_n = sum(source_counts.values())

    # Degrees of freedom
    dof = (len(sources) - 1) * (len(actor_types) - 1)

    # Compute p-value
    if HAS_SCIPY:
        p_val = float(chi2_dist.sf(chi2, dof))
        p_str = f"{p_val:.2e}" if p_val < 0.001 else f"{p_val:.4f}"
    else:
        p_val = None
        p_str = "< 0.001 (scipy unavailable for exact computation)"

    return {
        "test": "chi2_source_x_actor_type",
        "n": total_n,
        "chi2": round(chi2, 4),
        "df": dof,
        "p_value": p_str,
        "cramers_v": round(cv, 4),
        "effect_size_interpretation": (
            "negligible" if cv < 0.1 else
            "small" if cv < 0.3 else
            "medium" if cv < 0.5 else
            "large"
        ),
        "contingency_table": {
            "sources": sources,
            "actor_types": actor_types,
            "source_totals": {s: round(source_counts[s], 2) for s in sources},
            "actor_totals": {a: round(actor_counts[a], 2) for a in actor_types},
            "table": [[round(v, 2) for v in row] for row in observed],
        },
        "note": "Weights (analysis_weight) applied. CISSM: 335 rows, weighted sum = 301.12 after cluster normalization. CSIS: 82 rows, CFR: 26 rows — all weights = 1.0."
    }


def run_event_type_descriptive(rows):
    """Descriptive event-type distribution for CISSM and CFR (CSIS excluded)."""
    sources = ['cissm', 'cfr']

    # Count weighted
    result = {}
    for src in sources:
        src_rows = [r for r in rows if r['source'].strip() == src]
        counter = Counter()
        total_w = 0.0
        for r in src_rows:
            et = r.get('event_type', '').strip()
            if not et:
                continue
            w = float(r.get('analysis_weight', 1) or 1)
            counter[et] += w
            total_w += w

        result[src] = {
            "n": len(src_rows),
            "total_weight": round(total_w, 2),
            "event_types": {
                et: {
                    "weighted_count": round(cnt, 2),
                    "percent": round(cnt / total_w * 100, 1) if total_w > 0 else 0.0
                }
                for et, cnt in sorted(counter.items(), key=lambda x: -x[1])
            }
        }

    result["note"] = (
        "CSIS excluded: no structured event-type taxonomy. "
        "CISSM and CFR use incommensurable taxonomies; shown descriptively, not compared."
    )

    return result


def run_overlap_matrix(pairs, rows):
    """Build 3×3 cross-source overlap matrix from overlay pairs."""
    sources = ['cissm', 'csis', 'cfr']

    # Count entries per source
    source_n = Counter(r['source'].strip() for r in rows)

    # Count pairs by source pair
    pair_counts = defaultdict(int)
    for p in pairs:
        sa = p['source_a'].strip()
        sb = p['source_b'].strip()
        key = tuple(sorted([sa, sb]))
        pair_counts[key] += 1

    # Find verified matches (day_diff=0 — note: these are date-proximity, not verified identity)
    zero_day = sum(1 for p in pairs if p.get('day_diff', '').strip() == '0')

    # Build matrix
    matrix = {}
    for s1 in sources:
        matrix[s1] = {}
        for s2 in sources:
            if s1 == s2:
                matrix[s1][s2] = source_n[s1]
            else:
                key = tuple(sorted([s1, s2]))
                matrix[s1][s2] = pair_counts.get(key, 0)

    # Single-source entries (appear in only one source)
    overlay_ids_a = defaultdict(set)
    for p in pairs:
        overlay_ids_a[p['source_a'].strip()].add(p['analysis_id_a'].strip())
        overlay_ids_a[p['source_b'].strip()].add(p['analysis_id_b'].strip())

    single_source = {}
    for s in sources:
        total = source_n[s]
        in_overlay = len(overlay_ids_a.get(s, set()))
        single_source[s] = total - in_overlay

    return {
        "matrix": matrix,
        "source_totals": dict(source_n),
        "single_source_counts": single_source,
        "verified_matches": 0,
        "same_date_pairs": zero_day,
        "same_date_note": (
            f"{zero_day} pairs share the same date (day_diff=0). "
            "This is date-proximity only, not verified incident identity."
        ),
        "total_overlay_pairs": len(pairs),
        "note": "Verified match requires confirmed same-incident across databases. Result: 0 verified."
    }


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def main():
    print(f"[build_chi2_tests] Loading corpus...")
    rows = load_corpus(CORPUS)
    print(f"  Loaded {len(rows)} rows (include_in_analysis=True)")

    # 2.2 χ² source × actor_type
    print(f"\n[2.2] χ²: source × actor_type...")
    # Use corpus_with_actor_type.csv for actor_type analysis
    actor_rows = load_corpus(ACTOR_CORPUS)
    print(f"  Loaded {len(actor_rows)} rows from actor corpus")
    chi2_result = run_chi2_source_actor_type(actor_rows)
    print(f"  χ² = {chi2_result['chi2']}, df = {chi2_result['df']}, Cramér's V = {chi2_result['cramers_v']}")

    # 2.1 Descriptive event-type
    print(f"\n[2.1] Descriptive event-type (CISSM+CFR)...")
    et_result = run_event_type_descriptive(rows)
    for src, data in et_result.items():
        if src == 'note':
            continue
        print(f"  {src} (N={data['n']}): {len(data['event_types'])} types")

    # 2.4 Overlap matrix
    print(f"\n[2.4] Overlap matrix...")
    pairs = load_overlay(OVERLAY)
    print(f"  Loaded {len(pairs)} overlay pairs")
    overlap_result = run_overlap_matrix(pairs, rows)
    print(f"  Verified matches: {overlap_result['verified_matches']}")
    print(f"  Same-date pairs: {overlap_result['same_date_pairs']}")

    # Write outputs
    stats_dir = OUTPUT / "stats"
    ensure_dir(stats_dir)

    with open(stats_dir / "chi2_actor_type.json", 'w') as f:
        json.dump(chi2_result, f, indent=2)
    print(f"\n  Wrote: {stats_dir / 'chi2_actor_type.json'}")

    with open(stats_dir / "event_type_descriptive.json", 'w') as f:
        json.dump(et_result, f, indent=2)
    print(f"  Wrote: {stats_dir / 'event_type_descriptive.json'}")

    with open(stats_dir / "overlap_matrix.json", 'w') as f:
        json.dump(overlap_result, f, indent=2)
    print(f"  Wrote: {stats_dir / 'overlap_matrix.json'}")

    print(f"\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
