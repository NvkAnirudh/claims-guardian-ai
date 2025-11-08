from typing import List
import json
import os
from sqlalchemy.orm import Session
from app.models.claim import Claim
from app.models.validation import ValidationIssue, IssueSeverity


class ModifierValidator:
    """Validates correct usage of modifiers"""

    def __init__(self, db: Session):
        self.db = db
        self.modifier_rules = self._load_modifier_rules()

    def _load_modifier_rules(self) -> dict:
        """Load modifier rules from JSON"""
        rules_path = os.path.join(
            os.path.dirname(__file__),
            '../../data/raw/modifier_rules.json'
        )
        try:
            with open(rules_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def validate(self, claim: Claim) -> List[ValidationIssue]:
        """Run modifier validation checks"""
        issues = []

        # Check 1: Modifier 25 required for E/M + procedure same day
        issues.extend(self._check_modifier_25(claim))

        # Check 2: Modifier 59/X{EPSU} conflicts
        issues.extend(self._check_modifier_59_conflicts(claim))

        # Check 3: Bilateral modifier usage
        issues.extend(self._check_bilateral_modifiers(claim))

        # Check 4: Invalid modifier combinations
        issues.extend(self._check_invalid_combinations(claim))

        return issues

    def _check_modifier_25(self, claim: Claim) -> List[ValidationIssue]:
        """Check if modifier 25 is needed for E/M + procedure same day"""
        issues = []

        em_codes = [p for p in claim.procedure_codes if p.cpt.startswith('99') and p.cpt[:3] in ['992', '999']]
        other_procs = [p for p in claim.procedure_codes if not (p.cpt.startswith('99') and p.cpt[:3] in ['992', '999'])]

        # Preventive codes don't need modifier 25
        preventive_codes = ['99381', '99382', '99383', '99384', '99385', '99386', '99387',
                           '99391', '99392', '99393', '99394', '99395', '99396', '99397']

        if em_codes and other_procs:
            for em in em_codes:
                # Skip preventive codes
                if em.cpt in preventive_codes:
                    continue

                if '25' not in em.modifiers:
                    issues.append(ValidationIssue(
                        agent_name="Modifier Validator",
                        issue_type="missing_modifier_25",
                        severity=IssueSeverity.MEDIUM,
                        description=f"Modifier 25 required on E/M code {em.cpt} when billed with procedure",
                        explanation="When billing E/M service on same day as procedure, modifier 25 indicates the E/M was significant and separately identifiable",
                        confidence_score=0.88,
                        suggested_fix=f"Add modifier 25 to {em.cpt}"
                    ))

        return issues

    def _check_modifier_59_conflicts(self, claim: Claim) -> List[ValidationIssue]:
        """Check for conflicts between 59 and X{EPSU} modifiers"""
        issues = []

        x_modifiers = ['XE', 'XP', 'XS', 'XU']

        for proc in claim.procedure_codes:
            has_59 = '59' in proc.modifiers
            has_x = any(xm in proc.modifiers for xm in x_modifiers)

            if has_59 and has_x:
                x_used = [xm for xm in x_modifiers if xm in proc.modifiers]
                issues.append(ValidationIssue(
                    agent_name="Modifier Validator",
                    issue_type="modifier_conflict",
                    severity=IssueSeverity.MEDIUM,
                    description=f"CPT {proc.cpt} has both modifier 59 and {', '.join(x_used)}",
                    explanation=f"X{'{EPSU}'} modifiers are more specific than 59. Use only the X modifier, not both",
                    confidence_score=0.92,
                    suggested_fix=f"Remove modifier 59, keep {x_used[0]}"
                ))

        return issues

    def _check_bilateral_modifiers(self, claim: Claim) -> List[ValidationIssue]:
        """Check bilateral modifier (50) usage"""
        issues = []

        for proc in claim.procedure_codes:
            if '50' in proc.modifiers:
                # Check if also has LT or RT (conflict)
                if 'LT' in proc.modifiers or 'RT' in proc.modifiers:
                    issues.append(ValidationIssue(
                        agent_name="Modifier Validator",
                        issue_type="modifier_conflict",
                        severity=IssueSeverity.HIGH,
                        description=f"CPT {proc.cpt} has modifier 50 with LT/RT",
                        explanation="Cannot use bilateral modifier (50) with laterality modifiers (LT/RT)",
                        confidence_score=0.95,
                        suggested_fix="Use either modifier 50 for bilateral, or LT/RT for unilateral procedures"
                    ))

        return issues

    def _check_invalid_combinations(self, claim: Claim) -> List[ValidationIssue]:
        """Check for invalid modifier combinations"""
        issues = []

        for proc in claim.procedure_codes:
            # TC and 26 cannot be used together
            if 'TC' in proc.modifiers and '26' in proc.modifiers:
                issues.append(ValidationIssue(
                    agent_name="Modifier Validator",
                    issue_type="modifier_conflict",
                    severity=IssueSeverity.CRITICAL,
                    description=f"CPT {proc.cpt} has both TC and 26 modifiers",
                    explanation="TC (technical component) and 26 (professional component) are mutually exclusive",
                    confidence_score=0.98,
                    suggested_fix="Use either TC or 26, not both"
                ))

        return issues
