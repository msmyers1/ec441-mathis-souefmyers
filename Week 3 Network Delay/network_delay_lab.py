"""
EC441 — Network Delay Calculator & Visualizer
Lab Assignment: Network Fundamentals & Delays

This tool calculates end-to-end delay for store-and-forward packet networks
and generates visualizations showing how each delay component scales.

Usage:
    python network_delay_lab.py              # interactive mode
    python network_delay_lab.py --demo       # run demo with sample values

Author: Mathis Souef-Myers
Course: EC441, Professor Carruthers, Spring 2026
"""

import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ─── Constants ───────────────────────────────────────────────────────────────
V_COPPER = 2.0e8      # signal speed in copper/fiber (m/s)
V_LIGHT  = 3.0e8      # speed of light in vacuum (m/s)

# ─── Core delay calculations ────────────────────────────────────────────────

def transmission_delay(L_bits, R_bps):
    """Time to push all bits onto the wire: d_trans = L / R"""
    return L_bits / R_bps

def propagation_delay(d_meters, v=V_COPPER):
    """Time for signal to travel the link: d_prop = d / v"""
    return d_meters / v

def end_to_end_delay(L_bits, R_bps, d_meters, N_links, v=V_COPPER, d_proc=0):
    """
    Total delay for store-and-forward across N links.
    
    In store-and-forward, the first link takes (d_trans + d_prop).
    Each subsequent link adds another d_trans + d_prop.
    So total = N * d_trans + N * d_prop + processing.
    """
    d_trans = transmission_delay(L_bits, R_bps)
    d_prop = propagation_delay(d_meters, v)
    total = N_links * d_trans + N_links * d_prop + N_links * d_proc
    return {
        "trans_per_link": d_trans,
        "prop_per_link": d_prop,
        "proc_per_link": d_proc,
        "N_links": N_links,
        "total_trans": N_links * d_trans,
        "total_prop": N_links * d_prop,
        "total_proc": N_links * d_proc,
        "total": total,
    }

def format_time(seconds):
    """Pretty-print a time value with appropriate units."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    else:
        return f"{seconds:.4f} s"

# ─── Visualization ──────────────────────────────────────────────────────────

def plot_delay_breakdown(result, title="End-to-End Delay Breakdown"):
    """Pie chart + bar chart showing delay components."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(title, fontsize=16, fontweight="bold", y=1.02)

    components = ["Transmission", "Propagation", "Processing"]
    values = [result["total_trans"], result["total_prop"], result["total_proc"]]
    colors = ["#00A8E8", "#FF8C42", "#4CAF50"]

    # Filter out zero components
    nonzero = [(c, v, col) for c, v, col in zip(components, values, colors) if v > 0]
    if not nonzero:
        ax1.text(0.5, 0.5, "All delays are zero", ha="center", va="center")
        return fig

    labels, vals, cols = zip(*nonzero)

    # Pie chart
    wedges, texts, autotexts = ax1.pie(
        vals, labels=labels, colors=cols, autopct="%1.1f%%",
        startangle=90, textprops={"fontsize": 11}
    )
    for t in autotexts:
        t.set_fontweight("bold")
    ax1.set_title("Relative Contribution", fontsize=13)

    # Bar chart with actual values
    bars = ax2.barh(labels, vals, color=cols, height=0.5)
    ax2.set_xlabel("Delay (seconds)", fontsize=11)
    ax2.set_title("Absolute Delay", fontsize=13)
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_width() * 1.02, bar.get_y() + bar.get_height() / 2,
                 format_time(val), va="center", fontsize=10, fontweight="bold")
    ax2.set_xlim(0, max(vals) * 1.3)

    fig.tight_layout()
    return fig


def plot_sweep_packet_size(R_bps, d_meters, N_links, v=V_COPPER):
    """Show how total delay changes as packet size varies."""
    sizes_bytes = np.logspace(1, 7, 200)  # 10 B to 10 MB
    sizes_bits = sizes_bytes * 8

    totals = []
    trans_totals = []
    prop_totals = []
    for L in sizes_bits:
        r = end_to_end_delay(L, R_bps, d_meters, N_links, v)
        totals.append(r["total"])
        trans_totals.append(r["total_trans"])
        prop_totals.append(r["total_prop"])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.loglog(sizes_bytes, totals, "k-", linewidth=2.5, label="Total delay")
    ax.loglog(sizes_bytes, trans_totals, "--", color="#00A8E8", linewidth=1.8, label="Transmission")
    ax.loglog(sizes_bytes, prop_totals, "--", color="#FF8C42", linewidth=1.8, label="Propagation")

    ax.set_xlabel("Packet Size (bytes)", fontsize=12)
    ax.set_ylabel("Delay (seconds)", fontsize=12)
    ax.set_title(
        f"Delay vs. Packet Size\n(R = {R_bps/1e6:.0f} Mb/s, d = {d_meters/1e3:.0f} km, {N_links} links)",
        fontsize=14, fontweight="bold"
    )
    ax.legend(fontsize=11)
    ax.grid(True, which="both", alpha=0.3)

    # Annotate crossover point
    crossover_idx = np.argmin(np.abs(np.array(trans_totals) - np.array(prop_totals)))
    ax.axvline(sizes_bytes[crossover_idx], color="gray", linestyle=":", alpha=0.6)
    ax.annotate(
        f"Crossover ≈ {sizes_bytes[crossover_idx]:.0f} B",
        xy=(sizes_bytes[crossover_idx], totals[crossover_idx]),
        xytext=(sizes_bytes[crossover_idx] * 5, totals[crossover_idx] * 3),
        arrowprops=dict(arrowstyle="->", color="gray"),
        fontsize=10, color="gray"
    )

    fig.tight_layout()
    return fig


