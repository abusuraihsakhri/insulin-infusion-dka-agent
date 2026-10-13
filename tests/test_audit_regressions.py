"""Security and API regression tests for the audit changes."""
import copy
import os

import pytest
from fastapi.testclient import TestClient

from agents.base import AuditTrail, SecurityException
from agents.api import app


def test_audit_signature_is_recomputed_for_each_entry():
    trail = AuditTrail(secret_key="a-fixture-secret")
    trail.log("worker", "service", "EVALUATED", {"status": "ok"})
    trail.log("worker", "service", "EVALUATED", {"status": "ok"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "MODIFIED"
    assert not trail.verify_integrity()


def test_audit_forgery_with_consistent_links_is_rejected():
    trail = AuditTrail(secret_key="a-fixture-secret")
    trail.log("worker", "service", "EVALUATED", {"status": "ok"})
    trail.logs[0]["current_hash"] = "a" * 64
    assert not trail.verify_integrity()


def test_audit_log_accessor_returns_defensive_copy():
    trail = AuditTrail(secret_key="a-fixture-secret")
    trail.log("worker", "service", "EVALUATED", {"status": "ok"})
    result = trail.get_trail()
    result[0]["actor"] = "malicious"
    assert trail.verify_integrity()
    assert trail.get_trail()[0]["actor"] == "worker"


def test_predictable_secret_rejected():
    with pytest.raises(ValueError, match="placeholder"):
        AuditTrail(secret_key="change-me-in-production")


def test_actor_identifiers_are_screened():
    trail = AuditTrail(secret_key="a-fixture-secret")
    with pytest.raises(SecurityException):
        trail.log("MRN-123456", "service", "EVALUATED", {"status": "ok"})


def test_log_endpoint_disabled_by_default(monkeypatch):
    monkeypatch.delenv("AUDIT_LOG_READ_TOKEN", raising=False)
    client = TestClient(app)
    assert client.get("/api/audit/logs").status_code == 403


def test_log_endpoint_needs_matching_token(monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_READ_TOKEN", "a-test-only-token")
    client = TestClient(app)
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "invalid"}).status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "a-test-only-token"}).status_code == 200


def test_nested_phi_is_rejected_by_api():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "T-01", "target_identifier": "SAFE-1", "primary_metric": 4.0,
        "attributes": {"note": "MRN-12345678"},
    })
    assert response.status_code == 422


def test_dka_monitor_endpoint_and_invalid_inputs():
    client = TestClient(app)
    values = {
        "glucose_mg_dl": 190, "potassium_mmol_l": 4,
        "beta_hydroxybutyrate_mmol_l": 0.5, "venous_ph": 7.31,
        "bicarbonate_mmol_l": 17,
    }
    r = client.post("/api/dka-monitor", json=values)
    assert r.status_code == 200, r.text
    assert r.json()["biochemical_resolution_criteria_met"] is True
    assert client.post("/api/dka-monitor", json={**values, "potassium_mmol_l": -2}).status_code == 422
    assert client.post("/api/dka-monitor", json={**values, "patient_name": "identifiable"}).status_code == 422


def test_audit_signing_is_not_ambiguous_across_delimiters():
    trail = AuditTrail(secret_key="a-fixture-secret")
    trail.log("worker|tier", "service", "EVALUATED", {"status": "ok"})
    trail.logs[0]["actor"] = "worker"
    trail.logs[0]["actor_tier"] = "tier|service"
    assert not trail.verify_integrity()


def test_configured_short_key_rejected(monkeypatch):
    monkeypatch.setenv("AUDIT_SECRET_KEY", "short")
    with pytest.raises(ValueError, match="32 UTF-8"):
        AuditTrail()
