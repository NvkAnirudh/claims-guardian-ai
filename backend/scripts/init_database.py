#!/usr/bin/env python3
"""Database initialization script - creates tables and loads reference data"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database.models import Base, ICD10Code, CPTCode
from app.database.connection import engine, get_db_session
import pandas as pd
import json


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")


def load_icd10_codes():
    """Load ICD-10 codes from CSV"""
    print("Loading ICD-10 codes...")
    csv_path = os.path.join(os.path.dirname(__file__), '../data/raw/icd10_codes.csv')

    df = pd.read_csv(csv_path)

    with get_db_session() as db:
        for _, row in df.iterrows():
            code = ICD10Code(
                code=row['code'],
                description=row['description'],
                category=row['category'] if pd.notna(row['category']) else None,
                age_min=int(row['age_min']) if pd.notna(row['age_min']) else None,
                age_max=int(row['age_max']) if pd.notna(row['age_max']) else None,
                gender_restriction=row['gender_restriction'] if pd.notna(row['gender_restriction']) else None
            )
            db.merge(code)

    print(f"✓ Loaded {len(df)} ICD-10 codes")


def load_cpt_codes():
    """Load CPT codes from CSV"""
    print("Loading CPT codes...")
    csv_path = os.path.join(os.path.dirname(__file__), '../data/raw/cpt_codes.csv')

    df = pd.read_csv(csv_path)

    with get_db_session() as db:
        for _, row in df.iterrows():
            code = CPTCode(
                code=row['code'],
                description=row['description'],
                time_minutes=int(row['time_minutes']) if pd.notna(row['time_minutes']) else None,
                complexity_level=row['complexity_level'] if pd.notna(row['complexity_level']) else None,
                avg_charge=float(row['avg_charge']) if pd.notna(row['avg_charge']) else None,
                category=row['category'] if pd.notna(row['category']) else None,
                requires_diagnosis=bool(row['requires_diagnosis']) if pd.notna(row['requires_diagnosis']) else True
            )
            db.merge(code)

    print(f"✓ Loaded {len(df)} CPT codes")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)

    try:
        create_tables()
        load_icd10_codes()
        load_cpt_codes()

        print("=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
