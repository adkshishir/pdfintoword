import type { Metadata } from "next";
import { SeoLanding } from "@/components/SeoLanding";

export const metadata: Metadata = {
  title: "Scanned PDF to Word — OCR Conversion | PDFintoWord",
  description:
    "Convert scanned PDFs to editable Word with OCR. PaddleOCR and Tesseract extract text while preserving document structure.",
};

const faqs = [
  {
    question: "Can you convert scanned PDFs?",
    answer:
      "Yes. Use Accurate mode to enable OCR with PaddleOCR and Tesseract fallback for scanned and image-based PDFs.",
  },
  {
    question: "Does OCR work on handwritten PDFs?",
    answer:
      "Handwritten content is supported in OCR mode, though accuracy depends on scan quality and legibility.",
  },
];

export default function ScannedPdfPage() {
  return (
    <SeoLanding
      title="Scanned PDF to Word"
      description="Turn scanned documents and image-based PDFs into editable Word files using intelligent OCR and layout reconstruction."
      faqs={faqs}
    />
  );
}
