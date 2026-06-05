# CSH Model-Free Region-Family Candidate Scan

Predefined parent-region family aggregates scanned as model-free ridge features against within-recording shuffled labels and total-spike baseline.

Holdout: `CSH_ZAD_019`
Families scanned: `11`
Candidates: `0`

| family | outcome | eval_centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero | members |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| basal_ganglia | reject: target1 | 0.607 | +0.100 | +0.157 | 1.000 | 0.000 | 1/4 | 0.499 | CNU, PALc, STRd, STRv, VS |
| brainstem_interbrain | reject: target0 | 0.572 | +0.035 | +0.122 | 0.036 | 0.972 | 1/4 | 0.501 | BS, HB, IB, LZ, ZI |
| cortical_retrosplenial | reject: target1 | 0.548 | +0.015 | +0.098 | 0.890 | 0.146 | 1/4 | 0.567 | RSPagl, RSPd, RSPv |
| hippocampal_formation | reject: target0 | 0.582 | +0.010 | +0.132 | 0.305 | 0.709 | 2/4 | 0.784 | CA, DG, ENTm, HIP, RHP |
| cortical_sensorimotor | reject: shuffle | 0.587 | +0.008 | +0.137 | 0.701 | 0.282 | 1/4 | 0.433 | MOp, MOs, SSp-bfd, SSp-ll, SSp-tr, SSp-ul, SSp-un, SSs |
| broad_named_anatomy | reject: shuffle | 0.451 | +0.003 | +0.001 | 0.698 | 0.362 | 2/4 | 1.000 | ATN, AUDd, AUDv, BS, CA, CNU, CTXpl, CTXsp, DG, DORpm, ENTm, EPI, FRP, HB, HIP, IB, LAT, LGd, LS, LZ, MBmot, MBsen, MBsta, MED, MG, MOp, MOs, MSC, OLF, ORBm, ORBvl, PALc, PRT, PVR, RHP, RSPagl, RSPd, RSPv, SCm, SCs, SSp-bfd, SSp-ll, SSp-tr, SSp-ul, SSp-un, SSs, STRd, STRv, VENT, VISa, VISp, VISpl, VISpm, VISpor, VL, VP, VS, ZI |
| fiber_tracts | reject: shuffle | 0.551 | +0.002 | +0.101 | 0.507 | 0.481 | 1/4 | 1.000 | cc, cett, eps, epsc, fa, fiber tracts, fxs, hc, lfbst, mfbc, mfbse, scp |
| thalamic | reject: shuffle | 0.530 | -0.017 | +0.080 | 0.381 | 0.581 | 0/4 | 1.000 | ATN, DORpm, LAT, LGd, MED, MG, PRT, VENT, VL, VP |
| midbrain | reject: shuffle | 0.438 | -0.230 | -0.012 | 0.828 | 0.216 | 1/4 | 0.285 | MBmot, MBsen, MBsta, SCm, SCs, P-mot, P-sen |
| cortical_visual | reject: absent in eval | 0.704 | +0.315 | +0.254 | 0.000 | 1.000 | 0/4 | 0.000 | VISa, VISp, VISpl, VISpm, VISpor |
| cortical_auditory | reject: absent in eval | 0.644 | +0.000 | +0.194 | 1.000 | 0.000 | 0/4 | 0.000 | AUDd, AUDv |

Decision:

No predefined region family passed the model-free promotion gate. The next no-spend branch should test an alternative conserved target or a larger matched-region manifest audit, not another GPU model run.
