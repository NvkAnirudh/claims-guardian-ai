from typing import List
import json
import os
from sqlalchemy.orm import Session
from app.models.claim import Claim
from app.models.validation import ValidationIssue, IssueSeverity
from app.database.models import ICD10Code, CPTCode


class DemographicValidator:
    """Validates age/gender restrictions on codes"""

    def __init__(self, db: Session):
        self.db = db
        self.demographic_rules = self._load_demographic_rules()

    def _load_demographic_rules(self) -> dict:
        """Load demographic rules from JSON"""
        rules_path = os.path.join(
            os.path.dirname(__file__),
            '../../data/raw/demographic_rules.json'
        )
        try:
            with open(rules_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {"icd10_rules": {}, "cpt_rules": {}}

    def validate(self, claim: Claim) -> List[ValidationIssue]:
        """Run demographic validation checks"""
        issues = []
        patient_age = self._calculate_age(claim.patient.dob, claim.service_date)

        # Check ICD-10 codes
        issues.extend(self._check_icd10_restrictions(claim, patient_age))

        # Check CPT codes
        issues.extend(self._check_cpt_restrictions(claim, patient_age))

        return issues

    def _calculate_age(self, dob, service_date) -> int:
        """Calculate age in years"""
        return (service_date - dob).days // 365

    def _check_icd10_restrictions(self, claim: Claim, patient_age: int) -> List[ValidationIssue]:
        """Check ICD-10 age/gender restrictions"""
        issues = []

        for dx_code in claim.diagnosis_codes:
            # Check database restrictions
            dx = self.db.query(ICD10Code).filter(ICD10Code.code == dx_code).first()

            if dx:
                # Gender restriction
                if dx.gender_restriction and claim.patient.gender != dx.gender_restriction:
                    issues.append(ValidationIssue(
                        agent_name="Demographic Validator",
                        issue_type="gender_restriction",
                        severity=IssueSeverity.CRITICAL,
                        description=f"ICD-10 {dx_code} ({dx.description}) invalid for gender {claim.patient.gender}",
                        explanation=f"This code is only valid for gender {dx.gender_restriction}",
                        confidence_score=0.99
                    ))

                # Age restrictions
                if dx.age_min is not None and patient_age < dx.age_min:
                    issues.append(ValidationIssue(
                        agent_name="Demographic Validator",
                        issue_type="age_restriction",
                        severity=IssueSeverity.HIGH,
                        description=f"ICD-10 {dx_code} invalid for age {patient_age}",
                        explanation=f"This code requires minimum age {dx.age_min}",
                        confidence_score=0.95
                    ))

                if dx.age_max is not None and patient_age > dx.age_max:
                    issues.append(ValidationIssue(
                        agent_name="Demographic Validator",
                        issue_type="age_restriction",
                        severity=IssueSeverity.MEDIUM,
                        description=f"ICD-10 {dx_code} unusual for age {patient_age}",
                        explanation=f"This code is typically for age {dx.age_max} or younger",
                        confidence_score=0.75
                    ))

            # Check JSON rules for code ranges
            issues.extend(self._check_icd10_range_rules(dx_code, claim.patient.gender, patient_age))

        return issues

    def _check_icd10_range_rules(self, dx_code: str, gender: str, age: int) -> List[ValidationIssue]:
        """Check ICD-10 code against range-based rules"""
        issues = []
        rules = self.demographic_rules.get('icd10_rules', {})

        for rule_name, rule in rules.items():
            code_range = rule.get('code_range')

            # Check if code matches range
            if self._code_in_range(dx_code, code_range):
                # Check gender
                if rule.get('gender') and gender != rule['gender']:
                    issues.append(ValidationIssue(
                        agent_name="Demographic Validator",
                        issue_type="gender_restriction",
                        severity=IssueSeverity.CRITICAL if rule['severity'] == 'critical' else IssueSeverity.HIGH,
                        description=f"ICD-10 {dx_code}: {rule['description']} invalid for gender {gender}",
                        explanation=rule['explanation'],
                        confidence_score=0.99 if rule['severity'] == 'critical' else 0.90
                    ))

                # Check age
                age_min = rule.get('age_min')
                age_max = rule.get('age_max')

                if age_min and age < age_min:
                    issues.append(ValidationIssue(
                        agent_name="Demographic Validator",
                        issue_type="age_restriction",
                        severity=IssueSeverity.HIGH if rule['severity'] == 'high' else IssueSeverity.MEDIUM,
                        description=f"ICD-10 {dx_code} invalid for age {age} (minimum {age_min})",
                        explanation=rule['explanation'],
                        confidence_score=0.85
                    ))

                if age_max and age > age_max:
                    issues.append(ValidationIssue(
                        agent_name="Demographic Validator",
                        issue_type="age_restriction",
                        severity=IssueSeverity.MEDIUM,
                        description=f"ICD-10 {dx_code} unusual for age {age} (typically max {age_max})",
                        explanation=rule['explanation'],
                        confidence_score=0.70
                    ))

        return issues

    def _check_cpt_restrictions(self, claim: Claim, patient_age: int) -> List[ValidationIssue]:
        """Check CPT age/gender restrictions"""
        issues = []
        rules = self.demographic_rules.get('cpt_rules', {})

        for proc in claim.procedure_codes:
            for rule_name, rule in rules.items():
                code_range = rule.get('code_range')

                if self._code_in_range(proc.cpt, code_range):
                    # Check gender
                    if rule.get('gender') and claim.patient.gender != rule['gender']:
                        issues.append(ValidationIssue(
                            agent_name="Demographic Validator",
                            issue_type="gender_restriction",
                            severity=IssueSeverity.HIGH,
                            description=f"CPT {proc.cpt}: {rule['description']} invalid for gender {claim.patient.gender}",
                            explanation=rule['explanation'],
                            confidence_score=0.90
                        ))

                    # Check age
                    age_min = rule.get('age_min')
                    age_max = rule.get('age_max')

                    if age_min and patient_age < age_min:
                        issues.append(ValidationIssue(
                            agent_name="Demographic Validator",
                            issue_type="age_restriction",
                            severity=IssueSeverity.HIGH,
                            description=f"CPT {proc.cpt} invalid for age {patient_age} (minimum {age_min})",
                            explanation=rule['explanation'],
                            confidence_score=0.90
                        ))

                    if age_max and patient_age > age_max:
                        issues.append(ValidationIssue(
                            agent_name="Demographic Validator",
                            issue_type="age_restriction",
                            severity=IssueSeverity.HIGH,
                            description=f"CPT {proc.cpt} invalid for age {patient_age} (maximum {age_max})",
                            explanation=rule['explanation'],
                            confidence_score=0.90
                        ))

        return issues

    def _code_in_range(self, code: str, code_range) -> bool:
        """Check if code is in range (handles single codes or ranges like O00-O9A)"""
        if isinstance(code_range, list):
            return code in code_range

        if isinstance(code_range, str):
            if '-' in code_range:
                # Range like "O00-O9A"
                start, end = code_range.split('-')
                return start <= code <= end
            else:
                # Single code
                return code == code_range

        return False
