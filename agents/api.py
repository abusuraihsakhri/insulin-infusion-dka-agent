"""
FastAPI REST API Server for Insulin Infusion Dka Agent.
"""
import os
import hmac
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, ConfigDict
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from insulin_infusion_dka_agent.dka_monitor import evaluate_adult_dka_labs

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Insulin Infusion Dka Agent API",
    description="Generic laboratory metric audit demonstration. Not a validated DKA treatment or dosing system.",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "UP", "service": "insulin-infusion-dka-agent", "clinical_validation": False, "version": "3.0.0"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "audit_integrity_verified": AuditLogger.verify_integrity()
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        PHIGuard.assert_no_phi(payload.model_dump_json())
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Possible identifier in submitted payload. Use synthetic data only.") from None
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Possible identifier in query. Use synthetic data only.") from None


class DKALabRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    glucose_mg_dl: float
    potassium_mmol_l: float
    beta_hydroxybutyrate_mmol_l: float
    venous_ph: float
    bicarbonate_mmol_l: float
    previous_glucose_mg_dl: Optional[float] = None
    hours_between_measurements: Optional[float] = None


@app.post("/api/dka-monitor")
def api_dka_monitor(payload: DKALabRequest):
    """Research-only adult DKA laboratory flagging; never medication dosing."""
    try:
        return evaluate_adult_dka_labs(**payload.model_dump()).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: Optional[str] = Header(default=None)):
    expected = os.getenv("AUDIT_LOG_READ_TOKEN")
    if not expected or not x_audit_token or not hmac.compare_digest(x_audit_token, expected):
        raise HTTPException(status_code=403, detail="Audit log access is disabled or unauthorized")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
