from typing import List
from sqlalchemy.orm import Session
from app.models.claim import Claim
from app.models.validation import ValidationIssue, IssueSeverity
from app.database.models import ICD10Code, CPTCode


class CPTICDValidator:
    """Validates CPT-ICD-10 code compatibility"""

    def __init__(self, db: Session):
        self.db = db

    def validate(self, claim: Claim) -> List[ValidationIssue]:
        """Run all CPT-ICD-10 validation checks"""
        issues = []

        # Check 1: E/M codes require valid diagnosis
        issues.extend(self._check_em_has_diagnosis(claim))

        # Check 2: Preventive codes shouldn't have high complexity E/M
        issues.extend(self._check_preventive_complexity(claim))

        # Check 3: Procedure-diagnosis category alignment
        issues.extend(self._check_category_alignment(claim))

        return issues

    def _check_em_has_diagnosis(self, claim: Claim) -> List[ValidationIssue]:
        """E/M codes require at least one diagnosis"""
        issues = []

        for proc in claim.procedure_codes:
            # E/M codes start with 99
            if proc.cpt.startswith('99') and proc.cpt[:3] in ['992', '999']:
                if not claim.diagnosis_codes:
                    issues.append(ValidationIssue(
                        agent_name="CPT-ICD Validator",
                        issue_type="missing_diagnosis",
                        severity=IssueSeverity.HIGH,
                        description=f"E/M code {proc.cpt} requires diagnosis",
                        explanation="Evaluation & Management services must have documented diagnosis codes",
                        confidence_score=0.95
                    ))

        return issues

    def _check_preventive_complexity(self, claim: Claim) -> List[ValidationIssue]:
        """Preventive diagnoses shouldn't have high complexity E/M codes"""
        issues = []

        # Preventive diagnosis codes
        preventive_codes = ['Z00.00', 'Z00.01', 'Z00.121', 'Z00.129']

        # Check if any diagnosis is preventive
        has_preventive = any(dx in preventive_codes for dx in claim.diagnosis_codes)

        if has_preventive:
            for proc in claim.procedure_codes:
                # High complexity E/M codes (99205, 99215, 99285)
                high_complexity = ['99205', '99215', '99285', '99223', '99233']

                if proc.cpt in high_complexity:
                    # Get expected charge for appropriate code
                    expected_code = self._get_appropriate_preventive_code(claim)
                    expected_cpt = self.db.query(CPTCode).filter(
                        CPTCode.code == expected_code
                    ).first()

                    cost_diff = proc.charge - (expected_cpt.avg_charge if expected_cpt else 0)

                    issues.append(ValidationIssue(
                        agent_name="CPT-ICD Validator",
                        issue_type="preventive_complexity_mismatch",
                        severity=IssueSeverity.HIGH,
                        description=f"High complexity code {proc.cpt} billed for routine preventive visit",
                        explanation=f"Preventive visits are typically straightforward and don't justify high complexity E/M codes. Expected {expected_code} for routine care.",
                        confidence_score=0.85,
                        cost_impact=cost_diff if cost_diff > 0 else None,
                        suggested_fix=f"Consider downcoding to {expected_code} or use preventive visit codes (99381-99397)"
                    ))

        return issues

    def _check_category_alignment(self, claim: Claim) -> List[ValidationIssue]:
        """Check if procedure categories align with diagnosis categories"""
        issues = []

        # Get diagnosis categories
        dx_categories = []
        for dx_code in claim.diagnosis_codes:
            dx = self.db.query(ICD10Code).filter(ICD10Code.code == dx_code).first()
            if dx and dx.category:
                dx_categories.append(dx.category.lower())

        # Get procedure categories
        for proc in claim.procedure_codes:
            cpt = self.db.query(CPTCode).filter(CPTCode.code == proc.cpt).first()

            if cpt and cpt.category and dx_categories:
                proc_cat = cpt.category.lower()

                # Check for obvious mismatches
                if 'gi procedures' in proc_cat and not any(
                    'digestive' in cat for cat in dx_categories
                ):
                    issues.append(ValidationIssue(
                        agent_name="CPT-ICD Validator",
                        issue_type="category_mismatch",
                        severity=IssueSeverity.MEDIUM,
                        description=f"GI procedure {proc.cpt} with non-digestive diagnosis",
                        explanation="Review if procedure matches the documented diagnosis",
                        confidence_score=0.70
                    ))

        return issues

    def _get_appropriate_preventive_code(self, claim: Claim) -> str:
        """Get appropriate preventive code based on patient age"""
        from datetime import datetime
        age = (claim.service_date - claim.patient.dob).days // 365

        if age < 1:
            return '99381'  # Infant
        elif age <= 4:
            return '99382'  # 1-4 years
        elif age <= 11:
            return '99383'  # 5-11 years
        elif age <= 17:
            return '99384'  # 12-17 years
        elif age <= 39:
            return '99385'  # 18-39 years
        elif age <= 64:
            return '99386'  # 40-64 years
        else:
            return '99387'  # 65+ years
