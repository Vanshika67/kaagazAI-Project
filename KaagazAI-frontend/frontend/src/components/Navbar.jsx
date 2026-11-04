import { useState } from "react";
import { Link } from "react-router-dom";
import { NAV_SECTIONS } from "../config/navConfig";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950 shadow-lg shadow-black/20">
      <div className="flex items-center justify-between px-4 py-3">
        <Link to="/" className="flex items-center gap-2 text-xl font-extrabold text-white">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-linear-to-br from-amber-300 via-pink-500 to-sky-500 text-slate-950">K</span>
          <span>
            Kaagaz<span className="bg-linear-to-r from-amber-300 to-pink-400 bg-clip-text text-transparent">AI</span>
          </span>
        </Link>
        <button type="button" onClick={() => setOpen((o) => !o)} className="rounded-lg px-3 py-2 text-white hover:bg-white/10 md:hidden" aria-label="Menu">
          {open ? "✕" : "☰"}
        </button>
      </div>

      {open && (
        <nav className="max-h-[70vh] overflow-y-auto border-t border-white/10 px-4 py-3 md:hidden">
          {NAV_SECTIONS.map((s) => (
            <div key={s.title} className="mb-4">
              <h4 className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-500">{s.title}</h4>
              {s.items.map((i) =>
                i.soon ? (
                  <span key={i.label} className="block px-2 py-2 text-sm text-slate-500">{i.label} (Soon)</span>
                ) : (
                  <Link key={i.label} to={i.path} onClick={() => setOpen(false)} className="block rounded-lg px-2 py-2 text-sm text-slate-200 hover:bg-white/5">
                    {i.label}
                  </Link>
                )
              )}
            </div>
          ))}
        </nav>
      )}
    </header>
  );
}