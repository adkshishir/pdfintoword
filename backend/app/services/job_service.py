import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.enums import ConversionMode, JobStatus
from app.models.job import Job
from app.storage import get_storage


def input_key_for_job(job_id: uuid.UUID) -> str:
    return f"uploads/{job_id}/input.pdf"


def output_key_for_job(job_id: uuid.UUID) -> str:
    return f"outputs/{job_id}/output.docx"


async def create_job(
    session: AsyncSession,
    pdf_data: bytes,
    mode: ConversionMode,
    page_count: int,
) -> Job:
    settings = get_settings()
    job_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    job = Job(
        id=job_id,
        status=JobStatus.PENDING,
        mode=mode,
        input_key=input_key_for_job(job_id),
        page_count=page_count,
        expires_at=now + timedelta(hours=settings.job_ttl_hours),
        progress=0,
        progress_message="Queued",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    storage = get_storage()
    await storage.put(job.input_key, pdf_data)
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    result = await session.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def delete_job_files(job: Job) -> None:
    storage = get_storage()
    await storage.delete_prefix(f"uploads/{job.id}")
    await storage.delete_prefix(f"outputs/{job.id}")
    await storage.delete_prefix(f"tmp/{job.id}")


def delete_job_files_sync(job: Job) -> None:
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(delete_job_files(job))
