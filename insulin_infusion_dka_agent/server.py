"""
FastAPI REST Application & Webhooks for DKAGuard: Diabetic Ketoacidosis & HHS Insulin Infusion / Potassium Sentinel.
"""
from typing import Dict, Any, Optional
from agents.base import PHIGuard, SecurityException
from .models import ClinicalCasePayload
from .agents import DKAGuardCoordinator
from .dka_monitor import evaluate_adult_dka_labs

coordinator = DKAGuardCoordinator()

def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field

        app = FastAPI(
            title="DKAGuard: Diabetic Ketoacidosis & HHS Insulin Infusion / Potassium Sentinel",
            description="Legacy generic metric audit demonstration; does not implement treatment or dosing decisions.",
            version="2.0.0-PRO",
        )

        class AuditRequest(BaseModel):
            case_id: str = "CASE-2026-001"
            patient_synthetic_id: str = "SYNTH-PT-881"
            primary_metric: float = 24.5
            secondary_metric: float = 14.0
            status_flag: str = "DISCORDANT"
            is_stat: bool = True
            clinical_notes: str = ""
            biomarkers: Dict[str, Any] = Field(default_factory=dict)

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "insulin-infusion-dka-agent", "domain": "Endocrinology / ICU", "version": "2.0.0-PRO"}

        @app.post("/api/audit")
        def api_audit(req: AuditRequest):
            try:
                PHIGuard.assert_no_phi(req.model_dump_json())
            except SecurityException:
                from fastapi import HTTPException
                raise HTTPException(status_code=422, detail="Possible identifier detected. Use synthetic data only.") from None
            payload = ClinicalCasePayload(
                case_id=req.case_id,
                patient_synthetic_id=req.patient_synthetic_id,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_flag=req.status_flag,
                is_stat=req.is_stat,
                clinical_notes=req.clinical_notes,
                biomarkers=req.biomarkers,
            )
            return coordinator.process_case(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        class DKALabRequest(BaseModel):
            glucose_mg_dl: float
            potassium_mmol_l: float
            beta_hydroxybutyrate_mmol_l: float
            venous_ph: float
            bicarbonate_mmol_l: float
            previous_glucose_mg_dl: Optional[float] = None
            hours_between_measurements: Optional[float] = None

            model_config = {"extra": "forbid"}

        @app.post("/api/dka-monitor")
        def api_dka_monitor(req: DKALabRequest):
            from fastapi import HTTPException
            try:
                return evaluate_adult_dka_labs(**req.model_dump()).to_dict()
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from None

        return app
    except ImportError:
        return None
