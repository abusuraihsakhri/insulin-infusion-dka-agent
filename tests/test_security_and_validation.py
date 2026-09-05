"""
Security and input validation tests for Insulin Infusion Dka Agent.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, assert_no_phi
from agents.models import SystemTaskPayload, UrgencyLevel


class TestPHIGuard:
    """Test PHI detection and redaction."""

    def test_ssn_detected(self):
        with pytest.raises(SecurityException):
            assert_no_phi("Patient SSN: 123-45-6789")

    def test_mrn_detected(self):
        with pytest.raises(SecurityException):
            assert_no_phi("MRN-12345678 clinical note")

    def test_phone_detected(self):
        with pytest.raises(SecurityException):
            assert_no_phi("Call patient at 555-123-4567")

    def test_email_detected(self):
        with pytest.raises(SecurityException):
            assert_no_phi("Email: patient@example.com")

    def test_clean_text_passes(self):
        assert_no_phi("Specimen KEY-001 analytical result optimal") is None

    def test_empty_text_passes(self):
        assert_no_phi("") is None

    def test_none_text_passes(self):
        assert_no_phi(None) is None

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678 needs follow-up")
        assert "MRN-12345678" not in result
        assert "[REDACTED_IDENTIFIER]" in result


class TestInputValidation:
    """Test metric input validation."""

    def test_nan_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("nan"),
            )

    def test_inf_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("inf"),
            )

    def test_negative_inf_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("-inf"),
            )

    def test_valid_metrics_accepted(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=25.5,
            secondary_metric=10.0,
        )
        assert payload.primary_metric == 25.5
        assert payload.secondary_metric == 10.0

    def test_zero_metrics_accepted(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=0.0,
            secondary_metric=0.0,
        )
        assert payload.primary_metric == 0.0

    def test_negative_metrics_accepted(self):
        """Negative values are valid finite numbers."""
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=-5.0,
        )
        assert payload.primary_metric == -5.0

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="",
                target_identifier="KEY-01",
                primary_metric=10.0,
            )


class TestAuditIntegrity:
    """Test HMAC audit trail integrity."""

    def test_audit_trail_verifies(self):
        from agents.base import AuditTrail
        trail = AuditTrail(secret_key="test-key-for-verification")
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value1"})
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value2"})
        assert trail.verify_integrity() is True

    def test_audit_trail_detects_tampering(self):
        from agents.base import AuditTrail
        trail = AuditTrail(secret_key="test-key-for-verification")
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value1"})
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value2"})
        # Tamper with the first entry
        if trail.logs:
            trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False

    def test_audit_log_contains_phi_raises(self):
        from agents.base import AuditTrail
        trail = AuditTrail(secret_key="test-key-for-verification")
        with pytest.raises(SecurityException):
            trail.log("actor", "tier", "EVENT", {"note": "Patient MRN-12345678"})
