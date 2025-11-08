from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.database import models as db_models
from app.models.claim import Claim, Patient, Provider, ProcedureCode
from app.models.validation import ValidationIssue, IssueSeverity
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/chat", tags=["chat"])


class QuestionRequest(BaseModel):
    claim_id: str
    question: str


class QuestionResponse(BaseModel):
    claim_id: str
    question: str
    answer: str


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    """Ask a question about a specific claim's validation results"""

    # Fetch claim from database
    db_claim = db.query(db_models.Claim).filter(
        db_models.Claim.claim_id == request.claim_id
    ).first()

    if not db_claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Fetch validation issues
    db_issues = db.query(db_models.ValidationResult).filter(
        db_models.ValidationResult.claim_id == request.claim_id
    ).all()

    # Reconstruct Claim object
    claim = Claim(
        claim_id=db_claim.claim_id,
        patient=Patient(**db_claim.patient_data),
        provider=Provider(**db_claim.provider_data),
        service_date=db_claim.service_date,
        diagnosis_codes=db_claim.diagnosis_codes,
        procedure_codes=[ProcedureCode(**p) for p in db_claim.procedure_codes],
        total_charge=db_claim.total_charge
    )

    # Reconstruct ValidationIssue objects
    issues = [
        ValidationIssue(
            agent_name=issue.agent_name,
            issue_type=issue.issue_type,
            severity=IssueSeverity(issue.severity),
            description=issue.description,
            explanation=issue.explanation or "",
            confidence_score=issue.confidence_score,
            cost_impact=issue.cost_impact,
            suggested_fix=issue.suggested_fix
        )
        for issue in db_issues
    ]

    # Get answer from LLM
    llm_service = LLMService()
    answer = llm_service.answer_question(request.question, claim, issues)

    return QuestionResponse(
        claim_id=request.claim_id,
        question=request.question,
        answer=answer
    )
