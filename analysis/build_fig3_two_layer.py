#!/usr/bin/env python3
"""
PAPER ANALYSIS SCRIPT: build_fig3_two_layer.py
Description: Figure 3: conceptual two-layer model diagram.
   Surface layer: hacktivist DDoS, observable, OSINT-captured
   Subsurface layer: state APT, covert, curated-database captured
Output: figures/fig3.png, figures/fig3.pdf
"""

import sys
from pathlib import Path

# Base directory: script location → repo root
BASE_DIR = Path(__file__).resolve().parent.parent
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# Paths
OUTPUT = BASE_DIR / "output"


def make_figure():
    """Create the two-layer conceptual diagram."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Colors
    SURFACE_COLOR = '#4477AA'  # blue
    SUBSURFACE_COLOR = '#CCBB44'  # yellow
    ARROW_COLOR = '#555555'
    TEXT_COLOR = '#222222'

    # === SURFACE LAYER (top) ===
    # Box
    surface_box = FancyBboxPatch(
        (0.5, 4.5), 9, 2.8,
        boxstyle="round,pad=0.15",
        facecolor=SURFACE_COLOR, alpha=0.15,
        edgecolor=SURFACE_COLOR, linewidth=2
    )
    ax.add_patch(surface_box)

    # Label
    ax.text(5, 6.7, 'SURFACE LAYER', ha='center', va='center',
            fontsize=16, fontweight='bold', color=SURFACE_COLOR)

    # Characteristics
    ax.text(1.5, 5.8, '• Hacktivist DDoS / defacement', fontsize=11, color=TEXT_COLOR, va='top')
    ax.text(1.5, 5.3, '• Self-attributed / publicly claimed', fontsize=11, color=TEXT_COLOR, va='top')
    ax.text(1.5, 4.8, '• Observable in real time', fontsize=11, color=TEXT_COLOR, va='top')

    # Right column
    ax.text(6, 5.8, '• Captured by OSINT collection', fontsize=11, color=TEXT_COLOR, va='top')
    ax.text(6, 5.3, '• Dominates CISSM database (52.8% self-attributed)', fontsize=11, color=TEXT_COLOR, va='top')
    ax.text(6, 4.8, '• Episodic, reactive, expressive', fontsize=11, color=TEXT_COLOR, va='top')

    # === SUBSURFACE LAYER (bottom) ===
    subsurface_box = FancyBboxPatch(
        (0.5, 0.5), 9, 2.8,
        boxstyle="round,pad=0.15",
        facecolor=SUBSURFACE_COLOR, alpha=0.15,
        edgecolor=SUBSURFACE_COLOR, linewidth=2
    )
    ax.add_patch(subsurface_box)

    # Label
    ax.text(5, 2.7, 'SUBSURFACE LAYER', ha='center', va='center',
            fontsize=16, fontweight='bold', color=SUBSURFACE_COLOR)

    # Characteristics
    ax.text(1.5, 1.8, '• State APT / espionage / sabotage', fontsize=11, color=TEXT_COLOR, va='top')
    ax.text(1.5, 1.3, '• Anonymized / deniable', fontsize=11, color=TEXT_COLOR, va='top')
    ax.text(1.5, 0.8, '• Covert, persistent, strategic', fontsize=11, color=TEXT_COLOR, va='top')

    ax.text(6, 1.8, '• Captured by curated intelligence', fontsize=11, color=TEXT_COLOR, va='top')
    ax.text(6, 1.3, '• Dominates CSIS/CFR databases (84.6%+ state)', fontsize=11, color=TEXT_COLOR, va='top')
    ax.text(6, 0.8, '• Low-volume, continuous operations', fontsize=11, color=TEXT_COLOR, va='top')

    # === DIVIDER ===
    ax.axhline(y=4.2, xmin=0.1, xmax=0.9, color=ARROW_COLOR, linestyle='--', linewidth=1, alpha=0.5)

    # === OBSERVATION ARROWS ===
    # Arrow pointing to surface (from databases)
    ax.annotate('', xy=(5, 7.5), xytext=(5, 4.8),
                arrowprops=dict(arrowstyle='<->', color=ARROW_COLOR, lw=1.5, alpha=0.6))
    ax.text(5.3, 6.1, 'CISSM (OSINT)', fontsize=10, color=ARROW_COLOR, rotation=90, alpha=0.7)

    # Arrow pointing to subsurface
    ax.annotate('', xy=(7.5, 4.2), xytext=(7.5, 3.5),
                arrowprops=dict(arrowstyle='<->', color=ARROW_COLOR, lw=1.5, alpha=0.6))
    ax.text(7.8, 3.6, 'CSIS / CFR\n(curated)', fontsize=10, color=ARROW_COLOR, alpha=0.7,
            va='center')

    # === LEGEND ===
    # Database boxes at bottom
    legend_y = 7.6
    ax.text(0.5, legend_y, 'DATABASES:', fontsize=10, fontweight='bold', va='center')

    boxes_data = [
        (1.8, legend_y, 'CISSM\n(N=335)', SURFACE_COLOR, 'hacktivist-majority (38.5%)'),
        (4.5, legend_y, 'CSIS\n(N=82)', SUBSURFACE_COLOR, 'state-majority (76.8%)'),
        (7.0, legend_y, 'CFR\n(N=26)', SUBSURFACE_COLOR, 'state-dominant (84.6%)'),
    ]
    for x, y, name, color, desc in boxes_data:
        p = FancyBboxPatch(
            (x - 0.9, y - 1.0), 1.8, 0.9,
            boxstyle="round,pad=0.08",
            facecolor=color, alpha=0.3,
            edgecolor=color, linewidth=1.5
        )
        ax.add_patch(p)
        ax.text(x, y - 0.55, name, ha='center', va='center',
                fontsize=9, fontweight='bold', color=TEXT_COLOR)

    # Title
    ax.text(5, 7.9, 'Two-Layer Model of Cyber Operations in the Russia-Ukraine War',
            ha='center', va='bottom', fontsize=14, fontweight='bold', color=TEXT_COLOR)

    fig.tight_layout()

    # Output
    figures_dir = OUTPUT / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    for fmt, dpi in [('png', 300), ('pdf', 300)]:
        path = figures_dir / f"fig3.{fmt}"
        fig.savefig(path, dpi=dpi, bbox_inches='tight')
        print(f"  Wrote: {path}")

    plt.close(fig)
    print("  Two-layer model diagram generated")


def main():
    print("[build_fig3_two_layer] Generating conceptual diagram...")
    make_figure()
    return 0


if __name__ == "__main__":
    sys.exit(main())
