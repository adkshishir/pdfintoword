import type { Metadata } from "next";
import { SeoLanding } from "@/components/SeoLanding";

export const metadata: Metadata = {
  title: "Preserve Formatting PDF to Word | PDFintoWord",
  description:
    "Convert PDF to Word without losing layout. Headers, footers, tables, images, and spacing stay intact.",
};

export default function PreserveFormattingPage() {
  return (
    <SeoLanding
      title="Preserve Formatting PDF to Word"
      description="Maintain visual hierarchy, reading order, and structural elements from your original PDF in every Word export."
      faqs={[
        {
          question: "What formatting is preserved?",
          answer:
            "Layout blocks, tables, embedded images, headings, lists, page breaks, and spacing relationships.",
        },
      ]}
    />
  );
}
