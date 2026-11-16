import { useState } from "react";
import { LANGUAGE_OPTIONS } from "../config/languages";

// Agar apiClient.js mein alag base URL hai to yahan wahi rakho
const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

const box =
  "w-full rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-white placeholder-slate-500 outline-none focus:border-indigo-400";

async function readError(res) {
  try {
    const j = await res.json();
    return j.detail || "Kuch galat ho gaya.";
  } catch {
    return "Kuch galat ho gaya.";
  }
}

export default function AiDraft() {
  const [question, setQuestion] = useState("");
  const [length, setLength] = useState("medium");
  const [language, setLanguage] = useState("English");
  const [draft, setDraft] = useState("");
  const [font, setFont] = useState(null);
  const [fontSize, setFontSize] = useState("18");
  const [ink, setInk] = useState("blue");
  const [maxPages, setMaxPages] = useState("0");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  const makeDraft = async () => {
    setBusy("draft");
    setError("");
    try {
      const fd = new FormData();
      fd.append("question", question);
      fd.append("length", length);
      fd.append("language", language);
      const res = await fetch(`${API}/api/tools/ai-draft`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(await readError(res));
      const data = await res.json();
      setDraft((prev) => (prev ? prev + "\n\n" : "") + `Q. ${question.trim()}\n${data.draft}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  };

  const makePdf = async () => {
    setBusy("pdf");
    setError("");
    try {
      const fd = new FormData();
      fd.append("text", draft);
      fd.append("font_size", fontSize);
      fd.append("ink", ink);
      fd.append("max_pages", maxPages);
      if (font) fd.append("font", font);
      const res = await fetch(`${API}/api/tools/handwriting`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(await readError(res));
      const blob = await res.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "handwriting_notes.pdf";
      a.click();
      URL.revokeObjectURL(a.href);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="text-3xl font-black">AI Answer Draft</h1>
        <p className="mt-2 text-slate-400">
          Question daalo, AI draft banayega. Draft padho, apne words mein edit karo, phir apne handwriting
          font mein PDF banao.
        </p>

        <section className="mt-6 space-y-3 rounded-2xl border border-white/10 bg-white/5 p-5">
          <h2 className="font-bold">1. Question</h2>
          <textarea rows={3} className={box} value={question} placeholder="Question yahan paste karo..."
            onChange={(e) => setQuestion(e.target.value)} />
          <div className="flex flex-wrap gap-3">
            <select className={box + " sm:w-auto"} value={length} onChange={(e) => setLength(e.target.value)}>
              <option value="short" className="text-black">Short (2 marks)</option>
              <option value="medium" className="text-black">Medium (5 marks)</option>
              <option value="long" className="text-black">Long (10 marks)</option>
            </select>
            <select className={box + " sm:w-auto"} value={language} onChange={(e) => setLanguage(e.target.value)}>
              {LANGUAGE_OPTIONS.map((l) => (
                <option key={l.value} value={l.value} className="text-black">{l.label}</option>
        ))}
            </select>
            <button type="button" onClick={makeDraft} disabled={!question.trim() || busy !== ""}
              className="rounded-lg bg-indigo-600 px-5 py-2 font-semibold disabled:opacity-50">
              {busy === "draft" ? "Likh raha hai..." : "Draft banao"}
            </button>
          </div>
        </section>

        <section className="mt-6 space-y-3 rounded-2xl border border-white/10 bg-white/5 p-5">
          <h2 className="font-bold">2. Draft (padho aur edit karo)</h2>
          <textarea rows={12} className={box} value={draft} placeholder="Draft yahan aayega. Dusre question ka draft niche jud jayega."
            onChange={(e) => setDraft(e.target.value)} />
        </section>

        <section className="mt-6 space-y-3 rounded-2xl border border-white/10 bg-white/5 p-5">
          <h2 className="font-bold">3. Apni handwriting mein PDF</h2>
          <label className="block text-sm text-slate-300">
            Aapka handwriting font (.ttf / .otf), khaali chhodo to default font
            <input type="file" accept=".ttf,.otf" className="mt-1 block text-sm"
              onChange={(e) => setFont(e.target.files?.[0] ?? null)} />
          </label>
          <label className="block text-xs text-slate-400">AI draft ki language
            <select className={box + " sm:w-64"} value={language} onChange={(e) => setLanguage(e.target.value)}>
              {LANGUAGE_OPTIONS.map((l) => (
                <option key={l.value} value={l.value} className="text-black">{l.label}</option>
           ))}
            </select>
          </label>
          <div className="flex flex-wrap gap-3">
            <input className={box + " sm:w-32"} type="number" value={fontSize} title="Font size"
              onChange={(e) => setFontSize(e.target.value)} />
            <select className={box + " sm:w-auto"} value={ink} onChange={(e) => setInk(e.target.value)}>
              <option value="blue" className="text-black">Blue ink</option>
              <option value="dark_blue" className="text-black">Dark blue ink</option>
              <option value="black" className="text-black">Black ink</option>
            </select>
            <input className={box + " sm:w-40"} type="number" value={maxPages} title="Max pages (0 = no limit)"
              placeholder="Max pages" onChange={(e) => setMaxPages(e.target.value)} />
          </div>
          <button type="button" onClick={makePdf} disabled={!draft.trim() || busy !== ""}
            className="w-full rounded-lg bg-emerald-600 py-3 font-semibold disabled:opacity-50">
            {busy === "pdf" ? "PDF ban rahi hai..." : "Handwriting PDF download karo"}
          </button>
        </section>

        {error && (
          <div className="mt-4 rounded-lg border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-300">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}