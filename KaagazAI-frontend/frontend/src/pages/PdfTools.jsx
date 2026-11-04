import { useState } from "react";
import ToolCard from "../components/ToolCard";
import { themeForCategory } from "../config/theme";
import { PDF_TOOLS, PDF_CATEGORIES } from "../config/toolGroups";

export default function PdfTools() {
  const [query, setQuery] = useState("");
  const [active, setActive] = useState("all");
  const q = query.trim().toLowerCase();
  const matches = (t) => !q || (t.name + " " + t.description).toLowerCase().includes(q);
  const cats = active === "all" ? PDF_CATEGORIES : PDF_CATEGORIES.filter((c) => c.id === active);

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-6xl px-4 py-10">
        <h1 className="text-3xl font-black">All PDF Tools</h1>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search PDF tools..."
          className="mt-5 block w-full max-w-xl rounded-full border border-white/20 bg-white/10 px-6 py-3 text-white placeholder-slate-400 outline-none focus:border-sky-400"
        />

        <div className="mt-6 flex flex-wrap gap-2">
          {[{ id: "all", name: "All", icon: "✨" }, ...PDF_CATEGORIES].map((c) => (
            <button key={c.id} type="button" onClick={() => setActive(c.id)}
              className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
                active === c.id ? "border-transparent bg-indigo-600 text-white" : "border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"
              }`}>
              {c.icon} {c.name}
            </button>
          ))}
        </div>

        {cats.map((cat) => {
          const tools = PDF_TOOLS.filter((t) => t.category === cat.id && matches(t));
          if (!tools.length) return null;
          const theme = themeForCategory(cat.id);
          return (
            <section key={cat.id} className="mt-10">
              <h2 className="mb-4 text-xl font-bold">{cat.icon} {cat.name}</h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {tools.map((t) => (
                  <ToolCard key={t.id} to={`/tool/${t.id}`} icon={t.icon} name={t.name} description={t.description} theme={theme} />
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}