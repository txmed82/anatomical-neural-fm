from __future__ import annotations

from scripts.runpod_first_a100 import wait_for_s3_volume


def test_wait_for_s3_volume_accepts_immediately_ready_client(monkeypatch) -> None:
    calls = []

    class FakeClient:
        def list_objects_v2(self, **kwargs):
            calls.append(kwargs)
            return {"Contents": []}

    monkeypatch.setattr("scripts.runpod_first_a100.boto3.client", lambda *args, **kwargs: FakeClient())

    wait_for_s3_volume("vol123", "US-MO-1", "access", "secret", timeout_seconds=1)

    assert calls == [{"Bucket": "vol123", "MaxKeys": 1}]
