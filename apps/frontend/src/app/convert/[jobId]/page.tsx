"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useJobStatus } from "@/hooks/useJobStatus";
import { Loader2, CheckCircle, XCircle } from "lucide-react";

export default function ConvertPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.jobId as string;
  const { data: job, isLoading } = useJobStatus(jobId);

  useEffect(() => {
    if (job?.status === "completed") {
      router.push(`/preview/${jobId}`);
    }
  }, [job?.status, jobId, router]);

  if (isLoading && !job) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const progress = job?.progress ?? 0;
  const isFailed = job?.status === "failed";

  return (
    <div className="mx-auto max-w-lg px-4 py-16">
      <h1 className="mb-8 text-center text-2xl font-bold">Converting your PDF</h1>

      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-4 flex items-center justify-center gap-2">
          {isFailed ? (
            <XCircle className="h-6 w-6 text-red-500" />
          ) : job?.status === "completed" ? (
            <CheckCircle className="h-6 w-6 text-success" />
          ) : (
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          )}
          <span className="font-medium capitalize">{job?.status ?? "loading"}</span>
        </div>

        <div className="mb-2 h-3 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-cta transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>

        <p className="text-center text-sm text-slate-600">
          {job?.progress_message ?? "Starting conversion..."}
        </p>

        {job?.ocr_used && (
          <p className="mt-2 text-center text-xs text-slate-500">OCR processing enabled</p>
        )}

        {isFailed && (
          <div className="mt-4 space-y-4">
            <p className="text-center text-sm text-red-600">{job?.error_message}</p>
            <Button variant="outline" className="w-full" onClick={() => router.push("/")}>
              Try again
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
