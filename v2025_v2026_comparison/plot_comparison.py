#!/usr/bin/env python3
"""Figures for the new-vs-old altitude / rise-speed comparison.

`error_vs_gps.png` pools every paired sounding in the campaign.
The two detailed time-series figures are kept for the two soundings examined
in detail; pass --timeseries <stem> to draw another.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path(__file__).resolve().parent
d = pd.read_pickle(OUT / "_merged.pkl")

# Reference categorical palette, light mode, slots 1-3 (all-pairs validated).
#   blue = v2026 (new) retrieval, orange = v2025 (original) retrieval.
# GPS truth is a reference, not a categorical series, so it wears neutral ink.
C_NEW, C_OLD = "#2a78d6", "#eb6834"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#dcdbd6", "#fcfcfb"
C_GPS = INK

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "font.size": 9,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "figure.dpi": 130,
})

DETAIL = ["2025-05-25_1510_15333", "2025-06-05_1639_15326"]
TITLE = {"2025-05-25_1510_15333": "2025-05-25 15:10 UTC  |  sonde 15333",
         "2025-06-05_1639_15326": "2025-06-05 16:39 UTC  |  sonde 15326"}


def tidy(ax, ylabel, title):
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=10, color=INK, pad=6)
    ax.margins(x=0.01)


# ---------------------------------------------------------------- time series
def timeseries(case):
    g = d[d.case == case].reset_index(drop=True)
    m = g.alt_gps.notna()
    t = g.t / 60.0
    tg = t[m]
    title = TITLE.get(case, case)

    fig, axes = plt.subplots(4, 1, figsize=(9.5, 11), sharex=True)
    fig.suptitle(f"Altitude and rise speed: v2026 vs v2025 retrieval\n{title}",
                 x=0.012, ha="left", fontsize=12, color=INK)

    ax = axes[0]
    ax.plot(t, g.alt_old / 1000, lw=2, color=C_OLD, label="v2025")
    ax.plot(t, g.alt_new / 1000, lw=2, color=C_NEW, label="v2026")
    ax.plot(tg, g.alt_gps[m] / 1000, "o", ms=3.4, color=C_GPS, mec=SURF, mew=0.6,
            label="GPS (truth)", zorder=5)
    tidy(ax, "Altitude (km MSL)", "Altitude")
    ax.legend(loc="lower center", ncol=3)

    ax = axes[1]
    ax.axhline(0, color=INK2, lw=0.8)
    ax.plot(tg, (g.alt_old - g.alt_gps)[m], lw=1.8, color=C_OLD, label="v2025 − GPS")
    ax.plot(tg, (g.alt_new - g.alt_gps)[m], lw=1.8, color=C_NEW, label="v2026 − GPS")
    tidy(ax, "Altitude error (m)", "Altitude error against GPS")
    ax.legend(loc="upper left", ncol=2)

    ax = axes[2]
    ax.axhline(0, color=INK2, lw=0.8)
    ax.plot(t, g.rise_old, lw=1.6, color=C_OLD, alpha=0.9, label="v2025")
    ax.plot(t, g.rise_new, lw=1.6, color=C_NEW, label="v2026")
    ax.plot(tg, g.rise_gps[m], "o", ms=3.4, color=C_GPS, mec=SURF, mew=0.6,
            label="GPS (truth)", zorder=5)
    tidy(ax, "Rise speed (m s$^{-1}$)", "Rise speed")
    ax.legend(loc="lower left", ncol=3)

    ax = axes[3]
    ax.axhline(0, color=INK2, lw=0.8)
    series = [("rise_old", C_OLD, "v2025 − GPS"),
              ("rise_new", C_NEW, "v2026 − GPS")]
    errs = {c: (g[c] - g.rise_gps)[m] for c, _, _ in series}
    for col, colr, lab in series:
        ax.plot(tg, errs[col], lw=1.8, color=colr, label=lab)
    ylim = 12.0
    ax.set_ylim(-ylim, ylim)
    off = []
    for col, colr, _ in series:
        e = errs[col]
        for sign, mark in ((1, "^"), (-1, "v")):
            k = (e * sign) > ylim
            if k.any():
                ax.plot(tg[k], np.full(int(k.sum()), sign * ylim * 0.97), mark,
                        ms=6, color=colr, mec=SURF, mew=0.6, zorder=6)
        off += [f"{v:+.1f}" for v in e[e.abs() > ylim]]
    note = f"  (off scale: {', '.join(off)} m s⁻¹)" if off else ""
    tidy(ax, "Rise speed error (m s$^{-1}$)", "Rise speed error against GPS" + note)
    ax.legend(loc="upper left", ncol=2)
    ax.set_xlabel("Minutes from first record")

    fig.tight_layout(rect=[0, 0, 1, 0.965])
    fig.savefig(OUT / f"{case}_timeseries.png", bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------- campaign-wide scatters
MIN_SND = 5      # minimum soundings contributing to a binned profile point


def error_figure():
    """The two binned error profiles - the scatters were dropped because both
    products sit almost on the 1:1 line and the panels carried no information."""
    m = d.alt_gps.notna()
    n_snd = d.case.nunique()

    def summary(col, truth, unit, dp):
        k = d[col].notna() & d[truth].notna()
        e = (d[col] - d[truth])[k]
        sl = np.polyfit(d[truth][k], d[col][k], 1)[0]
        return (f"median |err| {e.abs().median():.{dp}f} {unit}, "
                f"MAE {e.abs().mean():.{dp}f} {unit}, slope {sl:.3f}")

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6))
    fig.suptitle("Retrieval error against GPS truth — all paired soundings in "
                 f"the campaign\n{n_snd} soundings, {int(m.sum()):,} QC-passed "
                 "GPS fixes.  Line = median across soundings, band = interquartile "
                 "range.",
                 x=0.011, ha="left", fontsize=12, color=INK)

    # ---- altitude error with height ----------------------------------------
    ax = axes[0]
    edges = np.arange(0, 16001, 1000)
    ctr = 0.5 * (edges[1:] + edges[:-1]) / 1000
    sub = d[m].copy()
    sub["bin"] = pd.cut(sub.alt_gps, edges, labels=False)
    ax.axvline(0, color=INK2, lw=0.9)
    for col, colr, lab in [("alt_old", C_OLD, "v2025 − GPS"),
                           ("alt_new", C_NEW, "v2026 − GPS")]:
        sub["e"] = sub[col] - sub.alt_gps
        grp = sub.groupby(["bin", "case"], observed=True)["e"].median() \
                 .groupby("bin", observed=True)
        n_snd_b, med = grp.size(), grp.median()
        q1, q3 = grp.quantile(0.25), grp.quantile(0.75)
        keep = n_snd_b[n_snd_b >= MIN_SND].index
        idx = np.array([int(i) for i in keep])
        ax.fill_betweenx(ctr[idx], q1[keep], q3[keep], color=colr, alpha=0.18, lw=0)
        ax.plot(med[keep], ctr[idx], lw=2.2, color=colr, label=lab)
        ax.plot(med[keep], ctr[idx], "o", ms=4.5, color=colr, mec=SURF, mew=0.6)
    counts = (sub.groupby(["bin", "case"], observed=True).size()
                 .groupby("bin", observed=True).size())
    from matplotlib.transforms import blended_transform_factory
    tf = blended_transform_factory(ax.transAxes, ax.transData)
    shown = counts[counts >= MIN_SND]
    for b, nb in shown.items():
        ax.text(0.99, ctr[int(b)], f"{nb}", fontsize=7, color=INK2,
                va="center", ha="right", transform=tf)
    ax.text(0.99, ctr[int(shown.index.max())] + 0.9, "soundings", fontsize=7,
            color=INK2, va="center", ha="right", transform=tf)
    ax.set_xlabel("Altitude error (m)")
    ax.set_ylabel("GPS altitude (km MSL)")
    ax.set_title("Altitude error with height\n"
                 f"v2026: {summary('alt_new', 'alt_gps', 'm', 1)}\n"
                 f"v2025: {summary('alt_old', 'alt_gps', 'm', 1)}",
                 loc="left", fontsize=9.5, color=INK, pad=6)
    ax.legend(loc="lower left", fontsize=9)

    # ---- rise speed error with rise speed -----------------------------------
    ax = axes[1]
    wedges = np.array([-60, -40, -30, -20, -15, -10, -5, -2, 2, 5,
                       10, 15, 20, 30, 40, 60, 80])
    wctr = 0.5 * (wedges[1:] + wedges[:-1])
    sub_w = d[m].copy()
    sub_w["bin"] = pd.cut(sub_w.rise_gps, wedges, labels=False)
    ax.axhline(0, color=INK2, lw=0.9)
    for col, colr, lab in [("rise_old", C_OLD, "v2025 − GPS"),
                           ("rise_new", C_NEW, "v2026 − GPS")]:
        sub_w["e"] = sub_w[col] - sub_w.rise_gps
        grp = sub_w.groupby(["bin", "case"], observed=True)["e"].median() \
                   .groupby("bin", observed=True)
        n_snd_b, med = grp.size(), grp.median()
        q1, q3 = grp.quantile(0.25), grp.quantile(0.75)
        keep = n_snd_b[n_snd_b >= MIN_SND].index
        idx = np.array([int(i) for i in keep])
        ax.fill_between(wctr[idx], q1[keep], q3[keep], color=colr, alpha=0.18, lw=0)
        ax.plot(wctr[idx], med[keep], lw=2.2, color=colr, label=lab)
        ax.plot(wctr[idx], med[keep], "o", ms=4.5, color=colr, mec=SURF, mew=0.6)
    counts = (sub_w.groupby(["bin", "case"], observed=True).size()
                   .groupby("bin", observed=True).size())
    yt = ax.get_ylim()[0]
    for b, nb in counts.items():
        if nb >= MIN_SND:
            ax.text(wctr[int(b)], yt, f"{nb}", fontsize=7, color=INK2,
                    va="bottom", ha="center")
    ax.set_xlabel("GPS rise speed (m s$^{-1}$)")
    ax.set_ylabel("Rise speed error (m s$^{-1}$)")
    ax.set_title("Rise speed error with rise speed\n"
                 f"v2026: {summary('rise_new', 'rise_gps', 'm/s', 2)}\n"
                 f"v2025: {summary('rise_old', 'rise_gps', 'm/s', 2)}",
                 loc="left", fontsize=9.5, color=INK, pad=6)
    ax.legend(loc="upper right", fontsize=9)

    for ax in axes:
        ax.margins(x=0.02)
    fig.text(0.011, 0.005,
             f"Each sounding contributes its own median error per bin; small "
             f"grey numbers are the soundings per bin, and bins with fewer than "
             f"{MIN_SND} are not drawn.",
             fontsize=8.5, color=INK2, ha="left")
    fig.tight_layout(rect=[0, 0.03, 1, 0.90])
    fig.savefig(OUT / "error_vs_gps.png", bbox_inches="tight", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    args = sys.argv[1:]
    cases = args[args.index("--timeseries") + 1:] if "--timeseries" in args else DETAIL
    for c in cases:
        if c in set(d.case):
            timeseries(c)
        else:
            print(f"  no data for {c}")
    error_figure()
    print("wrote", *(p.name for p in sorted(OUT.glob("*.png"))))
