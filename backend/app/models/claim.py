from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class Patient(BaseModel):
    name: str
    dob: date
    gender: str = Field(..., pattern="^[MF]$")
    insurance_id: str


class Provider(BaseModel):
    name: str
    npi: str = Field(..., min_length=10, max_length=10)
    specialty: str


class ProcedureCode(BaseModel):
    cpt: str
    modifiers: List[str] = []
    units: int = 1
    charge: float


class Claim(BaseModel):
    claim_id: str
    patient: Patient
    provider: Provider
    service_date: date
    diagnosis_codes: List[str]
    procedure_codes: List[ProcedureCode]
    total_charge: float

    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "CLM001",
                "patient": {
                    "name": "John Doe",
                    "dob": "1985-05-15",
                    "gender": "M",
                    "insurance_id": "XYZ123456789"
                },
                "provider": {
                    "name": "Dr. Jane Smith",
                    "npi": "1234567890",
                    "specialty": "Family Medicine"
                },
                "service_date": "2025-01-15",
                "diagnosis_codes": ["E11.9"],
                "procedure_codes": [
                    {
                        "cpt": "99213",
                        "modifiers": [],
                        "units": 1,
                        "charge": 135.00
                    }
                ],
                "total_charge": 135.00
            }
        }