def plot_sweep_distance(L_bits, R_bps, N_links, v=V_COPPER):
    """Show how total delay changes as link distance varies."""
    distances_km = np.logspace(-1, 4, 200)  # 100 m to 10,000 km
    distances_m = distances_km * 1e3

    totals = []
    trans_totals = []
    prop_totals = []
    for d in distances_m:
        r = end_to_end_delay(L_bits, R_bps, d, N_links, v)
        totals.append(r["total"])
        trans_totals.append(r["total_trans"])
        prop_totals.append(r["total_prop"])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.loglog(distances_km, totals, "k-", linewidth=2.5, label="Total delay")
    ax.loglog(distances_km, trans_totals, "--", color="#00A8E8", linewidth=1.8, label="Transmission")
    ax.loglog(distances_km, prop_totals, "--", color="#FF8C42", linewidth=1.8, label="Propagation")

    ax.set_xlabel("Link Distance (km)", fontsize=12)
    ax.set_ylabel("Delay (seconds)", fontsize=12)
    ax.set_title(
        f"Delay vs. Distance\n(L = {L_bits/8:.0f} bytes, R = {R_bps/1e6:.0f} Mb/s, {N_links} links)",
        fontsize=14, fontweight="bold"
    )
    ax.legend(fontsize=11)
    ax.grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    return fig


def plot_sweep_link_rate(L_bits, d_meters, N_links, v=V_COPPER):
    """Show how total delay changes as link rate varies."""
    rates_mbps = np.logspace(-1, 5, 200)  # 100 kb/s to 100 Gb/s
    rates_bps = rates_mbps * 1e6

    totals = []
    trans_totals = []
    prop_totals = []
    for R in rates_bps:
        r = end_to_end_delay(L_bits, R, d_meters, N_links, v)
        totals.append(r["total"])
        trans_totals.append(r["total_trans"])
        prop_totals.append(r["total_prop"])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.loglog(rates_mbps, totals, "k-", linewidth=2.5, label="Total delay")
    ax.loglog(rates_mbps, trans_totals, "--", color="#00A8E8", linewidth=1.8, label="Transmission")
    ax.loglog(rates_mbps, prop_totals, "--", color="#FF8C42", linewidth=1.8, label="Propagation")

    ax.set_xlabel("Link Rate (Mb/s)", fontsize=12)
    ax.set_ylabel("Delay (seconds)", fontsize=12)
    ax.set_title(
        f"Delay vs. Link Rate\n(L = {L_bits/8:.0f} bytes, d = {d_meters/1e3:.0f} km, {N_links} links)",
        fontsize=14, fontweight="bold"
    )
    ax.legend(fontsize=11)
    ax.grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    return fig


# ─── Interactive mode ───────────────────────────────────────────────────────

def get_float(prompt, default=None):
    """Get a float from the user with an optional default."""
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if raw == "" and default is not None:
            return default
        try:
            return float(raw)
        except ValueError:
            print("  Please enter a number.")

def get_int(prompt, default=None):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if raw == "" and default is not None:
            return default
        try:
            return int(raw)
        except ValueError:
            print("  Please enter an integer.")

