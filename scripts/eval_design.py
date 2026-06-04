"""Pure experiment-design helpers for local tests and training orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


OutputQueryMode = Literal["shared", "session"]

SHARED_CHOICE_READOUT_ID = "choice_readout"

# These are the primary cross-animal arms because their input tokens do not
# depend on arbitrary held-out unit-id embeddings.
PRIMARY_CROSS_ANIMAL_ARMS = ("shared_baseline", "pure_anatomy", "waveform_only")


@dataclass(frozen=True)
class AnimalSplit:
    train_rids: list[str]
    eval_rids: list[str]
    holdout_subjects: list[str]
    train_subjects: list[str]
    eval_subjects: list[str]


def arm_flags(arm: str) -> dict[str, bool]:
    base = {
        "use_unit_emb": False,
        "use_region_emb": False,
        "use_cell_type_emb": False,
        "use_waveform_emb": False,
    }
    flags_by_arm = {
        "baseline": {"use_unit_emb": True},
        "shared_baseline": {},
        "region": {"use_unit_emb": True, "use_region_emb": True},
        "cell_type": {"use_unit_emb": True, "use_cell_type_emb": True},
        "region_ctype": {
            "use_unit_emb": True,
            "use_region_emb": True,
            "use_cell_type_emb": True,
        },
        "pure_anatomy": {"use_region_emb": True, "use_cell_type_emb": True},
        "waveform": {"use_unit_emb": True, "use_waveform_emb": True},
        "waveform_only": {"use_waveform_emb": True},
    }
    if arm not in flags_by_arm:
        raise ValueError(f"unknown arm {arm!r}; expected one of {sorted(flags_by_arm)}")
    base.update(flags_by_arm[arm])
    return base


def split_recordings_by_subject(
    subject_by_rid: dict[str, str],
    holdout: list[str] | None,
) -> AnimalSplit:
    subjects = sorted(set(subject_by_rid.values()))
    if holdout is None:
        holdout = subjects[-2:] if len(subjects) >= 3 else subjects[-1:]
    holdout_set = set(holdout)
    train_rids = [rid for rid, subject in subject_by_rid.items() if subject not in holdout_set]
    eval_rids = [rid for rid, subject in subject_by_rid.items() if subject in holdout_set]
    train_subjects = sorted({subject_by_rid[rid] for rid in train_rids})
    eval_subjects = sorted({subject_by_rid[rid] for rid in eval_rids})
    return AnimalSplit(
        train_rids=train_rids,
        eval_rids=eval_rids,
        holdout_subjects=list(holdout),
        train_subjects=train_subjects,
        eval_subjects=eval_subjects,
    )


def output_query_session_id(recording_id: str, mode: OutputQueryMode) -> str:
    if mode == "shared":
        return SHARED_CHOICE_READOUT_ID
    if mode == "session":
        return recording_id
    raise ValueError(f"unknown output query mode {mode!r}")


def build_session_vocab(
    recording_ids: list[str],
    output_query_mode: OutputQueryMode,
) -> list[str]:
    session_ids = list(recording_ids)
    if output_query_mode == "shared" and SHARED_CHOICE_READOUT_ID not in session_ids:
        session_ids.append(SHARED_CHOICE_READOUT_ID)
    elif output_query_mode != "session":
        raise ValueError(f"unknown output query mode {output_query_mode!r}")
    return session_ids
