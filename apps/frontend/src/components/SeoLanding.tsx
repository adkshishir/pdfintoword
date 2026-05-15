import Link from "next/link";
import { Button } from "@/components/ui/button";

interface FaqItem {
  question: string;
  answer: string;
}

interface SeoLandingProps {
  title: string;
  description: string;
  faqs: FaqItem[];
}

export function SeoLanding({ title, description, faqs }: SeoLandingProps) {
  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((f) => ({
      "@type": "Question",
      name: f.question,
      acceptedAnswer: { "@type": "Answer", text: f.answer },
    })),
  };

  return (
    <article className="mx-auto max-w-3xl px-4 py-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <h1 className="mb-4 text-4xl font-bold text-slate-900">{title}</h1>
      <p className="mb-8 text-lg text-slate-600">{description}</p>
      <Link href="/">
        <Button>Convert PDF to Word</Button>
      </Link>

      <section className="mt-16">
        <h2 className="mb-6 text-2xl font-semibold">Frequently Asked Questions</h2>
        <div className="space-y-6">
          {faqs.map((faq) => (
            <div key={faq.question} className="rounded-lg border border-slate-200 bg-white p-6">
              <h3 className="font-semibold text-slate-900">{faq.question}</h3>
              <p className="mt-2 text-slate-600">{faq.answer}</p>
            </div>
          ))}
        </div>
      </section>
    </article>
  );
}
