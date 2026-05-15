import Link from "next/link";

export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link href="/" className="text-xl font-bold text-primary">
          PDFintoWord
        </Link>
        <nav className="flex gap-6 text-sm text-slate-600">
          <Link href="/pdf-to-word" className="hover:text-primary">
            PDF to Word
          </Link>
          <Link href="/scanned-pdf-to-word" className="hover:text-primary">
            Scanned PDF
          </Link>
        </nav>
      </div>
    </header>
  );
}
