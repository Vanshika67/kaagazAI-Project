import { Link } from "react-router-dom";
import ToolCard from "../components/ToolCard";
import { THEMES } from "../config/theme";
import { getTool } from "../config/tools";
import { PDF_TOOLS } from "../config/toolGroups";

const tool = (id) => getTool(id);

const SECTIONS = [
  {
    title: "PDF Tools",
    theme: "blue",
    cards: [
      { to: "/pdf-tools", icon: "🧰", name: "All PDF Tools", description: `${PDF_TOOLS.length} tools: merge, split, compress, convert, secure, edit.` },
      { to: "/workflow", icon: "⛓️", name: "Workflow Builder", description: "Chain several tools and run them on one PDF." },
      { to: "/page-manager", icon: "🧩", name: "Page Manager", description: "Reorder, delete and insert pages in one step." },
    ],
  },
  {
    title: "Create",
    theme: "green",
    cards: [
      { to: "/tool/resume-builder?template_style=simple", icon: "📄", name: "Resume - Simple", description: "ATS-friendly, clean single column resume." },
      { to: "/tool/resume-builder?template_style=modern", icon: "🎨", name: "Resume - Modern", description: "Colorful 2-column resume with photo." },
      { soon: true, icon: "✍️", name: "Handwriting Notes", description: "Apni handwriting mein notes PDF." },
    ],
  },
  {
    title: "AI Tools",
    theme: "fuchsia",
    cards: [
      { to: "/tool/ai-summarize", icon: tool("ai-summarize").icon, name: "AI Summarization", description: tool("ai-summarize").description },
      { to: "/tool/ai-translate", icon: tool("ai-translate").icon, name: "AI Translation", description: tool("ai-translate").description },
      { to: "/tool/chat-pdf", icon: tool("chat-pdf").icon, name: "Chat with PDF", description: tool("chat-pdf").description },
      { to: "/tool/ai-extract", icon: tool("ai-extract").icon, name: "Extract Data", description: tool("ai-extract").description },
      { to: "/tool/hindi-ocr", icon: tool("hindi-ocr").icon, name: "Hindi / Scanned OCR", description: tool("hindi-ocr").description },
      { to: "/tool/handwriting", icon: "📓", name: "Handwriting Notes", description: "Apne handwriting font mein notes PDF." },
      { to: "/tool/ai-draft", icon: "📝", name: "AI Answer Draft", description: "Question se draft banao, edit karo, apni handwriting mein PDF." },
      { soon: true, icon: "🔭", name: "Context Visualizer", description: "Document ka context visually dekho." },
    ],
  },
];

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-6xl px-4 py-10">
        <h1 className="text-4xl font-black tracking-tight sm:text-5xl">
          Your PDFs,{" "}
          <span className="bg-linear-to-r from-amber-300 via-pink-400 to-sky-400 bg-clip-text text-transparent">supercharged</span>
        </h1>
        <p className="mt-3 max-w-2xl text-slate-300">Apna kaam chuno. Har category alag hai.</p>

        {SECTIONS.map((s) => {
          const theme = THEMES[s.theme];
          return (
            <section key={s.title} className="mt-10">
              <div className="mb-4 flex items-center gap-3">
                <h2 className="text-xl font-bold">{s.title}</h2>
                <div className={`h-px flex-1 bg-linear-to-r ${theme.gradient} opacity-30`} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {s.cards.map((c) =>
                  c.soon ? (
                    <div key={c.name} className="rounded-2xl border border-dashed border-white/15 bg-white/5 p-5 opacity-60">
                      <div className="text-3xl">{c.icon}</div>
                      <h3 className="mt-2 font-bold">{c.name} <span className="ml-1 rounded-full bg-white/10 px-2 py-0.5 text-[10px]">Soon</span></h3>
                      <p className="mt-1 text-sm text-slate-400">{c.description}</p>
                    </div>
                  ) : (
                    <ToolCard key={c.name} to={c.to} icon={c.icon} name={c.name} description={c.description} theme={theme} />
                  )
                )}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}