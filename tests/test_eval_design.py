from scripts.eval_design import (
    PRIMARY_CROSS_ANIMAL_ARMS,
    arm_flags,
    build_session_vocab,
    output_query_session_id,
    split_recordings_by_subject,
)


def test_animal_split_holds_out_entire_subjects():
    subject_by_rid = {
        "rec-a": "mouse-1",
        "rec-b": "mouse-1",
        "rec-c": "mouse-2",
        "rec-d": "mouse-3",
    }

    split = split_recordings_by_subject(subject_by_rid, holdout=["mouse-1"])

    assert split.train_rids == ["rec-c", "rec-d"]
    assert split.eval_rids == ["rec-a", "rec-b"]
    assert split.holdout_subjects == ["mouse-1"]
    assert set(split.train_subjects).isdisjoint(split.eval_subjects)


def test_default_animal_split_is_deterministic_last_two_subjects():
    subject_by_rid = {
        "rec-a": "mouse-b",
        "rec-b": "mouse-a",
        "rec-c": "mouse-d",
        "rec-d": "mouse-c",
    }

    split = split_recordings_by_subject(subject_by_rid, holdout=None)

    assert split.holdout_subjects == ["mouse-c", "mouse-d"]
    assert split.train_rids == ["rec-a", "rec-b"]
    assert split.eval_rids == ["rec-c", "rec-d"]


def test_default_animal_split_keeps_training_subject_when_only_two_subjects():
    subject_by_rid = {
        "rec-a": "mouse-a",
        "rec-b": "mouse-b",
        "rec-c": "mouse-b",
    }

    split = split_recordings_by_subject(subject_by_rid, holdout=None)

    assert split.holdout_subjects == ["mouse-b"]
    assert split.train_rids == ["rec-a"]
    assert split.eval_rids == ["rec-b", "rec-c"]
    assert set(split.train_subjects).isdisjoint(split.eval_subjects)


def test_shared_output_query_uses_trainable_task_token_for_every_recording():
    assert output_query_session_id("rec-a", mode="shared") == "choice_readout"
    assert output_query_session_id("held-out-rec", mode="shared") == "choice_readout"


def test_session_output_query_preserves_recording_id_for_diagnostics():
    assert output_query_session_id("rec-a", mode="session") == "rec-a"


def test_session_vocab_includes_shared_query_token_once():
    vocab = build_session_vocab(["rec-a", "rec-b"], output_query_mode="shared")

    assert vocab == ["rec-a", "rec-b", "choice_readout"]


def test_primary_cross_animal_arms_do_not_depend_on_unit_identity():
    for arm in PRIMARY_CROSS_ANIMAL_ARMS:
        flags = arm_flags(arm)
        assert flags["use_unit_emb"] is False
        assert any(
            flags[name]
            for name in ("use_region_emb", "use_cell_type_emb", "use_waveform_emb")
        )
