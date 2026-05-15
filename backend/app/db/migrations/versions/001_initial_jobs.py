"""initial jobs table

Revision ID: 001
Revises:
Create Date: 2026-05-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    job_status = sa.Enum(
        "pending", "processing", "completed", "failed", "expired", name="job_status"
    )
    conversion_mode = sa.Enum("fast", "accurate", name="conversion_mode")
    pdf_type = sa.Enum("digital", "scanned", "mixed", name="pdf_type")
    job_status.create(op.get_bind(), checkfirst=True)
    conversion_mode.create(op.get_bind(), checkfirst=True)
    pdf_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", job_status, nullable=False, server_default="pending"),
        sa.Column("mode", conversion_mode, nullable=False, server_default="fast"),
        sa.Column("input_key", sa.String(512), nullable=False),
        sa.Column("output_key", sa.String(512), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("pdf_type", pdf_type, nullable=True),
        sa.Column("ocr_used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("progress_message", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_expires_at", "jobs", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_jobs_expires_at", table_name="jobs")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_table("jobs")
    sa.Enum(name="pdf_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="conversion_mode").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="job_status").drop(op.get_bind(), checkfirst=True)
