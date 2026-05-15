"use client";

import { Upload } from "lucide-react";
import { useCallback, useState } from "react";
import { cn } from "@/lib/utils";
import type { ConversionMode } from "@/lib/api";
import { useUploadStore } from "@/store/uploadStore";

const MODE_HINTS: Record<ConversionMode, string> = {
  fast: "Faster — keeps colors and text; lighter layout matching",
  accurate: "Best match — preserves layout, colors, backgrounds, and spacing like the PDF",
};

interface UploadZoneProps {
  onUpload: (file: File, mode: ConversionMode) => void;
  isLoading?: boolean;
}

export function UploadZone({ onUpload, isLoading }: UploadZoneProps) {
  const { mode, setMode, setFile } = useUploadStore();
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback(
    (file: File) => {
      if (file.type !== "application/pdf" && !file.name.endsWith(".pdf")) {
        alert("Please upload a PDF file");
        return;
      }
      setFile(file);
      onUpload(file, mode);
    },
    [mode, onUpload, setFile]
  );

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
        {(["accurate", "fast"] as ConversionMode[]).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={cn(
              "rounded-lg border px-4 py-2 text-sm font-medium capitalize transition-colors",
              mode === m
                ? "border-primary bg-primary/10 text-primary"
                : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
            )}
          >
            {m}
          </button>
        ))}
      </div>
      <p className="text-center text-sm text-slate-500">{MODE_HINTS[mode]}</p>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={cn(
          "flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-colors",
          dragOver ? "border-cta bg-cta/5" : "border-slate-300 bg-white"
        )}
      >
        <Upload className="mb-4 h-12 w-12 text-slate-400" />
        <p className="mb-2 text-lg font-medium text-slate-700">
          Drop your PDF here or click to browse
        </p>
        <p className="mb-4 text-sm text-slate-500">
          Layout, colors, tables, and images preserved in Word
        </p>
        <label className="cursor-pointer">
          <span className="rounded-lg bg-cta px-6 py-2 text-sm font-medium text-white hover:bg-primary">
            {isLoading ? "Uploading..." : "Select PDF"}
          </span>
          <input
            type="file"
            accept=".pdf,application/pdf"
            className="hidden"
            disabled={isLoading}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
            }}
          />
        </label>
      </div>
    </div>
  );
}
