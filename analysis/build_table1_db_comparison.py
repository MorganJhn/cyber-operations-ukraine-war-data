#!/usr/bin/env python3
"""
PAPER ANALYSIS SCRIPT: build_table1_db_comparison.py
Description: Table 1: database characteristics (source, N, time range, coding unit, attribution method, access).
Output: tables/table1.tex
"""

import json
import sys
from pathlib import Path

# Base directory: script location → repo root
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
STATS = BASE_DIR / "output" / "stats"
OUTPUT = BASE_DIR / "output"

TABLE1_TEMPLATE = r"""%% Auto-generated Table 1
%% Source: paper_analysis_corpus.csv descriptive.json
\begin{table}[ht]
\centering
\caption{Characteristics of the Three Cyber Conflict Databases}
\label{tab:db-comparison}
\begin{tabular}{lp{3.5cm}p{3.5cm}p{3.5cm}}
\toprule
Characteristic & CISSM & CSIS & CFR \\
\midrule
Entries & %(cissm_n)s & %(csis_n)s & %(cfr_n)s \\
Time range & %(cissm_date)s & %(csis_date)s & %(cfr_date)s \\
Coding unit & Cyber operation & Significant cyber incident & Policy-relevant event \\
Event taxonomy & Disruptive/Exploitive/ Mixed/Undetermined & Narrative descriptions\textsuperscript{a} & Espionage/Sabotage/ DDoS/Data destruction \\
Attribution method & OSINT self-attestation + researcher coding & State/official attribution & Media/law enforcement \\
Data access & Closed (Georgetown) & Public (CSIS RSI) & Public (CFR Cyber Tracker) \\
\bottomrule
\end{tabular}
\vspace{4pt}
\raggedright\footnotesize{\textsuperscript{a}CSIS entries use descriptive narratives instead of a structured event-type taxonomy. Excluded from event-type analyses (see \S4).}
\end{table}
"""


def load_stats(name):
    with open(STATS / name) as f:
        return json.load(f)


def format_date_range(months):
    """Convert month list like ['2022-02', '2024-12'] to 'Feb 2022--Dec 2024'."""
    if not months:
        return 'N/A'
    import datetime
    MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    start = months[0]
    end = months[-1]
    sy, sm = start.split('-')
    ey, em = end.split('-')
    return f"{MONTH_NAMES[int(sm)-1]} {sy}--{MONTH_NAMES[int(em)-1]} {ey}"


def main():
    print("[build_table1_db_comparison] Loading descriptive stats...")
    desc = load_stats("descriptive.json")

    sources = desc['sources']
    cissm = sources.get('cissm', {})
    csis = sources.get('csis', {})
    cfr = sources.get('cfr', {})

    # Date ranges
    cissm_date = format_date_range(cissm.get('months_covered', []))
    csis_date = format_date_range(csis.get('months_covered', []))
    cfr_date = format_date_range(cfr.get('months_covered', []))

    data = {
        'cissm_n': cissm.get('count', '?'),
        'csis_n': csis.get('count', '?'),
        'cfr_n': cfr.get('count', '?'),
        'cissm_date': cissm_date,
        'csis_date': csis_date,
        'cfr_date': cfr_date,
    }

    table = TABLE1_TEMPLATE % data

    tables_dir = OUTPUT / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    path = tables_dir / "table1.tex"
    with open(path, 'w') as f:
        f.write(table)

    print(f"  Wrote: {path}")
    print(f"  CISSM: N={data['cissm_n']}, date={cissm_date}")
    print(f"  CSIS:  N={data['csis_n']}, date={csis_date}")
    print(f"  CFR:   N={data['cfr_n']}, date={cfr_date}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
