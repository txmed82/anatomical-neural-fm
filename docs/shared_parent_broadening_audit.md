# Shared-Parent Broadening Audit

## Result

The completed two-holdout broadening run is directionally positive but weak.

| holdout | true region delta | shuffled region delta | true positive seeds | shuffled positive seeds |
|---|---:|---:|---:|---:|
| `CSH_ZAD_019` | +0.038 | -0.012 | 3/3 | 1/3 |
| `KS014` | +0.022 | -0.008 | 2/3 | 1/3 |
| `MFD_06` | +0.010 | -0.003 | 2/3 | 1/3 |

The broadening result does not reproduce the CSH_ZAD_019 effect size. It does
preserve the expected ordering: true parent-region labels beat shuffled
parent-region labels for both added holdouts.

## Split Diagnostics

| holdout | shared parent regions | train trials | eval trials | eval balance |
|---|---:|---:|---:|---|
| `CSH_ZAD_019` | 21 | 13015 | 2726 | `{'L': 1504, 'R': 1222}` |
| `KS014` | 17 | 13614 | 2127 | `{'L': 1064, 'R': 1063}` |
| `MFD_06` | 23 | 13476 | 2265 | `{'L': 1221, 'R': 1044}` |

The weak holdouts are not obviously underpowered by trial count or class
balance. The more likely issue is anatomical support composition.

Only five parent regions are common to all three shared-parent splits:
`BS`, `MBmot`, `cc`, `root`, and `void`.

Pairwise overlap:

| pair | overlap | first-only parent regions | second-only parent regions |
|---|---:|---|---|
| `CSH_ZAD_019` vs `KS014` | 9 | `CA`, `DG`, `IB`, `LAT`, `LZ`, `MOp`, `VENT`, `VL`, `VP`, `VS`, `fxs`, `mfbc` | `IIn`, `RHP`, `RSPv`, `SCm`, `VISp`, `VISpm`, `cett`, `fiber tracts` |
| `CSH_ZAD_019` vs `MFD_06` | 10 | `IB`, `LZ`, `MOp`, `PRT`, `RSPagl`, `RSPd`, `VENT`, `VL`, `VS`, `hc`, `mfbc` | `ENTm`, `HB`, `IIn`, `LGd`, `MBsta`, `P-mot`, `P-sen`, `RHP`, `SCm`, `VISp`, `cVIIIn`, `lfbst`, `scp` |
| `KS014` vs `MFD_06` | 9 | `PRT`, `RSPagl`, `RSPd`, `RSPv`, `VISpm`, `cett`, `fiber tracts`, `hc` | `CA`, `DG`, `ENTm`, `HB`, `LAT`, `LGd`, `MBsta`, `P-mot`, `P-sen`, `VP`, `cVIIIn`, `fxs`, `lfbst`, `scp` |

## Next No-Spend Step

Do not spend on another broadening sweep until the parent-region support
question is resolved. The next analysis should score per-parent-region unit
support and per-region stimulus-side signal for `CSH_ZAD_019`, `KS014`, and
`MFD_06`, then test whether the CSH_ZAD_019 lift is concentrated in parent
regions missing or weakly represented in the broadening holdouts.
