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

## Buoyancy and drag

From `w_air_ascent_wbuoy_method.ipynb`.  20 g balloon, 0.60 m launch diameter, in two payload versions
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

The observed ascent rate cannot be used due to contamination from vertical ascent in the inflow layer, so the w_buoy technique must be used. Ideally we need to measure the balloon bouyancy before launch.

## Detached-sonde fall speed

From `vt_detached.ipynb`, at a reference density ρ_ref = 1.041 kg/m³:

| | v1 (25 g) | v2 (20 g) |
|---|---|---|
| `V_T,ref` | 20.7 ± 2.8 m/s | 21.6 ± 2.2 m/s |
| cases contributing | 8 | 11 |
| spread between flights | ±6.4 m/s | ±5.7 m/s |

Applied as `V_T(ρ) = V_T,ng · (ρ_ng/ρ)^0.4`, this gives roughly 21 m/s near the ground
rising to about 40 m/s at ρ = 0.20.
The observed V_T is contaminated by ice accumulation and the downdraft and therefore the theortical technique must be used. Ideally we need to run test drops of the hailsonde under stable noctural conditions.