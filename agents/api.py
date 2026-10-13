"""
FastAPI REST API Server for Insulin Infusion Dka Agent.
"""
import os
import hmac
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

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


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: Optional[str] = Header(default=None)):
    expected = os.getenv("AUDIT_LOG_READ_TOKEN")
    if not expected or not x_audit_token or not hmac.compare_digest(x_audit_token, expected):
        raise HTTPException(status_code=403, detail="Audit log access is disabled or unauthorized")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
