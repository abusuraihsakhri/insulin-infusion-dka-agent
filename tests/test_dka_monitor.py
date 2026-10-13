"""Regression tests for research-only adult DKA monitoring rules."""
import math
import pytest

from insulin_infusion_dka_agent.dka_monitor import evaluate_adult_dka_labs


def sample(**overrides):
    values = dict(
        glucose_mg_dl=190, potassium_mmol_l=4.0,
        beta_hydroxybutyrate_mmol_l=0.5, venous_ph=7.31,
        bicarbonate_mmol_l=17.0,
    )
    values.update(overrides)
    return evaluate_adult_dka_labs(**values)


def test_resolution_requires_ketones_and_either_acid_base_measurement():
    assert sample().biochemical_resolution_criteria_met
    assert sample(venous_ph=7.2, bicarbonate_mmol_l=18).biochemical_resolution_criteria_met
    assert not sample(beta_hydroxybutyrate_mmol_l=0.6).biochemical_resolution_criteria_met
    assert not sample(venous_ph=7.29, bicarbonate_mmol_l=17.99).biochemical_resolution_criteria_met


def test_glucose_alone_is_not_a_resolution_criterion():
    assert sample(glucose_mg_dl=300).biochemical_resolution_criteria_met
    assert not sample(glucose_mg_dl=99, beta_hydroxybutyrate_mmol_l=4).biochemical_resolution_criteria_met


def test_potassium_warning_boundary():
    assert sample(potassium_mmol_l=3.49).low_potassium_safety_flag
    assert not sample(potassium_mmol_l=3.5).low_potassium_safety_flag
    assert not sample(potassium_mmol_l=5.5).low_potassium_safety_flag


def test_glucose_velocity_preserves_sign_and_time():
    result = sample(glucose_mg_dl=200, previous_glucose_mg_dl=310, hours_between_measurements=2)
    assert result.glucose_change_mg_dl_per_hour == 55
    result = sample(glucose_mg_dl=310, previous_glucose_mg_dl=200, hours_between_measurements=2)
    assert result.glucose_change_mg_dl_per_hour == -55
    assert sample().glucose_change_mg_dl_per_hour is None


@pytest.mark.parametrize("changes", [
    {"glucose_mg_dl": float("nan")},
    {"potassium_mmol_l": float("inf")},
    {"venous_ph": -3},
    {"beta_hydroxybutyrate_mmol_l": -1},
    {"previous_glucose_mg_dl": 300},
    {"hours_between_measurements": 1},
    {"previous_glucose_mg_dl": 300, "hours_between_measurements": 0},
    {"previous_glucose_mg_dl": 300, "hours_between_measurements": float("nan")},
    {"glucose_mg_dl": True},
])
def test_bad_inputs_rejected(changes):
    with pytest.raises(ValueError):
        sample(**changes)
