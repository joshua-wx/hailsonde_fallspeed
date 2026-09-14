# Sparv altitude / rise-speed update — validation against GPS

Compares the **new** Sparv retrieval against the **original** software across the
whole ICECHIP campaign, using the **GPS altitude and GPS rise speed** carried in
the new files as truth.

| | path |
|---|---|
| new product | `/home/meso/data/icechip-hailsonde-data/v2026/<yyyymmdd>/<category>/<stem>.alt.csv` |
| original | `/home/meso/data/icechip-hailsonde-data/v2025/<category>/[<yyyymmdd>/]<stem>.raw_history.csv` |

The two trees are organised differently (v2026 nests category under date;
`v2025/updraft` nests date under category and `v2025/proximity` is flat),
so soundings are paired on their **stem** (`date_time_sondeid`), which is unique
across the campaign, and merged on the UTC time stamp rather than by row order.

**Coverage:** 65 v2026 soundings, 62 with an v2025 counterpart, 61 with
enough usable GPS to score — **87,478 samples, 8,675 QC-passed GPS fixes**.
No reference exists for `2025-05-18_2314_15297_merged`,
`2025-05-23_1633_15331_merged` or `2025-05-29_2136_15306`;
`2025-06-22_1733_15392` has fewer than 3 usable GPS fixes.

## Files

- `compare_alt_rise.py` — pairing, QC, merge, derived rise speeds, statistics
- `plot_comparison.py` — figures (`--timeseries <stem>` to draw another sounding)
- `comparison_stats.csv` — statistics per sounding and pooled
- `merged_all_soundings.csv` — every merged sample: both products, GPS, derived
- `error_vs_gps.png` — all soundings pooled: two binned error profiles,
  altitude error with height and rise speed error with rise speed.  (Plain
  retrieved-vs-GPS scatters were dropped: both products sit almost on the 1:1
  line, so the panels carried no usable information.  Their headline numbers —
  median absolute error, MAE and regression slope — are printed in the panel
  titles instead.)
- `<case>_timeseries.png` — the two soundings looked at in detail

### Buoyancy and drag uncertainty

- `wbuoy_drag.ipynb` — derives `w_buoy` and `eps_upd-drag` for the ICECHIP flight train
  (20 g balloon, 0.60 m launch diameter), following Marinescu et al. (2020) §2a and
  Appendix B but re-deriving every number rather than adopting theirs.  Reads the v2026
  files directly and does not depend on `compare_alt_rise.py`.
- `wbuoy_drag_per_launch.csv`, `wbuoy_drag_profile.csv`, `wbuoy_drag_summary.csv`
- `wbuoy_envelope.png`, `wbuoy_dragcurve.png`, `wbuoy_dragrange.png`

### Detached-sonde terminal velocity

- `vt_detached.ipynb` — `V_T(ρ)` for the sonde falling without the balloon, using
  `V_T(ρ) = V_T,ng · (ρ_ng/ρ)^0.4`.  `ρ_ng` is per case from the lowest 50 m AGL of the
  launch; `V_T,ng` is pooled across events per version.  Standalone.
- `vt_detached_per_case.csv`, `vt_detached_params.csv`, `vt_detached_profile.csv`
- `vt_detached_anatomy.png`, `vt_detached_nearground.png`, `vt_detached_law.png`

## Headline numbers (pooled over all soundings)

Median-based columns are the ones to read: a handful of pathological soundings
dominate the mean-based ones.

| Field | Method | median err | median abs err | MAE | RMSE | slope |
|---|---|---|---|---|---|---|
| Altitude (m) | New | −4 | **11** | **96** | **252** | 0.977 |
| | Original | +13 | 29 | 151 | 552 | 1.018 |
| Rise speed (m/s) | New | −0.04 | 0.31 | **0.87** | **2.82** | 0.927 |
| | Original | +0.02 | **0.29** | 0.91 | 3.05 | 1.033 |

**Altitude is clearly better** — 2.6x on median absolute error, and the
error-with-height profile shows why: the original drifts to about +600 m by
12.5 km while the new one stays near zero at every level.

**Rise speed is essentially a tie** on aggregate scores, but the
error-with-rise-speed profile shows the two products fail in opposite
directions.  Error grows roughly linearly with |rise speed| in both, mirrored
about zero: at +50 m/s the new field reads about 2.7 m/s low and the original
about 3.0 m/s high; at -35 m/s the signs flip.  That is the slope 0.93 vs 1.03
difference made visible - the new retrieval damps vertical motion, the original
exaggerates it.  Near zero both are unbiased, which is why the pooled medians
look identical.

Note this is a weaker altitude result than the two updraft soundings examined
first suggested (where the original drifted +450 m on average).  Most of the
campaign is proximity soundings that stay low, where the original's
drift-with-height has little room to develop.

## Buoyancy and drag — headline numbers

From `wbuoy_drag.ipynb`.  20 g balloon, 0.60 m launch diameter, in two payload versions
identified by the sonde ID in the filename stem: **v1** (id < 15312) carries 25 g, **v2**
(id 15312–15399) carries 20 g.  All 65 soundings fall in one range or the other.

