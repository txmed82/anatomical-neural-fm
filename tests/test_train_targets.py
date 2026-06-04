from __future__ import annotations

import numpy as np

from scripts.train import build_trial_samples


class Obj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_build_trial_samples_choice_skips_nogo_and_nan_stim() -> None:
    rec = Obj(
        trials=Obj(
            choice=np.array([-1, 1, 0, 1]),
            stim_on_times=np.array([0.1, 0.2, 0.3, np.nan]),
        ),
        domain=Obj(end=np.array([2.0])),
    )

    samples = build_trial_samples({"rec": rec}, ["rec"], window_len=1.0, target_mode="choice")

    assert samples == [("rec", 0.1, 0.0), ("rec", 0.2, 1.0)]


def test_build_trial_samples_stimulus_side_uses_contrast_not_choice() -> None:
    rec = Obj(
        trials=Obj(
            choice=np.array([1, -1, 1, -1]),
            contrast_left=np.array([1.0, 0.0, 0.25, np.nan]),
            contrast_right=np.array([0.0, 1.0, 0.25, 0.5]),
            stim_on_times=np.array([0.1, 0.2, 0.3, 0.4]),
        ),
        domain=Obj(end=np.array([2.0])),
    )

    samples = build_trial_samples(
        {"rec": rec},
        ["rec"],
        window_len=1.0,
        target_mode="stimulus_side",
    )

    assert samples == [("rec", 0.1, 0.0), ("rec", 0.2, 1.0), ("rec", 0.4, 1.0)]
