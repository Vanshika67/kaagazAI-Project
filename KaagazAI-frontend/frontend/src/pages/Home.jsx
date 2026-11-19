import { useState } from "react";
import { Link } from "react-router-dom";
import ToolCard from "../components/ToolCard";
import { CATEGORIES, TOOLS } from "../config/tools";
import { WORKFLOW_TOOLS } from "../config/workflowTools";
import { THEMES, themeForCategory } from "../config/theme";
import { COMING_SOON } from "../config/comingSoon";

// Ye tool alag page par hai, grid mein dobara nahi dikhega
const HIDDEN_IDS = ["handwriting", "chat-pdf"];
const LIST = TOOLS.filter((t) => !HIDDEN_IDS.includes(t.id) || t.id === "chat-pdf");

const STATS = [
  { label: "Total tools", value: TOOLS.length, icon: "🧰", theme: "blue" },
  { label: "Categories", value: CATEGORIES.length, icon: "🗂️", theme: "green" },
  { label: "Tools you can chain", value: Object.keys(WORKFLOW_TOOLS).length, icon: "⛓️", theme: "fuchsia" },
  { label: "Files auto-deleted in", value: "1 hr", icon: "🛡️", theme: "yellow" },
];

const FEATURED = [
  { to: "/workflow", icon: "⛓️", name: "Workflow Builder", tag: "Unique", theme: "fuchsia",
    text: "Pick several tools, set their order, and run them all on one PDF in a single go." },
  { to: "/page-manager", icon: "🧩", name: "Page Manager", tag: "Unique", theme: "cyan",
    text: "Reorder, delete and insert pages, even from other PDFs, in one step." },
  { to: "/handwriting", icon: "✍️", name: "Handwriting Notes / Assignment Helper", tag: "New", theme: "yellow",
    text: "Question aur answer daalo, apna handwriting font lagao, apni writing mein PDF pao." },
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [active, setActive] = useState("all");
  const q = query.trim().toLowerCase();
  const matches = (t) => !q || (t.name + " " + t.description).toLowerCase().includes(q);
  const visibleCategories = active === "all" ? CATEGORIES : CATEGORIES.filter((c) => c.id === active);
  const anyMatch = LIST.some(matches);

  return (
    <div className="relative min-h-screen overflow-hidden bg-linear-to-b from-indigo-950 via-slate-950 to-slate-950 text-white">
      <div className="pointer-events-none absolute -left-32 top-0 h-96 w-96 rounded-full bg-blue-600/20 blur-3xl" />
      <div className="pointer-events-none absolute -right-32 top-40 h-96 w-96 rounded-full bg-fuchsia-600/20 blur-3xl" />

      <div className="relative mx-auto max-w-6xl px-4 py-10">
        {/* ---------- hero ---------- */}
        <section className="relative py-10 text-center">
          <span className="float-a absolute left-2 top-4 text-5xl opacity-90 sm:left-10">📄</span>
          <span className="float-b absolute right-2 top-2 text-5xl opacity-90 sm:right-10">🔒</span>
          <span className="float-c absolute bottom-10 left-6 hidden text-4xl sm:block">⚡</span>
          <span className="float-a absolute bottom-6 right-12 hidden text-5xl sm:block">🖼️</span>
          <span className="float-b absolute left-1/4 top-0 hidden text-3xl sm:block">✍️</span>

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
        <section className="mt-6 grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
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
            <div className="grid gap-4 lg:grid-cols-3">
              {FEATURED.map((f) => (
                <Link key={f.to} to={f.to}
                  className={`group relative overflow-hidden rounded-3xl bg-linear-to-br ${THEMES[f.theme].gradient} p-6 shadow-xl transition duration-300 hover:-translate-y-1 hover:shadow-2xl`}>
                  <div className="pointer-events-none absolute -right-8 -top-8 h-40 w-40 rounded-full bg-white/20 transition duration-500 group-hover:scale-125" />
                  <div className="pointer-events-none absolute -bottom-10 right-20 h-28 w-28 rounded-full bg-black/10" />
                  <span className="relative inline-block rounded-full bg-white/25 px-3 py-1 text-xs font-bold uppercase tracking-wider">{f.tag}</span>
                  <div className="relative mt-3 text-5xl">{f.icon}</div>
                  <h3 className="relative mt-3 text-xl font-extrabold">{f.name}</h3>
                  <p className="relative mt-1 text-white/90">{f.text}</p>
                  <span className="relative mt-4 inline-block font-semibold">Try it →</span>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* ---------- category pills ---------- */}
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
          const tools = LIST.filter((t) => t.category === cat.id && matches(t));
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