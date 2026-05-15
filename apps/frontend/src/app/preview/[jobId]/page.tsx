"use client";

import { useParams } from "next/navigation";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { useJobStatus } from "@/hooks/useJobStatus";
import { downloadUrl } from "@/lib/api";
import { useUploadStore } from "@/store/uploadStore";
import { Download, ZoomIn, ZoomOut } from "lucide-react";

export default function PreviewPage() {
  const params = useParams();
  const jobId = params.jobId as string;
  const { data: job } = useJobStatus(jobId);
  const { file } = useUploadStore();
  const [zoom, setZoom] = useState(100);
  const [page, setPage] = useState(1);

  const pdfUrl = useMemo(() => {
    if (file) return URL.createObjectURL(file);
    return null;
  }, [file]);

  const totalPages = job?.page_count ?? 1;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Preview & Compare</h1>
        <a href={downloadUrl(jobId)} download={`${jobId}.docx`}>
          <Button>
            <Download className="mr-2 h-4 w-4" />
            Download DOCX
          </Button>
        </a>
      </div>

      <div className="mb-4 flex items-center gap-2">
        <Button variant="outline" className="text-sm px-2 py-1" onClick={() => setZoom((z) => Math.max(50, z - 10))}>
          <ZoomOut className="h-4 w-4" />
        </Button>
        <span className="text-sm text-slate-600">{zoom}%</span>
        <Button variant="outline" className="text-sm px-2 py-1" onClick={() => setZoom((z) => Math.min(200, z + 10))}>
          <ZoomIn className="h-4 w-4" />
        </Button>
        <span className="ml-4 text-sm text-slate-500">
          Page {page} of {totalPages}
        </span>
        <Button variant="outline" className="text-sm px-2 py-1" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          Prev
        </Button>
        <Button
          variant="outline"
          className="text-sm px-2 py-1"
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          Next
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <h2 className="mb-3 font-semibold text-slate-700">Original PDF</h2>
          <div
            className="flex min-h-[400px] items-center justify-center overflow-auto rounded-lg bg-slate-100 p-4"
            style={{ transform: `scale(${zoom / 100})`, transformOrigin: "top center" }}
          >
            {pdfUrl ? (
              <iframe src={pdfUrl} className="h-[500px] w-full" title="PDF preview" />
            ) : (
              <p className="text-slate-500 text-sm text-center">
                PDF preview available when uploaded from this session.
                <br />
                Download DOCX to view the converted document.
              </p>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <h2 className="mb-3 font-semibold text-slate-700">Word Output</h2>
          <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg bg-slate-50 p-8 text-center">
            <p className="mb-4 text-slate-600">
              Your DOCX is ready. Open in Microsoft Word or Google Docs for full editing.
            </p>
            {job?.processing_time_ms && (
              <p className="text-sm text-slate-500">
                Converted in {(job.processing_time_ms / 1000).toFixed(1)}s
                {job.ocr_used && " (with OCR)"}
              </p>
            )}
            <a href={downloadUrl(jobId)} className="mt-4" download={`${jobId}.docx`}>
              <Button variant="primary">Download Word Document</Button>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
