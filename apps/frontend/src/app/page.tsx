"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { UploadZone } from "@/components/UploadZone";
import { createJob, type ConversionMode } from "@/lib/api";
import { FileText, Table, Image, Zap } from "lucide-react";

export default function HomePage() {
  const router = useRouter();

  const upload = useMutation({
    mutationFn: ({ file, mode }: { file: File; mode: ConversionMode }) => createJob(file, mode),
    onSuccess: (job) => router.push(`/convert/${job.id}`),
  });

  return (
    <div className="mx-auto max-w-4xl px-4 py-16">
      <section className="mb-12 text-center">
        <h1 className="mb-4 text-4xl font-bold tracking-tight text-slate-900 md:text-5xl">
          Convert PDF to <span className="text-primary">Editable Word</span>
        </h1>
        <p className="mx-auto max-w-2xl text-lg text-slate-600">
          Preserve layout, tables, images, and formatting. Supports digital, scanned, and handwritten PDFs.
        </p>
      </section>

      <UploadZone
        isLoading={upload.isPending}
        onUpload={(file, mode) => upload.mutate({ file, mode })}
      />

      {upload.isError && (
        <p className="mt-4 text-center text-sm text-red-600">
          {(upload.error as Error).message}
        </p>
      )}

      <section className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { icon: FileText, title: "Layout preserved", desc: "Paragraphs, spacing, and hierarchy" },
          { icon: Table, title: "Editable tables", desc: "Rows, columns, and structure kept" },
          { icon: Image, title: "Images included", desc: "Logos, diagrams, and screenshots" },
          { icon: Zap, title: "Fast or Accurate", desc: "Choose speed or maximum fidelity" },
        ].map(({ icon: Icon, title, desc }) => (
          <div key={title} className="rounded-xl border border-slate-200 bg-white p-6">
            <Icon className="mb-3 h-8 w-8 text-primary" />
            <h3 className="font-semibold text-slate-900">{title}</h3>
            <p className="mt-1 text-sm text-slate-500">{desc}</p>
          </div>
        ))}
      </section>

      <p className="mt-8 text-center text-sm text-slate-500">
        Supported: PDF (digital, scanned, mixed) → DOCX
      </p>
    </div>
  );
}
