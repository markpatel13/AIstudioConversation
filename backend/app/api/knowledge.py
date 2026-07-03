"""Knowledge Base API routes – including file upload."""

from __future__ import annotations

import io

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import KnowledgeSource
from app.schemas.schemas import KnowledgeSourceCreate, KnowledgeSourceResponse

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])


# ── helpers ──────────────────────────────────────────────────────────────────


def _extract_text(upload: UploadFile) -> str:
    """
    Extract plain text from an uploaded file.

    Supported formats
    -----------------
    .txt, .md, .csv  – decoded as UTF-8 (fallback latin-1)
    .pdf             – extracted via PyPDF2 (installed automatically)
    .docx            – extracted via python-docx (installed automatically)
    everything else  – decoded as UTF-8 best-effort
    """
    filename = (upload.filename or "").lower()
    raw: bytes = upload.file.read()

    # ── PDF ──────────────────────────────────────────────────────────────
    if filename.endswith(".pdf"):
        try:
            import PyPDF2  # type: ignore

            reader = PyPDF2.PdfReader(io.BytesIO(raw))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages).strip()
        except ImportError:
            raise HTTPException(
                status_code=422,
                detail="PDF support requires PyPDF2. Add it to requirements.txt.",
            )
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"PDF parse error: {exc}")

    # ── DOCX ─────────────────────────────────────────────────────────────
    if filename.endswith(".docx"):
        try:
            import docx  # type: ignore

            doc = docx.Document(io.BytesIO(raw))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise HTTPException(
                status_code=422,
                detail="DOCX support requires python-docx. Add it to requirements.txt.",
            )
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"DOCX parse error: {exc}")

    # ── Plain text (TXT / MD / CSV / anything else) ───────────────────────
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace").strip()


# ── routes ───────────────────────────────────────────────────────────────────


@router.post("/", response_model=KnowledgeSourceResponse, status_code=201)
def create_knowledge_source(
    payload: KnowledgeSourceCreate, db: Session = Depends(get_db)
):
    """Create a knowledge source from a JSON body (manual text entry)."""
    source = KnowledgeSource(
        name=payload.name,
        content=payload.content,
        tags=payload.tags,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.post("/upload", response_model=KnowledgeSourceResponse, status_code=201)
def upload_knowledge_file(
    name: str = Form(...),
    tags: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a local file (.txt, .md, .pdf, .docx, .csv) as a knowledge source.
    The file content is extracted and stored as plain text.
    """
    content = _extract_text(file)
    if not content:
        raise HTTPException(status_code=422, detail="Could not extract any text from the file.")

    source = KnowledgeSource(
        name=name or file.filename or "Uploaded File",
        content=content,
        tags=tags or None,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/", response_model=list[KnowledgeSourceResponse])
def list_knowledge_sources(db: Session = Depends(get_db)):
    """List all knowledge sources."""
    return db.query(KnowledgeSource).order_by(KnowledgeSource.created_at.desc()).all()


@router.get("/{source_id}", response_model=KnowledgeSourceResponse)
def get_knowledge_source(source_id: int, db: Session = Depends(get_db)):
    """Get a single knowledge source by ID."""
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    return source


@router.delete("/{source_id}", status_code=204)
def delete_knowledge_source(source_id: int, db: Session = Depends(get_db)):
    """Delete a knowledge source."""
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    db.delete(source)
    db.commit()
