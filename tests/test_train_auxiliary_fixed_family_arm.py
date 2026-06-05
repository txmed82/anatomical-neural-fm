import torch
import torch.nn as nn

from scripts.train import model_logits_with_optional_auxiliary, split_model_batch


class FakeModel(nn.Module):
    def forward(self, input_unit_index, **kwargs):
        assert "fixed_family_feature" not in kwargs
        return input_unit_index.float().sum(dim=1, keepdim=True).unsqueeze(-1)


def test_split_model_batch_removes_auxiliary_feature_without_mutating_input() -> None:
    batch = {
        "input_unit_index": torch.tensor([[1, 2]]),
        "fixed_family_feature": torch.tensor([[3.0]]),
    }

    model_batch, fixed_family_feature = split_model_batch(batch)

    assert "fixed_family_feature" not in model_batch
    assert torch.equal(fixed_family_feature, torch.tensor([[3.0]]))
    assert "fixed_family_feature" in batch


def test_model_logits_adds_fixed_family_auxiliary_logit() -> None:
    model = FakeModel()
    auxiliary_head = nn.Linear(1, 1)
    with torch.no_grad():
        auxiliary_head.weight.fill_(2.0)
        auxiliary_head.bias.fill_(0.5)
    batch = {
        "input_unit_index": torch.tensor([[1, 2], [3, 4]]),
        "fixed_family_feature": torch.tensor([[5.0], [7.0]]),
    }

    logits = model_logits_with_optional_auxiliary(model, batch, auxiliary_head)

    assert logits.shape == (2, 1)
    assert torch.allclose(logits, torch.tensor([[13.5], [21.5]]))


def test_model_logits_requires_auxiliary_feature_when_head_is_present() -> None:
    model = FakeModel()
    auxiliary_head = nn.Linear(1, 1)

    try:
        model_logits_with_optional_auxiliary(
            model,
            {"input_unit_index": torch.tensor([[1, 2]])},
            auxiliary_head,
        )
    except ValueError as exc:
        assert "fixed_family_feature" in str(exc)
    else:
        raise AssertionError("expected missing auxiliary feature error")
