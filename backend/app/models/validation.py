from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationIssue(BaseModel):
    agent_name: str
    issue_type: str
    severity: IssueSeverity
    description: str
    explanation: str = ""
    confidence_score: float
    cost_impact: Optional[float] = None
    suggested_fix: Optional[str] = None


class ValidationResult(BaseModel):
    claim_id: str
    overall_status: str  # "passed", "flagged", "rejected"
    risk_score: float  # 0-100
    issues: List[ValidationIssue]
    total_cost_impact: float
    processing_time_ms: int
