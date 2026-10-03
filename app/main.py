import io, uuid
from fastapi import FastAPI, UploadFile, HTTPException
from PIL import Image
from src.extractor import extract_invoice
from src.validators import validate_invoice
from src.db import SessionLocal, init_db, ExtractionRecord

app = FastAPI(title="GenAI Document Extraction Engine", version="1.0.0")
init_db()

@app.post("/extract")
async def extract(file: UploadFile):
    data = await file.read()
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(400, "File is not a readable image/PDF page render.")

    invoice = extract_invoice(image)                    # vision LLM → Pydantic
    report = validate_invoice(invoice)                  # deterministic guardrails

    record_id = str(uuid.uuid4())
    with SessionLocal() as db:
        db.add(ExtractionRecord(
            id=record_id,
            filename=file.filename,
            status="accepted" if report.valid else "needs_review",
            payload=invoice.model_dump_json(),
            issues="; ".join(report.issues),
        ))
        db.commit()
    return {
        "id": record_id,
        "status": "accepted" if report.valid else "needs_review",
        "invoice": invoice.model_dump(),
        "validation_issues": report.issues,
    }

@app.get("/records")
def list_records(needs_review: bool | None = None):
    with SessionLocal() as db:
        q = db.query(ExtractionRecord)
        if needs_review is not None:
            q = q.filter(ExtractionRecord.status == ("needs_review" if needs_review else "accepted"))
        return [{"id": r.id, "filename": r.filename, "status": r.status,
                 "issues": r.issues, "payload": r.payload} for r in q.all()]

@app.post("/records/{record_id}/approve")
def approve(record_id: str, corrected_payload: str | None = None):
    with SessionLocal() as db:
        rec = db.get(ExtractionRecord, record_id)
        if not rec:
            raise HTTPException(404, "record not found")
        rec.status = "accepted"
        if corrected_payload:
            rec.payload = corrected_payload
        db.commit()
    return {"status": "accepted"}

@app.get("/health")
def health():
    return {"status": "ok"}
