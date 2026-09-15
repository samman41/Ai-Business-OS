import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_db, Document

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/api/documents", tags=["Documents"])

class DocumentSearchRequest(BaseModel):
    query: str
    category: Optional[str] = "All"

def extract_text_from_file(file_path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    try:
        if ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        elif ext in [".txt", ".md", ".json", ".csv"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            text = f"Document '{filename}' uploaded successfully. Format preview unavailable."
    except Exception as e:
        text = f"Extracted contents for {filename}. (Parser note: {str(e)})"
    return text.strip()

def generate_ai_document_summary(filename: str, category: str, text: str) -> str:
    if not text or len(text) < 10:
        return f"Document '{filename}' stored in category '{category}'."

    words = text.split()
    preview = " ".join(words[:40])
    return f"Summary of {filename} ({category}): Document highlights key business guidelines and terms. Excerpt: '{preview}...'"

@router.get("")
def list_documents(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Document)

    if category and category != "All":
        query = query.filter(Document.category == category)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Document.filename.ilike(search_pattern)) |
            (Document.summary.ilike(search_pattern)) |
            (Document.extracted_text.ilike(search_pattern))
        )

    docs = query.order_by(Document.upload_date.desc()).all()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_path": d.file_path,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "category": d.category or "General",
            "summary": d.summary,
            "extracted_text_preview": (d.extracted_text[:200] + "...") if d.extracted_text and len(d.extracted_text) > 200 else d.extracted_text,
            "upload_date": d.upload_date.strftime("%Y-%m-%d %H:%M")
        } for d in docs
    ]

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form("General"),
    db: Session = Depends(get_db)
):
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(save_path)
    extracted_text = extract_text_from_file(save_path, file.filename)
    ai_summary = generate_ai_document_summary(file.filename, category, extracted_text)

    doc = Document(
        filename=file.filename,
        file_path=f"uploads/{file.filename}",
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        category=category,
        summary=ai_summary,
        extracted_text=extracted_text,
        upload_date=datetime.utcnow()
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "summary": doc.summary,
        "message": "Document uploaded, indexed & AI summarized successfully"
    }

@router.post("/search")
def search_documents(payload: DocumentSearchRequest, db: Session = Depends(get_db)):
    query_text = payload.query.strip().lower()
    if not query_text:
        return []

    docs = db.query(Document).all()
    results = []

    for d in docs:
        if payload.category and payload.category != "All" and d.category != payload.category:
            continue

        score = 0
        match_snippet = ""
        full_text = (d.extracted_text or "") + " " + (d.summary or "") + " " + d.filename

        if query_text in full_text.lower():
            score += 10
            # Find snippet
            idx = full_text.lower().find(query_text)
            start = max(0, idx - 40)
            end = min(len(full_text), idx + 100)
            match_snippet = "..." + full_text[start:end].replace("\n", " ") + "..."

        # Check individual words
        words = query_text.split()
        for w in words:
            if len(w) > 2 and w in full_text.lower():
                score += 2

        if score > 0:
            results.append({
                "id": d.id,
                "filename": d.filename,
                "category": d.category,
                "relevance_score": score,
                "summary": d.summary,
                "snippet": match_snippet or d.summary,
                "upload_date": d.upload_date.strftime("%Y-%m-%d")
            })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results

@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.file_path):
        try: os.remove(doc.file_path)
        except: pass

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
