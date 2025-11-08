from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Text, ARRAY, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class ICD10Code(Base):
    __tablename__ = "icd10_codes"

    code = Column(String(10), primary_key=True)
    description = Column(Text, nullable=False)
    category = Column(String(100))
    age_min = Column(Integer)
    age_max = Column(Integer)
    gender_restriction = Column(String(1))


class CPTCode(Base):
    __tablename__ = "cpt_codes"

    code = Column(String(10), primary_key=True)
    description = Column(Text, nullable=False)
    time_minutes = Column(Integer)
    complexity_level = Column(String(20))
    avg_charge = Column(Float)
    category = Column(String(100))
    requires_diagnosis = Column(Boolean, default=True)


class NCCIEdit(Base):
    __tablename__ = "ncci_edits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    column1_code = Column(String(10), nullable=False)
    column2_code = Column(String(10), nullable=False)
    modifier_indicator = Column(String(1))


class Claim(Base):
    __tablename__ = "claims"

    claim_id = Column(String(50), primary_key=True)
    patient_data = Column(JSON, nullable=False)
    provider_data = Column(JSON, nullable=False)
    service_date = Column(Date, nullable=False)
    diagnosis_codes = Column(ARRAY(String), nullable=False)
    procedure_codes = Column(JSON, nullable=False)
    total_charge = Column(Float, nullable=False)
    validation_status = Column(String(20))
    created_at = Column(DateTime, default=func.now())


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(50), ForeignKey("claims.claim_id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    issue_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    explanation = Column(Text)
    confidence_score = Column(Float, nullable=False)
    cost_impact = Column(Float)
    suggested_fix = Column(Text)
    created_at = Column(DateTime, default=func.now())