def interactive_mode():
    """Walk the user through inputting parameters and show results."""
    print("=" * 60)
    print("  EC441 Network Delay Calculator")
    print("  Store-and-Forward End-to-End Delay")
    print("=" * 60)
    print()

    L_bytes = get_float("Packet size in bytes", 1500)
    R_mbps = get_float("Link rate in Mb/s", 100)
    d_km = get_float("Link distance in km", 2000)
    N = get_int("Number of links (hops)", 3)
    d_proc_us = get_float("Processing delay per hop in μs", 0)

    L_bits = L_bytes * 8
    R_bps = R_mbps * 1e6
    d_meters = d_km * 1e3
    d_proc = d_proc_us * 1e-6

    result = end_to_end_delay(L_bits, R_bps, d_meters, N, V_COPPER, d_proc)

    print()
    print("─" * 60)
    print("  RESULTS")
    print("─" * 60)
    print(f"  Transmission delay per link:  {format_time(result['trans_per_link'])}")
    print(f"  Propagation delay per link:   {format_time(result['prop_per_link'])}")
    if d_proc > 0:
        print(f"  Processing delay per link:    {format_time(result['proc_per_link'])}")
    print(f"  Number of links:              {N}")
    print()
    print(f"  Total transmission delay:     {format_time(result['total_trans'])}")
    print(f"  Total propagation delay:      {format_time(result['total_prop'])}")
    if d_proc > 0:
        print(f"  Total processing delay:       {format_time(result['total_proc'])}")
    print(f"  ─────────────────────────────────")
    print(f"  END-TO-END DELAY:             {format_time(result['total'])}")
    print()

    # Determine which delay dominates
    if result["total_trans"] > result["total_prop"] * 2:
        print("  → Transmission dominates. Large packet relative to link speed.")
    elif result["total_prop"] > result["total_trans"] * 2:
        print("  → Propagation dominates. Long distance relative to packet size.")
    else:
        print("  → Transmission and propagation are comparable.")
    print()

    # Generate plots
    print("Generating plots...")

    fig1 = plot_delay_breakdown(result,
        f"Delay Breakdown: {L_bytes:.0f} B over {R_mbps:.0f} Mb/s, {d_km:.0f} km, {N} links")
    fig1.savefig("delay_breakdown.png", dpi=150, bbox_inches="tight")
    print("  → delay_breakdown.png")

    fig2 = plot_sweep_packet_size(R_bps, d_meters, N)
    fig2.savefig("sweep_packet_size.png", dpi=150, bbox_inches="tight")
    print("  → sweep_packet_size.png")

    fig3 = plot_sweep_distance(L_bits, R_bps, N)
    fig3.savefig("sweep_distance.png", dpi=150, bbox_inches="tight")
    print("  → sweep_distance.png")

    fig4 = plot_sweep_link_rate(L_bits, d_meters, N)
    fig4.savefig("sweep_link_rate.png", dpi=150, bbox_inches="tight")
    print("  → sweep_link_rate.png")

    plt.close("all")
    print("\nDone! Check the PNG files for visualizations.")


def demo_mode():
    """Run two contrasting scenarios from the review slides."""
    print("=" * 60)
    print("  EC441 Network Delay Calculator — Demo Mode")
    print("=" * 60)

    scenarios = [
        {
            "name": "Scenario A: Large file, short distance",
            "L_bytes": 5e6, "R_mbps": 10, "d_km": 1.5, "N": 3,
            "note": "5 MB file over 10 Mb/s, 1.5 km — transmission dominates"
        },
        {
            "name": "Scenario B: Small packet, long distance",
            "L_bytes": 100, "R_mbps": 10, "d_km": 5000, "N": 3,
            "note": "100 bytes over 10 Mb/s, 5000 km — propagation dominates"
        },
    ]

    for i, sc in enumerate(scenarios):
        print(f"\n{'─' * 60}")
        print(f"  {sc['name']}")
        print(f"  {sc['note']}")
        print(f"{'─' * 60}")

        L_bits = sc["L_bytes"] * 8
        R_bps = sc["R_mbps"] * 1e6
        d_meters = sc["d_km"] * 1e3

        result = end_to_end_delay(L_bits, R_bps, d_meters, sc["N"])

        print(f"  d_trans per link: {format_time(result['trans_per_link'])}")
        print(f"  d_prop per link:  {format_time(result['prop_per_link'])}")
        print(f"  Total ({sc['N']} links):  {format_time(result['total'])}")

        if result["total_trans"] > result["total_prop"] * 2:
            print("  → Transmission dominates")
        elif result["total_prop"] > result["total_trans"] * 2:
            print("  → Propagation dominates")
        else:
            print("  → Both comparable")

        fig = plot_delay_breakdown(result, sc["name"])
        fname = f"demo_scenario_{chr(65+i)}.png"
        fig.savefig(fname, dpi=150, bbox_inches="tight")
        print(f"  → {fname}")
        plt.close(fig)

    # Generate sweep plots using Scenario A params
    print(f"\n{'─' * 60}")
    print("  Generating parameter sweep plots...")
    print(f"{'─' * 60}")

    fig2 = plot_sweep_packet_size(10e6, 1500, 3)
    fig2.savefig("demo_sweep_packet_size.png", dpi=150, bbox_inches="tight")
    print("  → demo_sweep_packet_size.png")

    fig3 = plot_sweep_distance(1500 * 8, 10e6, 3)
    fig3.savefig("demo_sweep_distance.png", dpi=150, bbox_inches="tight")
    print("  → demo_sweep_distance.png")

    fig4 = plot_sweep_link_rate(1500 * 8, 1500, 3)
    fig4.savefig("demo_sweep_link_rate.png", dpi=150, bbox_inches="tight")
    print("  → demo_sweep_link_rate.png")

    plt.close("all")
    print("\nDone!")


# ─── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EC441 Network Delay Calculator")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample scenarios")
    args = parser.parse_args()

    if args.demo:
        demo_mode()
    else:
        interactive_mode()
