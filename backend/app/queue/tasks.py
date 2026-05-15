import logging
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.enums import JobStatus
from app.models.job import Job
from app.pipeline.orchestrator import run_conversion
from app.queue.celery_app import celery_app
from app.services.job_service import delete_job_files_sync, output_key_for_job
from app.storage.sync import storage_get_sync, storage_put_sync

logger = logging.getLogger(__name__)
settings = get_settings()

sync_engine = create_engine(settings.sync_database_url)
SyncSession = sessionmaker(bind=sync_engine)


def _get_job(session: Session, job_id: uuid.UUID) -> Job | None:
    return session.get(Job, job_id)


def _update_progress(session: Session, job: Job, progress: int, message: str) -> None:
    job.progress = progress
    job.progress_message = message
    session.commit()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def convert_pdf_task(self, job_id: str) -> None:
    job_uuid = uuid.UUID(job_id)
    start = time.time()

    with SyncSession() as session:
        job = _get_job(session, job_uuid)
        if not job:
            logger.error("Job %s not found", job_id)
            return

        if job.status == JobStatus.COMPLETED:
            return

        job.status = JobStatus.PROCESSING
        job.progress = 5
        job.progress_message = "Loading PDF"
        session.commit()

        try:
            pdf_bytes = storage_get_sync(job.input_key)

            _update_progress(session, job, 20, "Detecting PDF type")
            result = run_conversion(pdf_bytes, job.mode)

            _update_progress(session, job, 80, "Generating DOCX")
            output_key = output_key_for_job(job_uuid)
            storage_put_sync(output_key, result.docx_bytes)

            job.status = JobStatus.COMPLETED
            job.output_key = output_key
            job.pdf_type = result.pdf_type
            job.ocr_used = result.ocr_used
            job.page_count = result.page_count
            job.progress = 100
            job.progress_message = "Completed"
            job.processing_time_ms = int((time.time() - start) * 1000)
            job.completed_at = datetime.now(timezone.utc)
            session.commit()
            logger.info("Job %s completed in %sms", job_id, job.processing_time_ms)

        except Exception as exc:
            logger.exception("Job %s failed: %s", job_id, exc)
            session.rollback()
            job = _get_job(session, job_uuid)
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(exc)[:2000]
                job.progress_message = "Failed"
                job.processing_time_ms = int((time.time() - start) * 1000)
                session.commit()
            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc) from exc


@celery_app.task
def expire_jobs_task() -> int:
    now = datetime.now(timezone.utc)
    expired_count = 0

    with SyncSession() as session:
        jobs = session.execute(
            select(Job).where(
                Job.expires_at < now,
                Job.status != JobStatus.EXPIRED,
            )
        ).scalars().all()

        for job in jobs:
            try:
                delete_job_files_sync(job)
            except Exception as exc:
                logger.warning("Failed to delete files for job %s: %s", job.id, exc)
            job.status = JobStatus.EXPIRED
            expired_count += 1

        session.commit()

    logger.info("Expired %s jobs", expired_count)
    return expired_count
