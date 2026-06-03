from scripts.write_dataset_manifest import summarize_recordings


class Obj:
    def __init__(self, **values):
        self.__dict__.update(values)


def test_summarize_recordings_counts_trials_units_regions_and_classes():
    recs = {
        "rec-a_probe00": Obj(
            session=Obj(id="rec-a"),
            subject=Obj(id="mouse-1"),
            units=Obj(region_acronym=["CA1", "CA1", "LP"]),
            trials=Obj(choice=[-1, 1, 0, 1]),
        ),
        "rec-b_probe01": Obj(
            session=Obj(id="rec-b"),
            subject=Obj(id="mouse-2"),
            units=Obj(region_acronym=["DG"]),
            trials=Obj(choice=[-1, -1]),
        ),
    }

    manifest = summarize_recordings(recs)

    assert manifest["n_recordings"] == 2
    assert manifest["n_subjects"] == 2
    assert manifest["n_units"] == 4
    assert manifest["n_trials"] == 6
    assert manifest["recordings"][0] == {
        "recording_id": "rec-a_probe00",
        "session_id": "rec-a",
        "subject_id": "mouse-1",
        "n_units": 3,
        "n_regions": 2,
        "n_trials": 4,
        "choice_counts": {"left": 1, "right": 2, "nogo": 1},
    }
