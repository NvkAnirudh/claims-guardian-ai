# Backend Setup

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and API keys
```

### 3. Initialize Database
```bash
python scripts/init_database.py
```

### 4. Run Server
```bash
uvicorn app.main:app --reload
```

Access at: http://localhost:8000/docs
