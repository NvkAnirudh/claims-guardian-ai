from typing import TypedDict, List, Annotated
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session
import operator

from app.models.claim import Claim
from app.models.validation import ValidationIssue, ValidationResult
from app.agents.cpt_icd_validator import CPTICDValidator
from app.agents.bundling_validator import BundlingValidator
from app.agents.modifier_validator import ModifierValidator
from app.agents.demographic_validator import DemographicValidator
from app.agents.cost_analyzer import CostAnalyzer
from app.services.llm_service import LLMService
from app.database.connection import SessionLocal


class ValidationState(TypedDict):
    """State passed between nodes in the workflow"""
    claim: Claim
    issues: Annotated[List[ValidationIssue], operator.add]  # Accumulate issues from all agents
    start_time: float


class ClaimValidationOrchestrator:
    """Orchestrates multiple validation agents using LangGraph"""

    def __init__(self, db: Session, llm_service: LLMService = None):
        self.db = db
        self.llm_service = llm_service or LLMService()
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build parallel LangGraph workflow"""

        workflow = StateGraph(ValidationState)

        # Add agent nodes
        workflow.add_node("cpt_icd", self._run_cpt_icd)
        workflow.add_node("bundling", self._run_bundling)
        workflow.add_node("modifier", self._run_modifier)
        workflow.add_node("demographic", self._run_demographic)
        workflow.add_node("cost", self._run_cost)
        workflow.add_node("aggregate", self._aggregate_results)
        workflow.add_node("explain", self._add_explanations)

        # Parallel execution: All agents start simultaneously
        workflow.add_edge(START, "cpt_icd")
        workflow.add_edge(START, "bundling")
        workflow.add_edge(START, "modifier")
        workflow.add_edge(START, "demographic")
        workflow.add_edge(START, "cost")

        # All agents converge to aggregator
        workflow.add_edge("cpt_icd", "aggregate")
        workflow.add_edge("bundling", "aggregate")
        workflow.add_edge("modifier", "aggregate")
        workflow.add_edge("demographic", "aggregate")
        workflow.add_edge("cost", "aggregate")

        # Final explanation enhancement
        workflow.add_edge("aggregate", "explain")
        workflow.add_edge("explain", END)

        return workflow.compile()

    def validate_claim(self, claim: Claim) -> ValidationResult:
        """Run full validation workflow on a claim"""

        initial_state: ValidationState = {
            "claim": claim,
            "issues": [],
            "start_time": datetime.now().timestamp()
        }

        # Execute workflow
        final_state = self.workflow.invoke(initial_state)

        # Calculate metrics
        processing_time = int((datetime.now().timestamp() - final_state["start_time"]) * 1000)
        risk_score = self._calculate_risk_score(final_state["issues"])
        status = self._determine_status(final_state["issues"])
        total_cost_impact = sum(
            issue.cost_impact for issue in final_state["issues"]
            if issue.cost_impact is not None
        )

        return ValidationResult(
            claim_id=claim.claim_id,
            overall_status=status,
            risk_score=risk_score,
            issues=final_state["issues"],
            total_cost_impact=total_cost_impact,
            processing_time_ms=processing_time
        )

    # Agent execution functions
    def _run_cpt_icd(self, state: ValidationState) -> dict:
        """Execute CPT-ICD-10 validator"""
        db = SessionLocal()
        try:
            validator = CPTICDValidator(db)
            new_issues = validator.validate(state["claim"])
        finally:
            db.close()
        return {"issues": new_issues}  # Return only new issues, LangGraph will accumulate

    def _run_bundling(self, state: ValidationState) -> dict:
        """Execute bundling validator"""
        db = SessionLocal()
        try:
            validator = BundlingValidator(db)
            new_issues = validator.validate(state["claim"])
        finally:
            db.close()
        return {"issues": new_issues}

    def _run_modifier(self, state: ValidationState) -> dict:
        """Execute modifier validator"""
        db = SessionLocal()
        try:
            validator = ModifierValidator(db)
            new_issues = validator.validate(state["claim"])
        finally:
            db.close()
        return {"issues": new_issues}

    def _run_demographic(self, state: ValidationState) -> dict:
        """Execute demographic validator"""
        db = SessionLocal()
        try:
            validator = DemographicValidator(db)
            new_issues = validator.validate(state["claim"])
        finally:
            db.close()
        return {"issues": new_issues}

    def _run_cost(self, state: ValidationState) -> dict:
        """Execute cost analyzer"""
        db = SessionLocal()
        try:
            analyzer = CostAnalyzer(db)
            new_issues = analyzer.validate(state["claim"])
        finally:
            db.close()
        return {"issues": new_issues}

    def _aggregate_results(self, state: ValidationState) -> dict:
        """Aggregate and sort issues by severity"""
        # Sort issues by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        state["issues"].sort(
            key=lambda x: severity_order.get(x.severity.value, 4)
        )
        return {"issues": []}  # Return empty list - adds nothing but satisfies LangGraph

    def _add_explanations(self, state: ValidationState) -> dict:
        """Enhance issues with LLM-generated explanations"""
        for issue in state["issues"]:
            # Only enhance if explanation is basic/empty
            if len(issue.explanation) < 50:  # Basic explanation threshold
                enhanced = self.llm_service.explain_issue(issue, state["claim"])
                issue.explanation = enhanced
        return {"issues": []}  # Return empty list - adds nothing but satisfies LangGraph

    def _calculate_risk_score(self, issues: List[ValidationIssue]) -> float:
        """Calculate risk score from 0-100"""
        if not issues:
            return 0.0

        severity_weights = {
            "critical": 25,
            "high": 15,
            "medium": 8,
            "low": 3
        }

        score = sum(
            severity_weights.get(issue.severity.value, 0)
            for issue in issues
        )

        return min(score, 100.0)

    def _determine_status(self, issues: List[ValidationIssue]) -> str:
        """Determine overall claim status"""
        if not issues:
            return "passed"

        # Check for critical issues
        has_critical = any(issue.severity.value == "critical" for issue in issues)
        if has_critical:
            return "rejected"

        return "flagged"
