from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.services.ingestion_service import DocumentIngestionService
from app.services.transcription_service import TranscriptionService
from app.models.document import Document
from app.models.transcript import Transcript
from app.schemas.ingestion import DocumentOut, TranscriptOut, DocumentDetailOut
from app.utils.files import save_upload

router = APIRouter()

@router.post('/{patient_id}/uploads', response_model=DocumentOut)
async def upload_document(patient_id: int, file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    """Upload a document (PDF/image/text). Extracts text if available."""
    content = await file.read()
    path, extracted = DocumentIngestionService().save_and_extract(file.filename, content, file.content_type or 'application/octet-stream')
    doc = Document(patient_id=patient_id, file_path=path, mime_type=file.content_type or 'application/octet-stream', extracted_text=extracted)
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentOut(document_id=doc.id, extracted_text=doc.extracted_text)

@router.get('/{patient_id}/uploads', response_model=list[DocumentOut])
async def list_documents(patient_id: int, session: AsyncSession = Depends(get_session)):
    """List uploaded documents for a patient."""
    docs = (await session.execute(select(Document).where(Document.patient_id == patient_id))).scalars().all()
    return [DocumentOut(document_id=d.id, extracted_text=d.extracted_text) for d in docs]

@router.get('/{patient_id}/uploads/detail', response_model=list[DocumentDetailOut])
async def list_documents_detail(patient_id: int, session: AsyncSession = Depends(get_session)):
    """List uploaded documents with text availability and a short preview."""
    docs = (await session.execute(select(Document).where(Document.patient_id == patient_id))).scalars().all()
    items: list[DocumentDetailOut] = []
    for d in docs:
        text = d.extracted_text or ''
        items.append(DocumentDetailOut(
            document_id=d.id,
            mime_type=d.mime_type,
            has_text=bool(text.strip()),
            text_preview=text[:300] if text else None,
        ))
    return items

@router.post('/{patient_id}/audio', response_model=TranscriptOut)
async def upload_audio(patient_id: int, file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    """Upload audio and transcribe via Whisper."""
    content = await file.read()
    audio_path = save_upload(content, file.filename)
    text = TranscriptionService().transcribe(audio_path)
    tr = Transcript(patient_id=patient_id, audio_path=audio_path, text=text)
    session.add(tr)
    await session.commit()
    await session.refresh(tr)
    return TranscriptOut(transcript_id=tr.id, text=tr.text)

@router.post('/{patient_id}/uploads/reprocess', response_model=list[DocumentOut])
async def reprocess_documents(patient_id: int, session: AsyncSession = Depends(get_session)):
    """Re-run extraction for documents that have no extracted text."""
    docs = (await session.execute(select(Document).where(Document.patient_id == patient_id))).scalars().all()
    svc = DocumentIngestionService()
    updated: list[DocumentOut] = []
    for doc in docs:
        if doc.extracted_text and doc.extracted_text.strip():
            updated.append(DocumentOut(document_id=doc.id, extracted_text=doc.extracted_text))
            continue
        extracted = svc.extract_from_path(doc.file_path, doc.mime_type)
        if extracted and extracted.strip():
            doc.extracted_text = extracted
            session.add(doc)
        updated.append(DocumentOut(document_id=doc.id, extracted_text=doc.extracted_text))
    await session.commit()
    return updated
