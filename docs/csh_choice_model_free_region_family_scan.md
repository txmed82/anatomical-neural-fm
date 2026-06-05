# CSH Model-Free Region-Family Candidate Scan

Predefined parent-region family aggregates scanned as model-free ridge features against within-recording shuffled labels and total-spike baseline.

Holdout: `CSH_ZAD_019`
Families scanned: `11`
Candidates: `0`

| family | outcome | eval_centered_AUC | delta_vs_shuffle | delta_vs_total | target0 | target1 | recordings | eval_nonzero | members |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| brainstem_interbrain | reject: target1 | 0.506 | +0.114 | +0.115 | 0.933 | 0.055 | 1/4 | 0.499 | BS, HB, IB, LZ, ZI |
| cortical_sensorimotor | reject: target0 | 0.622 | +0.093 | +0.230 | 0.366 | 0.646 | 2/4 | 0.429 | MOp, MOs, SSp-bfd, SSp-ll, SSp-tr, SSp-ul, SSp-un, SSs |
| midbrain | reject: target1 | 0.620 | +0.031 | +0.229 | 0.947 | 0.076 | 1/4 | 0.284 | MBmot, MBsen, MBsta, SCm, SCs, P-mot, P-sen |
| fiber_tracts | reject: target1 | 0.610 | +0.021 | +0.219 | 0.713 | 0.254 | 2/4 | 1.000 | cc, cett, eps, epsc, fa, fiber tracts, fxs, hc, lfbst, mfbc, mfbse, scp |
| thalamic | reject: target1 | 0.420 | +0.016 | +0.029 | 0.767 | 0.257 | 4/4 | 1.000 | ATN, DORpm, LAT, LGd, MED, MG, PRT, VENT, VL, VP |
| broad_named_anatomy | reject: shuffle | 0.395 | +0.003 | +0.004 | 0.609 | 0.371 | 3/4 | 1.000 | ATN, AUDd, AUDv, BS, CA, CNU, CTXpl, CTXsp, DG, DORpm, ENTm, EPI, FRP, HB, HIP, IB, LAT, LGd, LS, LZ, MBmot, MBsen, MBsta, MED, MG, MOp, MOs, MSC, OLF, ORBm, ORBvl, PALc, PRT, PVR, RHP, RSPagl, RSPd, RSPv, SCm, SCs, SSp-bfd, SSp-ll, SSp-tr, SSp-ul, SSp-un, SSs, STRd, STRv, VENT, VISa, VISp, VISpl, VISpm, VISpor, VL, VP, VS, ZI |
| cortical_retrosplenial | reject: shuffle | 0.498 | -0.007 | +0.107 | 0.089 | 0.896 | 1/4 | 0.571 | RSPagl, RSPd, RSPv |
| hippocampal_formation | reject: shuffle | 0.605 | -0.023 | +0.213 | 0.517 | 0.517 | 1/4 | 0.785 | CA, DG, ENTm, HIP, RHP |
| basal_ganglia | reject: shuffle | 0.560 | -0.112 | +0.169 | 0.060 | 0.921 | 0/4 | 0.501 | CNU, PALc, STRd, STRv, VS |
| cortical_auditory | reject: absent in eval | 0.765 | +0.368 | +0.373 | 0.000 | 1.000 | 0/4 | 0.000 | AUDd, AUDv |
| cortical_visual | reject: absent in eval | 0.663 | +0.267 | +0.272 | 1.000 | 0.000 | 0/4 | 0.000 | VISa, VISp, VISpl, VISpm, VISpor |

Decision:

No predefined region family passed the model-free promotion gate. The next no-spend branch should test an alternative conserved target or a larger matched-region manifest audit, not another GPU model run.
