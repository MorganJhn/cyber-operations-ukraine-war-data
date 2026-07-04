#!/usr/bin/env python3
"""
PAPER ANALYSIS SCRIPT: build_table2_overlap.py
Description: Table 2: cross-source overlap matrix from overlap_matrix.json.
Output: tables/table2.tex
"""

import json
import sys
from pathlib import Path

# Base directory: script location → repo root
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
STATS = BASE_DIR / "output" / "stats"
OUTPUT = BASE_DIR / "output"

TABLE2_TEMPLATE = r"""%% Auto-generated Table 2
%% Source: overlap_matrix.json (analysis_overlay.csv, N=487 pairs)
\begin{table}[ht]
\centering
\caption{Pairwise Cross-Source Overlap Matrix}
\label{tab:overlap}
\begin{tabular}{lccc}
\toprule
 & CISSM & CSIS & CFR \\
\midrule
CISSM & %(cissm_cissm)s & — & — \\
CSIS  & %(cissm_csis)s\textsuperscript{a} & %(csis_csis)s & — \\
CFR   & %(cissm_cfr)s\textsuperscript{a} & %(csis_cfr)s\textsuperscript{a} & %(cfr_cfr)s \\
\bottomrule
\end{tabular}
\vspace{4pt}
\raggedright\footnotesize{\textsuperscript{a}Date-proximity only; not verified for incident identity. %(same_date)s of %(total_pairs)s overlay pairs share the same date (day\_diff=0). No verified same-incident matches found across databases.}
\end{table}
"""


def main():
    print("[build_table2_overlap] Loading overlap matrix...")
    with open(STATS / "overlap_matrix.json") as f:
        overlap = json.load(f)

    matrix = overlap['matrix']
    data = {
        'cissm_cissm': matrix['cissm']['cissm'],
        'csis_csis': matrix['csis']['csis'],
        'cfr_cfr': matrix['cfr']['cfr'],
        'cissm_csis': matrix['cissm']['csis'],
        'cissm_cfr': matrix['cissm']['cfr'],
        'csis_cfr': matrix['csis']['cfr'],
        'same_date': overlap['same_date_pairs'],
        'total_pairs': overlap['total_overlay_pairs'],
    }

    table = TABLE2_TEMPLATE % data

    tables_dir = OUTPUT / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    path = tables_dir / "table2.tex"
    with open(path, 'w') as f:
        f.write(table)

    print(f"  Wrote: {path}")
    print(f"  Overlap pairs: CISSM-CSIS={data['cissm_csis']}, "
          f"CISSM-CFR={data['cissm_cfr']}, CSIS-CFR={data['csis_cfr']}")
    print(f"  Same-date: {data['same_date']}/{data['total_pairs']} pairs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
