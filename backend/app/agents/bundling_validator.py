from typing import List
from sqlalchemy.orm import Session
from app.models.claim import Claim
from app.models.validation import ValidationIssue, IssueSeverity
from app.database.models import NCCIEdit


class BundlingValidator:
    """Validates bundling/unbundling violations"""

    def __init__(self, db: Session):
        self.db = db
        # Common bundling rules (simplified NCCI edits)
        self.bundled_pairs = {
            ('43235', '43239'): 'Upper GI endoscopy procedures are bundled',
            ('45378', '45380'): 'Colonoscopy with biopsy includes diagnostic colonoscopy',
            ('45380', '45385'): 'Colonoscopy with polyp removal includes biopsy',
        }

    def validate(self, claim: Claim) -> List[ValidationIssue]:
        """Run bundling validation checks"""
        issues = []

        if len(claim.procedure_codes) < 2:
            return issues  # No bundling issues with single procedure

        # Check pairwise combinations
        issues.extend(self._check_bundled_procedures(claim))

        # Check same-day E/M bundling
        issues.extend(self._check_em_procedure_bundling(claim))

        return issues

    def _check_bundled_procedures(self, claim: Claim) -> List[ValidationIssue]:
        """Check if procedures are improperly unbundled"""
        issues = []

        codes = [p.cpt for p in claim.procedure_codes]

        # Check against NCCI database
        for i, proc1 in enumerate(claim.procedure_codes):
            for proc2 in claim.procedure_codes[i+1:]:
                # Check database first
                ncci_edit = self.db.query(NCCIEdit).filter(
                    NCCIEdit.column1_code == proc1.cpt,
                    NCCIEdit.column2_code == proc2.cpt
                ).first()

                if ncci_edit:
                    # Check if modifier allows override
                    has_override = self._check_modifier_override(proc2.modifiers, ncci_edit.modifier_indicator)

                    if not has_override:
                        issues.append(ValidationIssue(
                            agent_name="Bundling Validator",
                            issue_type="unbundling_violation",
                            severity=IssueSeverity.HIGH,
                            description=f"CPT {proc2.cpt} is bundled into {proc1.cpt}",
                            explanation=f"These procedures should not be billed separately according to NCCI edits",
                            confidence_score=0.90,
                            cost_impact=proc2.charge,
                            suggested_fix=f"Remove {proc2.cpt} or add appropriate modifier if services were distinct"
                        ))

                # Check hardcoded rules
                pair = (proc1.cpt, proc2.cpt)
                if pair in self.bundled_pairs:
                    if not self._has_distinct_modifier(proc2.modifiers):
                        issues.append(ValidationIssue(
                            agent_name="Bundling Validator",
                            issue_type="unbundling_violation",
                            severity=IssueSeverity.HIGH,
                            description=f"CPT {proc2.cpt} bundled into {proc1.cpt}",
                            explanation=self.bundled_pairs[pair],
                            confidence_score=0.85,
                            cost_impact=proc2.charge,
                            suggested_fix=f"Remove {proc2.cpt} or add modifier 59/X{'{EPSU}'} if distinct service"
                        ))

        return issues

    def _check_em_procedure_bundling(self, claim: Claim) -> List[ValidationIssue]:
        """Check E/M with procedure on same day"""
        issues = []

        em_codes = [p for p in claim.procedure_codes if p.cpt.startswith('99')]
        procedures = [p for p in claim.procedure_codes if not p.cpt.startswith('99')]

        if em_codes and procedures:
            for em in em_codes:
                # E/M with procedure requires modifier 25
                if '25' not in em.modifiers:
                    # This is handled by modifier validator, but we can flag bundling aspect
                    pass  # Skip to avoid duplicate flags

        return issues

    def _check_modifier_override(self, modifiers: List[str], indicator: str) -> bool:
        """Check if modifiers allow override of bundling edit"""
        if indicator == '0':
            return False  # No modifier allowed
        elif indicator == '1':
            # Modifier 59 or X{EPSU} allowed
            return any(m in modifiers for m in ['59', 'XE', 'XP', 'XS', 'XU'])
        elif indicator == '9':
            return True  # Not applicable
        return False

    def _has_distinct_modifier(self, modifiers: List[str]) -> bool:
        """Check if procedure has modifier indicating distinct service"""
        distinct_modifiers = ['59', 'XE', 'XP', 'XS', 'XU']
        return any(m in modifiers for m in distinct_modifiers)
