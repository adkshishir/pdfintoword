import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models.enums import ConversionMode, JobStatus
from app.models.job import Job
from app.queue.tasks import convert_pdf_task
from app.services.job_service import create_job, delete_job_files, get_job
from app.services.validation import ValidationError, malware_scan_stub, validate_pdf_content
from app.storage import get_storage

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])
limiter = Limiter(key_func=get_remote_address)


class JobResponse(BaseModel):
    id: uuid.UUID
    status: JobStatus
    mode: ConversionMode
    page_count: int | None
    pdf_type: str | None
    ocr_used: bool
    progress: int
    progress_message: str | None
    error_message: str | None
    processing_time_ms: int | None
    created_at: str
    expires_at: str
    completed_at: str | None

    model_config = {"from_attributes": True}


def _job_to_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        status=job.status,
        mode=job.mode,
        page_count=job.page_count,
        pdf_type=job.pdf_type.value if job.pdf_type else None,
        ocr_used=job.ocr_used,
        progress=job.progress,
        progress_message=job.progress_message,
        error_message=job.error_message,
        processing_time_ms=job.processing_time_ms,
        created_at=job.created_at.isoformat() if job.created_at else "",
        expires_at=job.expires_at.isoformat() if job.expires_at else "",
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )


@router.post("", response_model=JobResponse, status_code=201)
@limiter.limit("10/minute")
async def create_conversion_job(
    request: Request,
    file: UploadFile = File(...),
    mode: ConversionMode = Form(ConversionMode.FAST),
    session: AsyncSession = Depends(get_session),
) -> JobResponse:
    data = await file.read()
    try:
        page_count = validate_pdf_content(data, file.content_type)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not malware_scan_stub(data):
        raise HTTPException(status_code=400, detail="File failed security check")

    job = await create_job(session, data, mode, page_count)

    queue_name = "accurate" if mode == ConversionMode.ACCURATE else "default"
    convert_pdf_task.apply_async(args=[str(job.id)], queue=queue_name)

    return _job_to_response(job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> JobResponse:
    job = await get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_response(job)


@router.get("/{job_id}/download")
async def download_job_output(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    job = await get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.COMPLETED or not job.output_key:
        raise HTTPException(status_code=400, detail="Job output not ready")

    storage = get_storage()
    try:
        data = await storage.get(job.output_key)
    except (FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=404, detail="Output file not found") from exc

    return StreamingResponse(
        BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{job_id}.docx"'},
    )


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    job = await get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await delete_job_files(job)
    await session.delete(job)
    await session.commit()
