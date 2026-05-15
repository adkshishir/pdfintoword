const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type ConversionMode = "fast" | "accurate";

export type JobStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "expired";

export interface Job {
  id: string;
  status: JobStatus;
  mode: ConversionMode;
  page_count: number | null;
  pdf_type: string | null;
  ocr_used: boolean;
  progress: number;
  progress_message: string | null;
  error_message: string | null;
  processing_time_ms: number | null;
  created_at: string;
  expires_at: string;
  completed_at: string | null;
}

export async function createJob(file: File, mode: ConversionMode): Promise<Job> {
  const form = new FormData();
  form.append("file", file);
  form.append("mode", mode);

  const res = await fetch(`${API_URL}/api/v1/jobs`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Upload failed");
  }

  return res.json();
}

export async function getJob(jobId: string): Promise<Job> {
  const res = await fetch(`${API_URL}/api/v1/jobs/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

export function downloadUrl(jobId: string): string {
  return `${API_URL}/api/v1/jobs/${jobId}/download`;
}
