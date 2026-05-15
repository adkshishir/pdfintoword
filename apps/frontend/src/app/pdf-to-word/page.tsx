import type { Metadata } from "next";
import { SeoLanding } from "@/components/SeoLanding";

export const metadata: Metadata = {
  title: "PDF to Word Converter — Preserve Formatting | PDFintoWord",
  description:
    "Convert PDF to editable Word documents online. Preserve layout, tables, images, and typography with professional accuracy.",
};

const faqs = [
  {
    question: "How do I convert PDF to Word?",
    answer:
      "Upload your PDF, choose Fast or Accurate mode, and download your editable DOCX file in minutes.",
  },
  {
    question: "Will formatting be preserved?",
    answer:
      "Yes. PDFintoWord preserves paragraphs, tables, images, spacing, and page structure in the output document.",
  },
  {
    question: "Is the output editable?",
    answer: "Yes. The DOCX file opens in Microsoft Word, Google Docs, and LibreOffice for full editing.",
  },
];

export default function PdfToWordPage() {
  return (
    <SeoLanding
      title="PDF to Word Converter"
      description="Transform PDF files into fully editable Word documents while keeping your original layout intact. Ideal for contracts, reports, and business documents."
      faqs={faqs}
    />
  );
}
