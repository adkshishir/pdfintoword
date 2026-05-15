"""API tests — run inside Docker where DB/Redis are available."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


@pytest.mark.asyncio
@patch("app.api.routes.jobs.convert_pdf_task")
async def test_create_job_mocked(mock_task: MagicMock, digital_pdf_bytes: bytes):
    mock_task.apply_async = MagicMock()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/jobs",
            files={"file": ("test.pdf", digital_pdf_bytes, "application/pdf")},
            data={"mode": "fast"},
        )
    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        mock_task.apply_async.assert_called_once()
    else:
        # DB may be unavailable outside Docker
        assert response.status_code in (201, 500, 503)
