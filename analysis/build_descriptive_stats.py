#!/usr/bin/env python3
"""
PAPER ANALYSIS SCRIPT: build_descriptive_stats.py
Description: Descriptive statistics (post-normalization); temporal state vs hacktivist monthly patterns.
Output:
  - stats/descriptive.json    — row counts, source shares, actor types, countries, dates
  - stats/temporal_patterns.json — monthly state vs hacktivist weighted counts by source
"""

import csv
import json
import sys
from pathlib import Path

# Base directory: script location → repo root
BASE_DIR = Path(__file__).resolve().parent.parent
from collections import Counter, defaultdict

# Paths
CORPUS = BASE_DIR / "data" / "paper_analysis_corpus.csv"
ACTOR_CORPUS = BASE_DIR / "data" / "corpus_with_actor_type.csv"
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


def month_key(date_str):
    """Extract YYYY-MM from a date string. Handles year-only (YYYY) as YYYY-01."""
    if not date_str or date_str.strip() == '':
        return None
    d = date_str.strip()
    if len(d) == 4 and d.isdigit():
        return d + '-01'
    if len(d) >= 7:
        return d[:7]
    return None


def compute_descriptive(rows):
    """Compute summary descriptive statistics for the corpus."""
    total = len(rows)

    # Source breakdown
    source_counts = Counter(r['source'].strip() for r in rows)

    # Actor types
    actor_types = Counter(r.get('actor_type', '').strip() for r in rows if r.get('actor_type', '').strip())

    # Event types
    event_types = Counter(r.get('event_type', '').strip() for r in rows if r.get('event_type', '').strip())

    # Countries
    countries = Counter(r.get('actor_country', '').strip() for r in rows if r.get('actor_country', '').strip())

    # Date range
    dates = [r['date'].strip() for r in rows if r['date'].strip()]
    date_min = min(dates) if dates else None
    date_max = max(dates) if dates else None

    # Months per source
    months = defaultdict(set)
    for r in rows:
        mk = month_key(r.get('date', ''))
        if mk:
            months[r['source'].strip()].add(mk)

    # Attribution method breakdown
    attr_methods = Counter(r.get('attribution_method', '').strip() for r in rows if r.get('attribution_method', '').strip())

    return {
        "total_records": total,
        "sources": {
            src: {
                "count": cnt,
                "percent": round(cnt / total * 100, 1),
                "months_covered": sorted(months.get(src, set()))
            }
            for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1])
        },
        "actor_types": {
            at: cnt for at, cnt in sorted(actor_types.items(), key=lambda x: -x[1])
        },
        "event_types": {
            et: cnt for et, cnt in sorted(event_types.items(), key=lambda x: -x[1])
        },
        "actor_countries": {
            c: cnt for c, cnt in sorted(countries.items(), key=lambda x: -x[1])
        },
        "attribution_methods": {
            am: cnt for am, cnt in sorted(attr_methods.items(), key=lambda x: -x[1])
        },
        "date_range": {
            "min": date_min,
            "max": date_max,
            "total_months": len(set(month_key(r.get('date','')) for r in rows if month_key(r.get('date',''))))
        },
        "note": "All counts unweighted. Weighted analyses use the analysis_weight column."
    }


def compute_temporal_patterns(rows):
    """
    Monthly state vs hacktivist weighted counts by source.
    Aggregated by YYYY-MM across all sources plus per-source.
    """
    # Aggregate monthly actor-type patterns
    # Using actor_type from the rows (should be present in paper_analysis_corpus.csv)
    monthly = defaultdict(lambda: {
        'state_russian': 0.0, 'state_ukrainian': 0.0,
        'hacktivist_prorussian': 0.0, 'hacktivist_proukrainian': 0.0,
        'hacktivist_other': 0.0, 'unknown': 0.0, 'total': 0.0
    })

    # Per-source monthly
    monthly_by_source = defaultdict(lambda: defaultdict(lambda: {
        'state': 0.0, 'hacktivist': 0.0, 'unknown': 0.0, 'total': 0.0
    }))

    for r in rows:
        mk = month_key(r.get('date', ''))
        if not mk:
            continue
        at = r.get('actor_type', '').strip()
        src = r['source'].strip()
        w = float(r.get('analysis_weight', 1) or 1)

        monthly[mk][at] += w
        monthly[mk]['total'] += w

        # Simplified categories for per-source
        if at.startswith('state_'):
            monthly_by_source[src][mk]['state'] += w
        elif at.startswith('hacktivist_'):
            monthly_by_source[src][mk]['hacktivist'] += w
        else:
            monthly_by_source[src][mk]['unknown'] += w
        monthly_by_source[src][mk]['total'] += w

    # Sort months
    sorted_months = sorted(monthly.keys())

    # Aggregate across all sources
    overall = {
        mk: monthly[mk] for mk in sorted_months
    }

    # Per-source
    per_source = {}
    for src in sorted(monthly_by_source.keys()):
        src_months = sorted(monthly_by_source[src].keys())
        per_source[src] = {
            mk: monthly_by_source[src][mk] for mk in src_months
        }

    return {
        "overall": {
            "months": sorted_months,
            "start": sorted_months[0] if sorted_months else None,
            "end": sorted_months[-1] if sorted_months else None,
            "total_months": len(sorted_months),
            "data": overall
        },
        "by_source": per_source,
        "note": "Values are weighted (analysis_weight). CISSM cluster weights applied."
    }


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def main():
    print(f"[build_descriptive_stats] Loading corpus...")
    rows = load_corpus(CORPUS)
    print(f"  Loaded {len(rows)} rows (include_in_analysis=True)")

    # 2.5 Descriptive statistics
    print(f"\n[2.5] Descriptive statistics...")
    desc = compute_descriptive(rows)
    for src, info in desc['sources'].items():
        print(f"  {src}: N={info['count']} ({info['percent']}%), months={len(info['months_covered'])}")
    print(f"  Actor types: {len(desc['actor_types'])}")
    print(f"  Event types: {len(desc['event_types'])}")
    print(f"  Countries: {len(desc['actor_countries'])}")

    # 2.6 Temporal patterns
    print(f"\n[2.6] Temporal: state vs hacktivist monthly...")
    temp = compute_temporal_patterns(rows)  # rows already has date + actor_type
    print(f"  Months: {temp['overall']['start']} to {temp['overall']['end']} ({temp['overall']['total_months']} months)")
    for src in temp['by_source']:
        print(f"  {src}: {len(temp['by_source'][src])} months with data")

    # Write outputs
    stats_dir = OUTPUT / "stats"
    ensure_dir(stats_dir)

    with open(stats_dir / "descriptive.json", 'w') as f:
        json.dump(desc, f, indent=2)
    print(f"\n  Wrote: {stats_dir / 'descriptive.json'}")

    with open(stats_dir / "temporal_patterns.json", 'w') as f:
        json.dump(temp, f, indent=2)
    print(f"  Wrote: {stats_dir / 'temporal_patterns.json'}")

    print(f"\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
