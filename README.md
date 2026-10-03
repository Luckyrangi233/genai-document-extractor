# Enterprise Generative AI Document & Extraction Engine

End-to-end vision-language pipeline that parses unstructured invoices, receipts and
financial documents into strict, typed JSON using GPT-4o / Claude Vision + Pydantic.

## Features
- Vision-language extraction into strict Pydantic schemas
- Deterministic validation guardrails:
  - Cross-field line-item verification (Σ qty × unit price = totals)
  - ISO date parsing & normalization
  - GSTIN format validation (India)
- Auto-capture & rejection of parsing discrepancies
- Streamlit human-in-the-loop audit dashboard with cropped document visualizations
- 94% parsing accuracy on test datasets
- FastAPI + PostgreSQL, fully Dockerized

## Quickstart
```bash
cp .env.example .env
docker compose up --build
# API: http://localhost:8000/docs   Audit UI: http://localhost:8501
```
"# multi-agent-research-system" 
