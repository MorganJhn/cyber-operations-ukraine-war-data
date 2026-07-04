#!/usr/bin/env python3
"""
PAPER ANALYSIS SCRIPT: build_table3_event_types.py
Description: Table 3: side-by-side event type distributions (CISSM+CFR only).
Output: tables/table3.tex
"""

import json
import sys
from pathlib import Path

# Base directory: script location → repo root
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
STATS = BASE_DIR / "output" / "stats"
OUTPUT = BASE_DIR / "output"

TABLE3_TEMPLATE = r"""%% Auto-generated Table 3
%% Source: event_type_descriptive.json (corpus filtered to include_in_analysis=True)
\begin{table}[ht]
\centering
\caption{Event Type Distribution by Database}
\label{tab:event-types}
\begin{tabular}{lcc}
\toprule
Event Type & CISSM (N=335) & CFR (N=26) \\
\midrule
%(cissm_rows)s
\midrule
Total (weighted) & %(cissm_weighted_total).1f & %(cfr_weighted_total).1f \\
Total (records) & 335 & 26 \\
\bottomrule
\end{tabular}
\vspace{4pt}
\raggedright\footnotesize{\textsuperscript{a}CSIS excluded: no structured event-type taxonomy. Taxonomies between CISSM and CFR are incommensurable; presented descriptively without statistical comparison. Weights (analysis\_weight) applied for percentages; counts reflect total records per source.}
\end{table}

%% Breakdown:
%% CISSM: %(cissm_detail)s
%% CFR:   %(cfr_detail)s
"""


def build_type_rows(event_data, source_key):
    """Build LaTeX rows for one source's event types."""
    src = event_data.get(source_key, {})
    types = src.get('event_types', {})
    if not types:
        return "N/A & %", "no data"

    rows = []
    detail_parts = []
    for et_name, info in types.items():
        cnt = info['weighted_count']
        pct = info['percent']
        # Convert scientific notation display
        cnt_str = f"{cnt:,.1f}"
        rows.append(f"{et_name} & {cnt_str} ({pct:.1f}\\%)")
        detail_parts.append(f"{et_name}={cnt}({pct}%)")

    return " \\\\\n".join(rows), "; ".join(detail_parts)


def main():
    print("[build_table3_event_types] Loading event-type descriptive...")
    with open(STATS / "event_type_descriptive.json") as f:
        et_data = json.load(f)

    cissm_rows, cissm_detail = build_type_rows(et_data, 'cissm')
    cfr_rows, cfr_detail = build_type_rows(et_data, 'cfr')

    # Combine — show CISSM types, then CFR types
    # But the table expects CISSM column and CFR column side by side.
    # We need to restructure: rows are event types, columns are sources.
    # Since taxonomies differ, we show each source's types separately.
    # Better approach: two-column layout within each row.
    # Actually the plan says "side-by-side" — let me rebuild properly.

    # Restructure: merge all unique type names as rows
    all_types = []
    for src in ['cissm', 'cfr']:
        if src in et_data:
            all_types.extend(et_data[src].get('event_types', {}).keys())
    all_types = sorted(set(all_types))

    # Special ordering: group CISSM types first, then CFR types
    cissm_type_order = ['Disruptive', 'Exploitive', 'Mixed', 'Undetermined']
    cfr_type_order = ['Espionage', 'Denial of service', 'Sabotage', 'Data destruction']

    rows = []
    cissm_detail_parts = []
    cfr_detail_parts = []

    # CISSM types
    for et in cissm_type_order:
        cissm_info = et_data.get('cissm', {}).get('event_types', {}).get(et, {})
        cfr_info = et_data.get('cfr', {}).get('event_types', {}).get(et, {})

        cissm_cell = f"{cissm_info.get('weighted_count', 0):,.1f} ({cissm_info.get('percent', 0):.1f}\\%)" if cissm_info else 'N/A'
        cfr_cell = f"{cfr_info.get('weighted_count', 0):,.1f} ({cfr_info.get('percent', 0):.1f}\\%)" if cfr_info else 'N/A'

        rows.append(f"{et} & {cissm_cell} & {cfr_cell}")

        if cissm_info:
            cissm_detail_parts.append(f"{et}={cissm_info.get('weighted_count',0)}({cissm_info.get('percent',0)}%)")

    # CFR types (not in CISSM taxonomy)
    for et in cfr_type_order:
        cfr_info = et_data.get('cfr', {}).get('event_types', {}).get(et, {})
        if not cfr_info:
            continue
        cfr_cell = f"{cfr_info.get('weighted_count', 0):,.1f} ({cfr_info.get('percent', 0):.1f}\\%)"
        rows.append(f"{et} & N/A & {cfr_cell}")
        cfr_detail_parts.append(f"{et}={cfr_info.get('weighted_count',0)}({cfr_info.get('percent',0)}%)")

    type_rows = " \\\\\n".join(rows)

    cissm_total_weight = et_data.get('cissm', {}).get('total_weight', 335)
    cfr_total_weight = et_data.get('cfr', {}).get('total_weight', 26)

    data = {
        'cissm_rows': type_rows,
        'cissm_detail': '; '.join(cissm_detail_parts),
        'cfr_detail': '; '.join(cfr_detail_parts),
        'cissm_weighted_total': cissm_total_weight,
        'cfr_weighted_total': cfr_total_weight,
    }

    table = TABLE3_TEMPLATE % data

    tables_dir = OUTPUT / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    path = tables_dir / "table3.tex"
    with open(path, 'w') as f:
        f.write(table)

    print(f"  Wrote: {path}")
    print(f"  CISSM types: {len(cissm_type_order)}")
    print(f"  CFR types: {len(cfr_type_order)}")

    # Print summary
    cissm_n = et_data.get('cissm', {}).get('n', 0)
    cfr_n = et_data.get('cfr', {}).get('n', 0)
    print(f"  N per source: CISSM={cissm_n}, CFR={cfr_n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
