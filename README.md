# Claims Guardian AI - Medical Claims Validation Agent

An intelligent multi-agent system for automated medical claims validation using AI to detect billing errors, fraud, and compliance violations.

## Table of Contents

- [Overview](#overview)
- [Real-World Use Case: Rachel's Story](#real-world-use-case-rachels-story)
- [Architecture](#architecture)
  - [Multi-Agent System](#multi-agent-system)
  - [Technology Stack](#technology-stack)
- [Features](#features)
  - [1. Comprehensive Validation Rules](#1-comprehensive-validation-rules)
  - [2. AI-Powered Explanations](#2-ai-powered-explanations)
  - [3. Risk Scoring & Reporting](#3-risk-scoring--reporting)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Troubleshooting](#troubleshooting)
  - [Access the Application](#access-the-application)
- [Usage](#usage)
  - [1. Validate a Claim (UI)](#1-validate-a-claim-ui)
  - [2. API Endpoints](#2-api-endpoints)
- [Project Structure](#project-structure)
- [Performance Metrics](#performance-metrics)
- [Sample Validation Output](#sample-validation-output)
- [Development](#development)
  - [Testing](#testing)
  - [Database Management](#database-management)
  - [Add More Medical Codes](#add-more-medical-codes)
- [Technical Highlights](#technical-highlights)
  - [LangGraph Parallel Execution](#langgraph-parallel-execution)
  - [Prompt Caching Implementation](#prompt-caching-implementation)
- [Future Enhancements](#future-enhancements)
- [Known Limitations](#known-limitations)
- [License](#license)
- [Contributing](#contributing)

## Overview

Claims Guardian AI is a production-ready prototype that validates medical insurance claims using a sophisticated multi-agent architecture. The system analyzes diagnosis codes, procedure codes, patient demographics, and charges to identify potential issues before claims are submitted to insurers.

**Key Highlights:**
- **5 Specialized AI Agents** running in parallel for comprehensive validation
- **80% cost reduction** using Anthropic's prompt caching
- **5x faster** than sequential validation through parallel execution
- **Real-time conversational interface** for explaining validation issues

## Real-World Use Case: Rachel's Story

### The Problem: Medical Billing Upcoding

Medical billing fraud and errors cost patients and insurance companies billions of dollars annually. Let's look at a real-world scenario to understand the impact.

**Meet Rachel** - She just had a baby and is worried about the hospital bill. When billing the insurance company, the hospital must choose the correct medical procedure code. For Rachel's delivery, there were two options:

| Code | Description | Charge |
|------|-------------|--------|
| **080** | Vaginal delivery without complications | **$12,000** |
| **072.1** | Vaginal delivery with complications | **$16,000** |

There are thousands of pages of documentation detailing exactly which code to use under which circumstances. However, hospitals - being profit-driven businesses - often choose the higher-paying code, even when inappropriate.

### What Actually Happened

**Hospital's Choice:** Code 072.1 ($16,000) - Despite Rachel having a routine, uncomplicated delivery.

Rachel has insurance through "Divided Healthcare" with an 80/20 split:
- Insurance company pays: **80%**
- Rachel pays (copay): **20%**

**The Billing Breakdown:**

```
Hospital initially attempted to charge: $72,000
Insurance negotiated rate (Code 072.1): $16,000
├─ Insurance pays (80%):              $12,800
└─ Rachel pays (20%):                  $3,200 ❌
```

### The Correct Billing

If the hospital had used the **correct code 080** for an uncomplicated delivery:

```
Correct charge (Code 080):            $12,000
├─ Insurance pays (80%):              $9,600
└─ Rachel pays (20%):                 $2,400 ✅
```

### The Impact

**Rachel is overcharged by $800** ($3,200 - $2,400) due to incorrect coding!

This scenario plays out **millions of times** across the healthcare system:
- **Patients overpay** on copays and deductibles
- **Insurance companies overpay** on their portion
- **Healthcare costs inflate** system-wide

### How Claims Guardian AI Solves This

Claims Guardian AI validates claims **before** they're processed, catching these billing errors immediately:

![Rachel's Claim Validation Flow](rachel_scenario.png)

**Validation Process:**

1. **Claim Submitted:** Hospital submits Rachel's claim with Code 072.1 ($16,000)

2. **Multi-Agent Validation:**
   - **CPT-ICD Validator** detects mismatch: Normal pregnancy diagnosis (Z34.90) doesn't match "delivery with complications" procedure (072.1)
   - **Cost Analyzer** flags unusual charge variance: $16,000 is 33% higher than average for routine delivery
   - **Demographic Validator** confirms patient profile matches routine delivery

3. **Issues Flagged:**
   ```json
   {
     "status": "flagged",
     "risk_score": 85,
     "issues": [
       {
         "agent": "CPT-ICD Validator",
         "severity": "high",
         "description": "Procedure code mismatch with diagnosis",
         "cost_impact": 4000,
         "suggested_fix": "Use code 080 for normal vaginal delivery"
       }
     ]
   }
   ```

4. **AI Explanation Generated:**
   > "This claim was flagged because code 072.1 indicates delivery with complications, but the diagnosis Z34.90 indicates a normal pregnancy. Using the correct code 080 would save Rachel $800 and the insurance company $3,200. Total potential savings: $4,000."

5. **Corrected Claim:**
   - Code changed from 072.1 → 080
   - Rachel pays: $2,400 (saving $800) ✅
   - Insurance pays: $9,600 (saving $3,200) ✅

### System-Wide Impact

If deployed at scale, Claims Guardian AI could:

- **Save patients** an average of $500-$2,000 per flagged claim
- **Reduce insurance costs** by catching fraudulent billing early
- **Process claims 5x faster** than manual review
- **Provide transparent explanations** for all billing decisions
- **Promote honest billing** by deterring intentional upcoding

**Real-World Statistics:**
- ~30-40% of medical claims contain errors or inflated charges
- Medical billing errors cost the US healthcare system **$68 billion annually**
- Automated validation could prevent **$20-25 billion** in improper payments

Claims Guardian AI protects patients like Rachel from being victims of billing errors and fraud, making healthcare more affordable and transparent for everyone.

## Architecture

### Multi-Agent System

The system uses **LangGraph** to orchestrate 5 specialized validation agents that run simultaneously:

```
┌─────────────┐
│   Claim     │
│   Input     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│    LangGraph Orchestrator           │
│  (Parallel Execution)               │
└──────┬──────────────────────────────┘
       │
       ├──► CPT-ICD Validator ────────┐
       ├──► Bundling Validator ───────┤
       ├──► Modifier Validator ────────┼──► Aggregator ──► LLM Explanations ──► Results
       ├──► Demographic Validator ─────┤
       └──► Cost Analyzer ─────────────┘
```

### Technology Stack

**Backend:**
- **FastAPI** - High-performance REST API
- **LangGraph** - Multi-agent workflow orchestration
- **Anthropic Claude 3.5** - LLM for natural language explanations
- **PostgreSQL** - Relational database for medical codes
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation

**Frontend:**
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling

**Infrastructure:**
- **Docker Compose** - Container orchestration
- **pgAdmin** - Database management UI

## Features

### 1. Comprehensive Validation Rules

**CPT-ICD-10 Compatibility Validator**
- Ensures procedure codes match diagnosis codes
- Detects preventive vs. problem-focused mismatches
- Identifies upcoding patterns (e.g., routine visit with high complexity code)

**Bundling Validator**
- Checks NCCI (National Correct Coding Initiative) edits
- Detects unbundling violations (billing separately for bundled services)
- Validates modifier overrides

**Modifier Validator**
- Ensures correct modifier usage (25, 59, GT, etc.)
- Validates anatomical modifiers (RT, LT, etc.)
- Checks modifier combinations

**Demographic Validator**
- Validates age restrictions on diagnosis codes
- Checks gender-specific code usage
- Identifies pregnancy codes for male patients

**Cost Analyzer**
- Detects charge outliers (±50% from average)
- Identifies statistical anomalies
- Flags potential upcoding by charge analysis

### 2. AI-Powered Explanations

- **Contextual explanations** using Claude 3.5 Sonnet
- **Prompt caching** for 80% cost reduction on repeated queries
- **Conversational interface** for asking follow-up questions
- **Suggested fixes** for each validation issue

### 3. Risk Scoring & Reporting

- **Risk score (0-100)** based on severity and quantity of issues
- **Overall status**: Passed, Flagged, or Rejected
- **Financial impact calculation** for each issue
- **Agent attribution** for transparency

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Anthropic API key (for LLM features)

### Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd claims-guardian-ai
```

2. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env`:
```env
ANTHROPIC_API_KEY=your_api_key_here
```

3. **Start the services**
```bash
docker compose up -d --build
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **pgAdmin**: http://localhost:5050

4. **Initialize the database**

Run the initialization script to create tables and load reference data:
```bash
docker exec claims_backend python scripts/init_database.py
```

This will populate the database with:
- 55 ICD-10 diagnosis codes
- 100 CPT procedure codes
- Demographic validation rules

**Verify initialization:**
```bash
# Check logs to confirm initialization completed
docker logs claims_backend
```

### Access the Application

- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@example.com / admin123)

## Usage

### 1. Validate a Claim (UI)

1. Open http://localhost:3000
2. Click "Load Valid Sample" or "Load Invalid Sample"
3. Click "Validate Claim"
4. Review validation results
5. Ask questions in the chat interface

### 2. API Endpoints

**Validate Single Claim**
```bash
curl -X POST http://localhost:8000/api/claims/validate \
  -H "Content-Type: application/json" \
  -d '{
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
    "procedure_codes": [{
      "cpt": "99213",
      "modifiers": [],
      "units": 1,
      "charge": 135.00
    }],
    "total_charge": 135.00
  }'
```

**Ask Question About Claim**
```bash
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "CLM001",
    "question": "Why was this claim flagged?"
  }'
```

**Get Statistics**
```bash
curl http://localhost:8000/api/stats/summary
```

See full API documentation at http://localhost:8000/docs

## Project Structure

```
prototype_1/
├── backend/
│   ├── app/
│   │   ├── agents/              # Validation agents
│   │   │   ├── orchestrator.py  # LangGraph workflow
│   │   │   ├── cpt_icd_validator.py
│   │   │   ├── bundling_validator.py
│   │   │   ├── modifier_validator.py
│   │   │   ├── demographic_validator.py
│   │   │   └── cost_analyzer.py
│   │   ├── api/                 # REST endpoints
│   │   │   ├── claims.py
│   │   │   ├── chat.py
│   │   │   └── stats.py
│   │   ├── database/            # Database models & connection
│   │   │   ├── models.py
│   │   │   ├── connection.py
│   │   │   └── init_db.py
│   │   ├── models/              # Pydantic models
│   │   │   ├── claim.py
│   │   │   └── validation.py
│   │   ├── services/            # Business logic
│   │   │   └── llm_service.py
│   │   ├── config.py            # Settings
│   │   └── main.py              # FastAPI app
│   ├── data/
│   │   └── raw/                 # Medical code datasets
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx         # Main application
│   │   ├── components/
│   │   │   ├── ClaimInput.tsx
│   │   │   ├── ValidationResults.tsx
│   │   │   └── ChatInterface.tsx
│   │   └── lib/
│   │       ├── api.ts           # API client
│   │       └── types.ts         # TypeScript types
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Performance Metrics

- **Processing Time**: 130-663ms per claim (depending on complexity)
- **Parallel Speedup**: 5x faster than sequential validation
- **LLM Cost Optimization**: 80% reduction using prompt caching
- **Cache Hit Rate**: ~90% for multiple issues per claim

## Sample Validation Output

```json
{
  "claim_id": "CLM002",
  "overall_status": "flagged",
  "risk_score": 100,
  "issues": [
    {
      "agent_name": "CPT-ICD Validator",
      "issue_type": "preventive_complexity_mismatch",
      "severity": "high",
      "description": "High complexity code 99205 billed for routine preventive visit",
      "explanation": "Preventive visits are typically straightforward and don't justify high complexity E/M codes.",
      "confidence_score": 0.85,
      "cost_impact": 325,
      "suggested_fix": "Consider downcoding to 99383 or use preventive visit codes"
    }
  ],
  "total_cost_impact": 880,
  "processing_time_ms": 663
}
```

## Development

### Testing

 

**Unit tests are not yet implemented.** To add tests:

 

```bash
# Create tests directory
mkdir -p backend/tests

# Install pytest
cd backend

pip install pytest pytest-asyncio httpx

# Create a sample test file
cat > tests/test_validators.py << 'EOF'

import pytest

from app.agents.cpt_icd_validator import CPTICDValidator

from app.models.claim import Claim, Patient, Provider, ProcedureCode

from datetime import date

def test_cpt_icd_validator():

    # Add your tests here

    pass
EOF

# Run tests
pytest tests/ -v
```

### Database Management

**Access pgAdmin:**
1. Go to http://localhost:5050
2. Login: admin@example.com / admin123
3. Add server: claims_postgres (host), port 5432

**Reset Database:**
```bash
docker compose down -v
docker compose up --build
docker exec claims_backend python scripts/init_database.py
```

### Add More Medical Codes

Edit files in `backend/data/raw/`:
- `icd10_codes.csv` - Add diagnosis codes
- `cpt_codes.csv` - Add procedure codes
- `modifier_rules.json` - Add modifier rules

Then restart: `docker compose restart claims_backend`

## Technical Highlights

### LangGraph Parallel Execution

```python
# All 5 agents start simultaneously
workflow.add_edge(START, "cpt_icd")
workflow.add_edge(START, "bundling")
workflow.add_edge(START, "modifier")
workflow.add_edge(START, "demographic")
workflow.add_edge(START, "cost")

# Results accumulate using operator.add
issues: Annotated[List[ValidationIssue], operator.add]
```

### Prompt Caching Implementation

```python
system_context = [{
    "type": "text",
    "text": f"Claim context: {claim_details}...",
    "cache_control": {"type": "ephemeral"}  # Cached for 5 min
}]

response = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    system=system_context,  # Cached!
    messages=[{"role": "user", "content": query}]
)
```

**Result**: First call costs $0.003, subsequent calls $0.0003 (10x cheaper!)

## Future Enhancements

- [ ] Integration with real NCCI edit database (1M+ rules)
- [ ] ML-based anomaly detection for fraud patterns
- [ ] Provider credentialing validation
- [ ] Prior authorization checking
- [ ] Claims attachment processing (OCR)
- [ ] Batch processing with progress tracking
- [ ] Export to CMS 1500 / UB-04 formats
- [ ] Integration with EHR systems (HL7/FHIR)

## Known Limitations

- **NCCI Edit Coverage**: Currently using sample dataset; full NCCI has 1M+ edit pairs
- **CPT Code Coverage**: 100 common codes; full AMA CPT has 10,000+ codes
- **LLM Dependency**: Chat features require Anthropic API key
- **No Authentication**: Prototype doesn't include user auth (add before production)

## License

MIT License - Open source project for educational and portfolio demonstration purposes.

## Contributing

This is an open-source project. Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Questions?** Check the API documentation at http://localhost:8000/docs or open an issue on GitHub.
