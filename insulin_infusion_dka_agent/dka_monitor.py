"""Adult DKA laboratory monitoring worksheet (research/education only).

No infusion pump control, medication order, patient management, or diagnostic
authorization is provided. Rules are transcribed from the 2024 international
consensus on hyperglycemic crises in adults (DOI: 10.2337/dci24-0032).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Optional


@dataclass(frozen=True)
class DKAMonitorResult:
    """Descriptive laboratory flags, not a treatment plan."""

    glucose_change_mg_dl_per_hour: Optional[float]
    glucose_below_200_mg_dl: bool
    beta_hydroxybutyrate_below_0_6_mmol_l: bool
    acid_base_criterion_met: bool
    biochemical_resolution_criteria_met: bool
    low_potassium_safety_flag: bool
    potassium_status: str
    caution: str = (
        "Educational adult DKA laboratory interpretation only; no diagnosis, "
        "insulin rate, potassium dose, or treatment decision is provided."
    )

    def to_dict(self) -> dict:
        return asdict(self)


def _measurement(name: str, value: float, minimum: float, maximum: float) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite numeric measurement")
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite numeric measurement") from exc
    if not isfinite(result) or not minimum <= result <= maximum:
        raise ValueError(f"{name} must be finite and within [{minimum}, {maximum}]")
    return result


def evaluate_adult_dka_labs(
    *,
    glucose_mg_dl: float,
    potassium_mmol_l: float,
    beta_hydroxybutyrate_mmol_l: float,
    venous_ph: float,
    bicarbonate_mmol_l: float,
    previous_glucose_mg_dl: Optional[float] = None,
    hours_between_measurements: Optional[float] = None,
) -> DKAMonitorResult:
    """Assess 2024 consensus biochemical DKA resolution, with a potassium flag.

    The cutoff for biochemical DKA resolution is beta-hydroxybutyrate <0.6
    mmol/L AND (venous pH >=7.3 OR bicarbonate >=18 mmol/L). Glucose <200
    mg/dL is an additional desirable marker, not a mandatory resolution test.
    Serum potassium <3.5 mmol/L warrants a safety flag. No dose is calculated.
    """
    glucose = _measurement("glucose_mg_dl", glucose_mg_dl, 0, 2000)
    potassium = _measurement("potassium_mmol_l", potassium_mmol_l, 0, 15)
    ketones = _measurement("beta_hydroxybutyrate_mmol_l", beta_hydroxybutyrate_mmol_l, 0, 30)
    ph = _measurement("venous_ph", venous_ph, 6, 8)
    bicarbonate = _measurement("bicarbonate_mmol_l", bicarbonate_mmol_l, 0, 60)

    if (previous_glucose_mg_dl is None) != (hours_between_measurements is None):
        raise ValueError("Previous glucose and time interval must be provided together")

    rate = None
    if previous_glucose_mg_dl is not None:
        previous = _measurement("previous_glucose_mg_dl", previous_glucose_mg_dl, 0, 2000)
        hours = _measurement("hours_between_measurements", hours_between_measurements, 0, 168)
        if hours == 0:
            raise ValueError("Time interval must be greater than zero")
        rate = (previous - glucose) / hours

    acid_base_met = ph >= 7.3 or bicarbonate >= 18
    low_potassium = potassium < 3.5
    return DKAMonitorResult(
        glucose_change_mg_dl_per_hour=rate,
        glucose_below_200_mg_dl=glucose < 200,
        beta_hydroxybutyrate_below_0_6_mmol_l=ketones < 0.6,
        acid_base_criterion_met=acid_base_met,
        biochemical_resolution_criteria_met=ketones < 0.6 and acid_base_met,
        low_potassium_safety_flag=low_potassium,
        potassium_status=(
            "LOW—requires clinician review before insulin treatment"
            if low_potassium else
            "ABOVE 5.0—monitor potassium and clinician guidance"
            if potassium > 5.0 else
            "3.5–5.0—continue clinician-directed monitoring"
        ),
    )
