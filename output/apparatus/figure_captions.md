# Figure Captions

## Figure 1: Temporal Distribution of Cyber Operations by Database
**File:** fig1.png/pdf
**Section:** §4 Data & Sources
**Description:** Stacked area chart showing monthly weighted counts of cyber operations
from CISSM (blue), CSIS (yellow), and CFR (purple) databases from February 2022 to
December 2024. CISSM dominates volume throughout the period (301 weighted incidents),
driven by OSINT capture of self-attributed hacktivist DDoS operations. CSIS shows
steadier low-volume state-attributed incidents (79, temporal filtered). CFR covers only the first year
of the conflict (26 incidents, ending December 2022).
**Data:** paper_analysis_corpus.csv, weighted by analysis_weight

## Figure 2: Actor Type Composition by Database
**File:** fig2.png/pdf
**Section:** §5b Collection-Driven Measurement (F2)
**Description:** Stacked bar chart comparing actor type distributions across the three
databases (unweighted counts). CISSM: hacktivist-majority (38.5% pro-Russian hacktivist,
28.7% Russian state). CSIS: state-majority (76.8% Russian state, 15.9% pro-Russian
hacktivist). CFR: state-dominant (84.6% Russian state, 11.5% Ukrainian state, 0%
hacktivist). N values above each bar.
**Data:** corpus_with_actor_type.csv, unweighted row counts

## Figure 3: Two-Layer Model of Cyber Operations
**File:** fig3.png/pdf
**Section:** §5c Two-Layer Model (F3), §6 Discussion
**Description:** Conceptual diagram illustrating the two-layer model of cyber operations
in the Russia-Ukraine war. The surface layer contains hacktivist DDoS and defacement
operations that are self-attributed, observable in real time, and captured by CISSM's
OSINT collection. The subsurface layer contains state APT, espionage, and sabotage
operations that are anonymized, covert, and captured by curated databases (CSIS, CFR).
Each database captures a different slice of the phenomenon, producing the observed
cross-source divergence.

## Appendix Figure A1: Data Pipeline Sankey
**File:** figA1.png
**Section:** Appendix
**Description:** Sankey diagram showing the end-to-end data pipeline from raw
extraction (18,995 records) through deduplication, NLP filtering, and enrichment
to the final analysis corpus (453 records, 3 sources). Flow widths proportional to
record counts at each stage.
