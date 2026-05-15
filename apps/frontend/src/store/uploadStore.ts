import { create } from "zustand";
import type { ConversionMode } from "@/lib/api";

interface UploadState {
  mode: ConversionMode;
  file: File | null;
  setMode: (mode: ConversionMode) => void;
  setFile: (file: File | null) => void;
  reset: () => void;
}

export const useUploadStore = create<UploadState>((set) => ({
  mode: "fast",
  file: null,
  setMode: (mode) => set({ mode }),
  setFile: (file) => set({ file }),
  reset: () => set({ mode: "fast", file: null }),
}));
