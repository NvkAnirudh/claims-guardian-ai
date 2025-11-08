from typing import List
from sqlalchemy.orm import Session
from app.models.claim import Claim
from app.models.validation import ValidationIssue, IssueSeverity
from app.database.models import CPTCode, ICD10Code


class CostAnalyzer:
    """Detects statistical outliers in billing amounts"""

    def __init__(self, db: Session):
        self.db = db

    def validate(self, claim: Claim) -> List[ValidationIssue]:
        """Run cost analysis checks"""
        issues = []

        # Check each procedure for cost anomalies
        for proc in claim.procedure_codes:
            issues.extend(self._check_charge_variance(claim, proc))

        # Check for upcoding patterns
        issues.extend(self._check_upcoding_patterns(claim))

        return issues

    def _check_charge_variance(self, claim: Claim, proc) -> List[ValidationIssue]:
        """Check if charge deviates significantly from average"""
        issues = []

        cpt = self.db.query(CPTCode).filter(CPTCode.code == proc.cpt).first()

        if not cpt or not cpt.avg_charge:
            return issues

        variance = (proc.charge - cpt.avg_charge) / cpt.avg_charge

        # Flag if > 50% deviation
        if abs(variance) > 0.50:
            if variance > 0:  # Overcharge
                severity = IssueSeverity.HIGH if variance > 1.0 else IssueSeverity.MEDIUM

                issues.append(ValidationIssue(
                    agent_name="Cost Analyzer",
                    issue_type="unusual_charge_high",
                    severity=severity,
                    description=f"CPT {proc.cpt} charge ${proc.charge:.2f} is {variance*100:.0f}% above average ${cpt.avg_charge:.2f}",
                    explanation=f"Charge deviates significantly from typical amount. Review documentation to justify higher charge.",
                    confidence_score=0.75,
                    cost_impact=proc.charge - cpt.avg_charge,
                    suggested_fix=f"Verify charge is correct. Expected range: ${cpt.avg_charge*0.8:.2f}-${cpt.avg_charge*1.2:.2f}"
                ))
            else:  # Undercharge (less critical)
                if variance < -0.80:  # Only flag if very low
                    issues.append(ValidationIssue(
                        agent_name="Cost Analyzer",
                        issue_type="unusual_charge_low",
                        severity=IssueSeverity.LOW,
                        description=f"CPT {proc.cpt} charge ${proc.charge:.2f} is {abs(variance)*100:.0f}% below average ${cpt.avg_charge:.2f}",
                        explanation="Charge is unusually low. May indicate billing error or contract discount.",
                        confidence_score=0.60
                    ))

        return issues

    def _check_upcoding_patterns(self, claim: Claim) -> List[ValidationIssue]:
        """Detect potential upcoding patterns"""
        issues = []

        # Pattern 1: High complexity E/M with routine diagnosis
        routine_diagnoses = ['Z00.00', 'Z00.01', 'Z00.121', 'Z00.129']
        has_routine = any(dx in routine_diagnoses for dx in claim.diagnosis_codes)

        if has_routine:
            for proc in claim.procedure_codes:
                # High complexity E/M codes
                high_em_codes = {
                    '99205': ('99203', 135),
                    '99215': ('99213', 135),
                    '99285': ('99283', 250),
                    '99223': ('99221', 150),
                }

                if proc.cpt in high_em_codes:
                    expected_code, expected_charge = high_em_codes[proc.cpt]
                    cost_diff = proc.charge - expected_charge

                    issues.append(ValidationIssue(
                        agent_name="Cost Analyzer",
                        issue_type="potential_upcoding",
                        severity=IssueSeverity.HIGH,
                        description=f"Possible upcoding: {proc.cpt} billed for routine visit",
                        explanation=f"High complexity code {proc.cpt} used with routine diagnosis. Expected {expected_code} for routine care.",
                        confidence_score=0.85,
                        cost_impact=cost_diff if cost_diff > 0 else None,
                        suggested_fix=f"Verify visit complexity. Consider downcoding to {expected_code} if appropriate."
                    ))

        # Pattern 2: Unusually high number of procedures
        if len(claim.procedure_codes) > 5:
            issues.append(ValidationIssue(
                agent_name="Cost Analyzer",
                issue_type="high_procedure_count",
                severity=IssueSeverity.LOW,
                description=f"Claim has {len(claim.procedure_codes)} procedures",
                explanation="Unusually high number of procedures on single claim. Verify all are documented and medically necessary.",
                confidence_score=0.60
            ))

        # Pattern 3: Total charge significantly higher than sum of averages
        total_expected = sum(
            self._get_avg_charge(p.cpt) for p in claim.procedure_codes
        )

        if total_expected > 0:
            total_variance = (claim.total_charge - total_expected) / total_expected

            if total_variance > 0.75:  # 75% higher than expected
                issues.append(ValidationIssue(
                    agent_name="Cost Analyzer",
                    issue_type="high_total_charge",
                    severity=IssueSeverity.MEDIUM,
                    description=f"Total charge ${claim.total_charge:.2f} is {total_variance*100:.0f}% above expected ${total_expected:.2f}",
                    explanation="Overall claim cost is significantly higher than typical charges for these procedures.",
                    confidence_score=0.70,
                    cost_impact=claim.total_charge - total_expected
                ))

        return issues

    def _get_avg_charge(self, cpt_code: str) -> float:
        """Get average charge for CPT code"""
        cpt = self.db.query(CPTCode).filter(CPTCode.code == cpt_code).first()
        return cpt.avg_charge if cpt and cpt.avg_charge else 0.0
