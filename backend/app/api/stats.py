from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.database import models as db_models

router = APIRouter(prefix="/api/stats", tags=["statistics"])


@router.get("/summary")
async def get_summary_stats(db: Session = Depends(get_db)):
    """Get overall validation statistics"""

    # Total claims
    total_claims = db.query(db_models.Claim).count()

    # Claims by status
    status_counts = db.query(
        db_models.Claim.validation_status,
        func.count(db_models.Claim.claim_id)
    ).group_by(db_models.Claim.validation_status).all()

    status_breakdown = {status: count for status, count in status_counts}

    # Total cost impact
    total_cost_impact = db.query(
        func.sum(db_models.ValidationResult.cost_impact)
    ).scalar() or 0.0

    # Issues by severity
    severity_counts = db.query(
        db_models.ValidationResult.severity,
        func.count(db_models.ValidationResult.id)
    ).group_by(db_models.ValidationResult.severity).all()

    severity_breakdown = {severity: count for severity, count in severity_counts}

    # Issues by type
    issue_type_counts = db.query(
        db_models.ValidationResult.issue_type,
        func.count(db_models.ValidationResult.id)
    ).group_by(db_models.ValidationResult.issue_type).all()

    top_issue_types = sorted(
        [(issue_type, count) for issue_type, count in issue_type_counts],
        key=lambda x: x[1],
        reverse=True
    )[:10]

    # Average issues per claim
    total_issues = db.query(db_models.ValidationResult).count()
    avg_issues_per_claim = total_issues / total_claims if total_claims > 0 else 0

    return {
        "total_claims": total_claims,
        "status_breakdown": status_breakdown,
        "total_cost_impact": round(total_cost_impact, 2),
        "severity_breakdown": severity_breakdown,
        "top_issue_types": [
            {"issue_type": it, "count": count}
            for it, count in top_issue_types
        ],
        "total_issues": total_issues,
        "avg_issues_per_claim": round(avg_issues_per_claim, 2)
    }


@router.get("/agents")
async def get_agent_stats(db: Session = Depends(get_db)):
    """Get statistics by validation agent"""

    agent_stats = db.query(
        db_models.ValidationResult.agent_name,
        func.count(db_models.ValidationResult.id).label('total_issues'),
        func.avg(db_models.ValidationResult.confidence_score).label('avg_confidence'),
        func.sum(db_models.ValidationResult.cost_impact).label('total_cost_impact')
    ).group_by(db_models.ValidationResult.agent_name).all()

    return {
        "agents": [
            {
                "agent_name": agent,
                "total_issues": total,
                "avg_confidence": round(avg_conf or 0, 2),
                "total_cost_impact": round(cost or 0, 2)
            }
            for agent, total, avg_conf, cost in agent_stats
        ]
    }


@router.get("/trends")
async def get_trends(db: Session = Depends(get_db)):
    """Get validation trends over time"""

    # Claims per day (last 30 days)
    daily_claims = db.query(
        func.date(db_models.Claim.created_at).label('date'),
        func.count(db_models.Claim.claim_id).label('count')
    ).group_by(func.date(db_models.Claim.created_at)).all()

    return {
        "daily_claims": [
            {"date": str(date), "count": count}
            for date, count in daily_claims
        ]
    }
