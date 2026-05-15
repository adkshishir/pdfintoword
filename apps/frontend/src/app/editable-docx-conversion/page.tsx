import type { Metadata } from "next";
import { SeoLanding } from "@/components/SeoLanding";

export const metadata: Metadata = {
  title: "Editable DOCX Conversion | PDFintoWord",
  description: "Get fully editable DOCX files from PDF with tables, headings, lists, and images preserved.",
};

export default function EditableDocxPage() {
  return (
    <SeoLanding
      title="Editable DOCX Conversion"
      description="Every conversion produces a native Word document you can edit — not a flat image or plain text dump."
      faqs={[
        {
          question: "What makes the DOCX editable?",
          answer:
            "We rebuild document structure with real paragraphs, headings, tables, and images using python-docx.",
        },
      ]}
    />
  );
}
