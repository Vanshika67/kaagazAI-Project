import { useState } from "react";
import { Link } from "react-router-dom";
import ToolCard from "../components/ToolCard";
import { CATEGORIES, TOOLS } from "../config/tools";
import { WORKFLOW_TOOLS } from "../config/workflowTools";
import { THEMES, themeForCategory } from "../config/theme";

const STATS = [
  { label: "PDF tools", value: TOOLS.length, icon: "🧰", theme: "blue" },
  { label: "Categories", value: CATEGORIES.length, icon: "🗂️", theme: "green" },
  { label: "Tools you can chain", value: Object.keys(WORKFLOW_TOOLS).length, icon: "⛓️", theme: "fuchsia" },
  { label: "Files auto-deleted in", value: "1 hr", icon: "🛡️", theme: "yellow" },
];

const COMING_SOON = [
  { icon: "🤖", label: "AI Summarizer", theme: "cyan" },
  { icon: "🌍", label: "PDF Translation", theme: "green" },
  { icon: "📝", label: "Report Generator", theme: "yellow" },
  { icon: "🧠", label: "Concept Visualizer", theme: "rose" },
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [active, setActive] = useState("all");
  const q = query.trim().toLowerCase();
  const matches = (t) => !q || `${t.name} ${t.description}`.toLowerCase().includes(q);

  const visibleCategories = CATEGORIES.filter((c) => active === "all" || active === c.id);
  const anyMatch = TOOLS.some((t) => matches(t) && (active === "all" || t.category === active));

  return (
    <div className="relative isolate overflow-hidden bg-slate-950 text-white">
      {/* ---------- decorative background ---------- */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -left-24 -top-24 h-96 w-96 animate-float rounded-full bg-blue-600/30 blur-3xl" />
        <div className="absolute -right-24 top-40 h-96 w-96 animate-float rounded-full bg-fuchsia-600/25 blur-3xl [animation-delay:-3s]" />
        <div className="absolute left-1/3 top-[55%] h-80 w-80 animate-float rounded-full bg-amber-400/15 blur-3xl [animation-delay:-5s]" />
        <div className="absolute bottom-10 right-10 h-72 w-72 animate-float rounded-full bg-emerald-500/20 blur-3xl [animation-delay:-1s]" />
        <div className="bg-grid absolute inset-0" />
      </div>

      <div className="mx-auto max-w-6xl px-4 pb-16 pt-12">
        {/* ---------- hero ---------- */}
        <section className="relative text-center">
          {/* floating emoji decorations (desktop only) */}
          <span className="absolute left-4 top-2 hidden animate-float text-4xl lg:block">📄</span>
          <span className="absolute right-8 top-10 hidden animate-float text-4xl [animation-delay:-2s] lg:block">🔒</span>
          <span className="absolute left-24 top-44 hidden animate-float text-3xl [animation-delay:-4s] lg:block">⚡</span>
          <span className="absolute right-28 top-52 hidden animate-float text-3xl [animation-delay:-6s] lg:block">🖼️</span>

          <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-1.5 text-sm text-slate-200 backdrop-blur">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            {TOOLS.length} tools · free · private
          </span>

          <h1 className="mt-5 text-4xl font-black tracking-tight sm:text-6xl">
            Your PDFs,{" "}
            <span className="bg-linear-to-r from-amber-300 via-pink-400 to-sky-400 bg-clip-text text-transparent">
              supercharged
            </span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-300">
            Merge, split, convert, compress, secure and edit PDFs, or chain several tools into one workflow.
          </p>

          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="🔍  Search tools..."
            className="mx-auto mt-7 block w-full max-w-xl rounded-full border border-white/20 bg-white/10 px-6 py-3.5 text-white placeholder-slate-400 shadow-lg shadow-blue-500/10 outline-none backdrop-blur transition focus:border-sky-400 focus:ring-4 focus:ring-sky-400/20"
          />
        </section>

        {/* ---------- stats ---------- */}
        <section className="mt-10 grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
          {STATS.map((s) => {
            const t = THEMES[s.theme];
            return (
              <div key={s.label} className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <span className={`grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-linear-to-br ${t.gradient} text-2xl shadow-lg`}>{s.icon}</span>
                <div>
                  <div className={`bg-linear-to-r ${t.gradient} bg-clip-text text-2xl font-black text-transparent`}>{s.value}</div>
                  <div className="text-xs text-slate-400">{s.label}</div>
                </div>
              </div>
            );
          })}
        </section>

        {/* ---------- featured ---------- */}
        {!q && active === "all" && (
          <section className="mt-12">
            <h2 className="mb-4 text-lg font-bold">⭐ Featured</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {[
                { to: "/workflow", icon: "⛓️", name: "Workflow Builder", tag: "Unique", theme: "fuchsia",
                  text: "Pick several tools, set their order, and run them all on one PDF in a single go." },
                { to: "/page-manager", icon: "🧩", name: "Page Manager", tag: "Unique", theme: "cyan",
                  text: "Reorder, delete and insert pages, even from other PDFs, in one step." },
              ].map((f) => (
                <Link key={f.to} to={f.to}
                  className={`group relative overflow-hidden rounded-3xl bg-linear-to-br ${THEMES[f.theme].gradient} p-6 shadow-xl transition duration-300 hover:-translate-y-1 hover:shadow-2xl`}>
                  <div className="pointer-events-none absolute -right-8 -top-8 h-40 w-40 rounded-full bg-white/20 transition duration-500 group-hover:scale-125" />
                  <div className="pointer-events-none absolute -bottom-10 right-20 h-28 w-28 rounded-full bg-black/10" />
                  <span className="relative inline-block rounded-full bg-white/25 px-3 py-1 text-xs font-bold uppercase tracking-wider">{f.tag}</span>
                  <div className="relative mt-3 text-5xl">{f.icon}</div>
                  <h3 className="relative mt-3 text-2xl font-extrabold">{f.name}</h3>
                  <p className="relative mt-1 max-w-sm text-white/90">{f.text}</p>
                  <span className="relative mt-4 inline-block font-semibold">Try it →</span>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* ---------- category filter pills ---------- */}
        <section className="mt-12 flex flex-wrap gap-2">
          {[{ id: "all", name: "All tools", icon: "✨" }, ...CATEGORIES].map((c) => {
            const isActive = active === c.id;
            const gradient = c.id === "all" ? "from-slate-500 to-slate-700" : themeForCategory(c.id).gradient;
            return (
              <button key={c.id} type="button" onClick={() => setActive(c.id)}
                className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
                  isActive
                    ? `border-transparent bg-linear-to-r ${gradient} text-white shadow-lg`
                    : "border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"
                }`}>
                {c.icon} {c.name}
              </button>
            );
          })}
        </section>

        {/* ---------- tools by category ---------- */}
        {visibleCategories.map((cat) => {
          const tools = TOOLS.filter((t) => t.category === cat.id && matches(t));
          if (tools.length === 0) return null;
          const theme = themeForCategory(cat.id);
          return (
            <section key={cat.id} className="mt-10">
              <div className="mb-4 flex items-center gap-3">
                <span className={`grid h-10 w-10 place-items-center rounded-xl bg-linear-to-br ${theme.gradient} text-xl shadow-lg`}>{cat.icon}</span>
                <h2 className="text-xl font-bold">{cat.name}</h2>
                <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${theme.badge}`}>{tools.length}</span>
                <div className={`h-px flex-1 bg-linear-to-r ${theme.gradient} opacity-30`} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {tools.map((t) => (
                  <ToolCard key={t.id} to={`/tool/${t.id}`} icon={t.icon} name={t.name} description={t.description} theme={theme} />
                ))}
              </div>
            </section>
          );
        })}

        {!anyMatch && <p className="mt-12 text-center text-slate-400">No tools match "{query}".</p>}

        {/* ---------- coming soon ---------- */}
        {!q && active === "all" && (
          <section className="mt-14 rounded-3xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur">
            <h2 className="text-lg font-bold">🚀 Coming soon</h2>
            <p className="mt-1 text-sm text-slate-400">AI-powered features we are building next.</p>
            <div className="mt-4 flex flex-wrap justify-center gap-3">
              {COMING_SOON.map((c) => (
                <span key={c.label} className={`rounded-full px-4 py-2 text-sm font-semibold ${THEMES[c.theme].tile}`}>
                  {c.icon} {c.label}
                </span>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
