import { useState } from "react";
import { LANGUAGE_OPTIONS } from "../config/languages";

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
const box =
  "w-full rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-white placeholder-slate-500 outline-none focus:border-amber-300";
const card = "mt-6 space-y-4 rounded-2xl border border-white/10 bg-white/5 p-5";

async function readError(res) {
  try { return (await res.json()).detail || "Kuch galat ho gaya."; }
  catch { return "Kuch galat ho gaya."; }
}

export default function HandwritingStudio() {
  const [items, setItems] = useState([{ q: "", a: "" }]);
  const [font, setFont] = useState(null);
  const [fontSize, setFontSize] = useState("18");
  const [spacing, setSpacing] = useState("1.6");
  const [ink, setInk] = useState("blue");
  const [ruled, setRuled] = useState("yes");
  const [maxPages, setMaxPages] = useState("0");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [language, setLanguage] = useState("English");

  const update = (i, key, val) =>
    setItems((arr) => arr.map((it, idx) => (idx === i ? { ...it, [key]: val } : it)));

  const aiDraft = async (i) => {
    setBusy("draft" + i); setError("");
    try {
      const fd = new FormData();
      fd.append("question", items[i].q);
      const res = await fetch(`${API}/api/tools/ai-draft`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(await readError(res));
      update(i, "a", (await res.json()).draft);
    } catch (e) { setError(e.message); }
    finally { setBusy(""); }
  };

  const fullText = items
    .filter((it) => it.q.trim() || it.a.trim())
    .map((it, i) => `Q${i + 1}. ${it.q.trim()}\nAns. ${it.a.trim()}`)
    .join("\n\n");

  const makePdf = async () => {
    setBusy("pdf"); setError("");
    try {
      const fd = new FormData();
      fd.append("text", fullText);
      fd.append("font_size", fontSize);
      fd.append("line_spacing", spacing);
      fd.append("ink", ink);
      fd.append("ruled", ruled);
      fd.append("max_pages", maxPages);
      if (font) fd.append("font", font);
      const res = await fetch(`${API}/api/tools/handwriting`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(await readError(res));
      const a = document.createElement("a");
      a.href = URL.createObjectURL(await res.blob());
      a.download = "my_handwriting_assignment.pdf";
      a.click();
      URL.revokeObjectURL(a.href);
    } catch (e) { setError(e.message); }
    finally { setBusy(""); }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="text-3xl font-black">
          <span className="bg-linear-to-r from-amber-300 to-pink-400 bg-clip-text text-transparent">
            Handwriting Notes / Assignment Helper
          </span>
        </h1>
        <p className="mt-2 text-slate-400">
          Question aur answer daalo, apna handwriting font lagao, aur apni hi writing mein ruled-page PDF pao.
        </p>

        <section className={card}>
          <h2 className="font-bold">1. Question aur Answer</h2>
          {items.map((it, i) => (
            <div key={i} className="space-y-2 rounded-xl border border-white/10 p-3">
              <div className="flex items-center justify-between text-sm text-slate-400">
                <span>Question {i + 1}</span>
                {items.length > 1 && (
                  <button type="button" className="text-red-300"
                    onClick={() => setItems((a) => a.filter((_, idx) => idx !== i))}>Hatao</button>
                )}
              </div>
              <textarea rows={2} className={box} placeholder="Question paste karo..."
                value={it.q} onChange={(e) => update(i, "q", e.target.value)} />
              <textarea rows={5} className={box} placeholder="Answer paste karo, ya neeche AI draft se banwao..."
                value={it.a} onChange={(e) => update(i, "a", e.target.value)} />
              <button type="button" disabled={!it.q.trim() || busy !== ""} onClick={() => aiDraft(i)}
                className="rounded-lg bg-indigo-600 px-4 py-1.5 text-sm font-semibold disabled:opacity-50">
                {busy === "draft" + i ? "Likh raha hai..." : "✨ AI se draft banao"}
              </button>
            </div>
          ))}
          <button type="button" onClick={() => setItems((a) => [...a, { q: "", a: "" }])}
            className="rounded-lg border border-dashed border-white/30 px-4 py-2 text-sm">+ Aur question jodo</button>
          <p className="text-xs text-slate-500">AI draft ko padh kar apne words mein edit kar lena, taaki answer sahi ho aur aapko samajh bhi aaye.</p>
        </section>

        <section className={card}>
          <h2 className="font-bold">2. Apni handwriting</h2>
          <label className="block text-sm text-slate-300">
            Apna handwriting font (.ttf / .otf). Khaali chhodo to default font use hoga.
            <input type="file" accept=".ttf,.otf" className="mt-1 block text-sm"
              onChange={(e) => setFont(e.target.files?.[0] ?? null)} />
          </label>
          <p className="text-xs text-slate-500">
            Font kaise banayein: Calligraphr.com par template print karo, us par apni handwriting likho, scan karke upload karo, aur .ttf download karo. Hindi ke liye Devanagari wala font chahiye.
          </p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <label className="text-xs text-slate-400">Font size
              <input className={box} type="number" value={fontSize} onChange={(e) => setFontSize(e.target.value)} /></label>
            <label className="text-xs text-slate-400">Line spacing
              <input className={box} type="number" step="0.1" value={spacing} onChange={(e) => setSpacing(e.target.value)} /></label>
            <label className="text-xs text-slate-400">Max pages (0 = no limit)
              <input className={box} type="number" value={maxPages} onChange={(e) => setMaxPages(e.target.value)} /></label>
            <label className="text-xs text-slate-400">Ink
              <select className={box} value={ink} onChange={(e) => setInk(e.target.value)}>
                <option value="blue" className="text-black">Blue</option>
                <option value="dark_blue" className="text-black">Dark blue</option>
                <option value="black" className="text-black">Black</option>
              </select></label>
          </div>
          <label className="block text-xs text-slate-400">Ruled lines
            <select className={box + " sm:w-40"} value={ruled} onChange={(e) => setRuled(e.target.value)}>
              <option value="yes" className="text-black">Yes</option>
              <option value="no" className="text-black">No</option>
            </select></label>
        </section>

        <button type="button" onClick={makePdf} disabled={!fullText.trim() || busy !== ""}
          className="mt-6 w-full rounded-xl bg-linear-to-r from-emerald-500 to-teal-500 py-3.5 text-lg font-bold shadow-lg disabled:opacity-50">
          {busy === "pdf" ? "PDF ban rahi hai..." : "📥 Handwriting PDF download karo"}
        </button>

        {error && (
          <div className="mt-4 rounded-lg border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-300">{error}</div>
        )}
      </div>
    </div>
  );
}