from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.claim import Claim
from app.models.validation import ValidationResult
from app.database.connection import get_db
from app.database import models as db_models
from app.agents.orchestrator import ClaimValidationOrchestrator
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.post("/validate", response_model=ValidationResult)
async def validate_claim(claim: Claim, db: Session = Depends(get_db)):
    """Validate a single medical claim"""

    llm_service = LLMService()
    orchestrator = ClaimValidationOrchestrator(db, llm_service)

    try:
        # Run validation
        result = orchestrator.validate_claim(claim)

        # Save to database
        _save_claim_to_db(db, claim, result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/batch-validate")
async def batch_validate_claims(claims: List[Claim], db: Session = Depends(get_db)):
    """Validate multiple claims in batch"""

    llm_service = LLMService()
    orchestrator = ClaimValidationOrchestrator(db, llm_service)

    results = []
    failed = []

    for claim in claims:
        try:
            result = orchestrator.validate_claim(claim)
            _save_claim_to_db(db, claim, result)
            results.append({
                "claim_id": claim.claim_id,
                "status": "success",
                "result": result
            })
        except Exception as e:
            failed.append({
                "claim_id": claim.claim_id,
                "status": "failed",
                "error": str(e)
            })

    return {
        "total": len(claims),
        "successful": len(results),
        "failed": len(failed),
        "results": results,
        "errors": failed
    }


@router.get("/{claim_id}", response_model=dict)
async def get_claim(claim_id: str, db: Session = Depends(get_db)):
    """Get claim and validation results by ID"""

    # Get claim from database
    db_claim = db.query(db_models.Claim).filter(
        db_models.Claim.claim_id == claim_id
    ).first()

    if not db_claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Get validation results
    validation_issues = db.query(db_models.ValidationResult).filter(
        db_models.ValidationResult.claim_id == claim_id
    ).all()

    return {
        "claim": {
            "claim_id": db_claim.claim_id,
            "patient": db_claim.patient_data,
            "provider": db_claim.provider_data,
            "service_date": db_claim.service_date,
            "diagnosis_codes": db_claim.diagnosis_codes,
            "procedure_codes": db_claim.procedure_codes,
            "total_charge": db_claim.total_charge,
            "validation_status": db_claim.validation_status,
            "created_at": db_claim.created_at
        },
        "validation_issues": [
            {
                "agent_name": issue.agent_name,
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "description": issue.description,
                "explanation": issue.explanation,
                "confidence_score": issue.confidence_score,
                "cost_impact": issue.cost_impact,
                "suggested_fix": issue.suggested_fix
            }
            for issue in validation_issues
        ]
    }


@router.get("/")
async def list_claims(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    db: Session = Depends(get_db)
):
    """List all claims with optional filtering"""

    query = db.query(db_models.Claim)

    if status:
        query = query.filter(db_models.Claim.validation_status == status)

    total = query.count()
    claims = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "claims": [
            {
                "claim_id": c.claim_id,
                "service_date": c.service_date,
                "total_charge": c.total_charge,
                "validation_status": c.validation_status,
                "created_at": c.created_at
            }
            for c in claims
        ]
    }


def _save_claim_to_db(db: Session, claim: Claim, result: ValidationResult):
    """Helper to save claim and validation results to database"""

    # Save claim
    db_claim = db_models.Claim(
        claim_id=claim.claim_id,
        patient_data=claim.patient.model_dump(mode='json'),
        provider_data=claim.provider.model_dump(mode='json'),
        service_date=claim.service_date,
        diagnosis_codes=claim.diagnosis_codes,
        procedure_codes=[p.model_dump(mode='json') for p in claim.procedure_codes],
        total_charge=claim.total_charge,
        validation_status=result.overall_status
    )

    # Merge (update if exists, insert if new)
    db.merge(db_claim)

    # Delete old validation results for this claim
    db.query(db_models.ValidationResult).filter(
        db_models.ValidationResult.claim_id == claim.claim_id
    ).delete()

    # Save validation issues
    for issue in result.issues:
        db_issue = db_models.ValidationResult(
            claim_id=claim.claim_id,
            agent_name=issue.agent_name,
            issue_type=issue.issue_type,
            severity=issue.severity.value,
            description=issue.description,
            explanation=issue.explanation,
            confidence_score=issue.confidence_score,
            cost_impact=issue.cost_impact,
            suggested_fix=issue.suggested_fix
        )
        db.add(db_issue)

    db.commit()