| quantity | v1 (25 g) | v2 (20 g) | basis |
|---|---|---|---|
| net free lift at launch | 49.9 g | 53.9 g | computed from the balloon spec, Eq. (B1) |
| `w_buoy` at launch | 3.19 m/s | 3.33 m/s | theory, C_D = 0.35 |
| `w_buoy` at ρ = 0.30 | 3.88 m/s | 4.05 m/s | theory, expanded balloon |
| `eps_upd-drag` | ±0.94 m/s | ±0.98 m/s | Appendix B, worst case |
| buoyancy + drag combined | ±1.13 m/s | ±1.17 m/s | C_D counted once, plus fill variability |
| observed sub-cloud rate | 5.56 m/s | 5.13 m/s | **upper bound** — inflow contaminated |
| launches over the buoyancy ceiling | 15 of 20 | 9 of 22 | cannot be buoyancy |

**The observed sub-cloud ascent rate cannot be used as `w_buoy`.** 24 of 42 freely
ascending launches climb faster than buoyancy alone can manage for their flight train,
even at the most favourable drag coefficient — they are measuring inflow, not the balloon.
The uncontaminated remainder (mean 3.24 m/s, sd 0.63) agrees with the theoretical value.

This is the main reason the Marinescu approach cannot be ported directly: their `w_buoy`
came from thirteen dedicated fair-weather launches, and this campaign has no equivalent
clean set.  A handful of fair-weather launches with each version, plus a spring-scale
free-lift reading at each, would fix it for the next campaign.

Note that the 5 g payload difference between versions is worth only 0.14 m/s of ascent
rate — far below the inflow contamination.  Pooled over the campaign v1 *appears* to
ascend faster despite being heavier, but that is a sampling artefact: restricted to the
four days both versions flew, v2 is faster, as the free-lift difference predicts.  The
notebook checks this explicitly.

## Detached-sonde fall speed — headline numbers

From `vt_detached.ipynb`, at a reference density ρ_ref = 1.041 kg/m³:

| | v1 (25 g) | v2 (20 g) |
|---|---|---|
| `V_T,ref` | 20.7 ± 2.8 m/s | 21.6 ± 2.2 m/s |
| cases contributing | 8 | 11 |
| spread between flights | ±6.4 m/s | ±5.7 m/s |

Applied as `V_T(ρ) = V_T,ng · (ρ_ng/ρ)^0.4`, this gives roughly 21 m/s near the ground
rising to about 40 m/s at ρ = 0.20.

**The sonde is not at terminal velocity for most of the fall.** In 25 of 30 cases the fall
speed *grows* through the descent — median 14 m/s at the start of free fall to 22 m/s by
the end — because the burst balloon remnant stays attached and progressively sheds drag.
GPS velocities confirm this is physical, not a retrieval artefact.  It is why `V_T,ng` is
anchored on the near-ground band, where the growth has stopped, and why fitting the whole
descent profile returns the wrong sign for the density exponent.

Consequence for use: the law describes the **bare sonde**.  Aloft the real system falls
slower than the curve, so subtracting `V_T(ρ)` from an observed descent rate at height will
overstate downward air motion.  The 0.4 exponent is prescribed, not measured — the settled
band spans too little density range to constrain it (a 5 % predicted signal against 27 %
between-flight scatter), and deeper bands are contaminated by the shedding remnant.

The two versions are not statistically separated: the mass ratio predicts v1 falls 12 %
faster, the observed ratio is 0.96 ± 0.16.

## Truth QC

Two neutral checks, applied per sounding:

1. `GPS altitude < -50 m` — a fill value (−100 m) appears in the data.
2. GPS rise speed inconsistent by more than 15 m/s with the rate implied by
   the surrounding GPS altitudes.  This catches the first velocity solution
   after acquisition, which the receiver reports as a large spurious value.

14 GPS values were rejected across the campaign.

## Known bad soundings — read before quoting mean-based numbers

A few soundings have GPS altitudes grossly inconsistent with their own
pressure record, and they dominate every mean-based statistic:

- **`2025-06-20_1923_15357`** — pressure sits at ~88.5 kPa and barely moves
  while GPS reports a 13-18 m/s climb through 3 km.  Drives the 10,841 m
  maximum error, and drives the wide v2026 interquartile band aloft.
- **`2025-05-25_2001_15281`** — GPS stops at 9 km while the sonde reaches
  13.4 km; 24 % of its fixes disagree with the pressure tendency.
- **`2025-05-18_2308_12051`** — new altitude is negative (−116 m) while GPS
  reports 18-676 m.

These are **not** filtered out: rejecting rows because a retrieval disagrees
with GPS would bias the comparison. They are reported instead, and the
median-based statistics are robust to them.

## Figure conventions

Plots label the two products by software version: **v2026** is the new Sparv
retrieval, **v2025** the original.  Colour roles are consistent across every
panel: **blue = v2026**, **orange = v2025**.  GPS truth is a reference rather than a categorical series, so it is drawn in
neutral ink.

Both profiles bin the data, and each sounding contributes its own median error
per bin so that a few long soundings cannot dominate a bin; the line is then
the median across soundings and the band the interquartile range.  Small grey
numbers give the soundings per bin, and bins holding fewer than 5 soundings are
not drawn.  Sample size falls off sharply with height — about 40 soundings
below 2 km, 11 at 12.5 km — which is why the v2026 interquartile band widens
aloft.
