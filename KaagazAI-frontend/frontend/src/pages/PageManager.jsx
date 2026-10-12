import { useState } from "react";
import FileDropzone from "../components/FileDropzone";
import ResultPanel from "../components/ResultPanel";
import PageHeader from "../components/PageHeader";
import { THEMES } from "../config/theme";
import { getPageCount, postForm } from "../api/apiClient";

const inputClass =
  "rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-sm outline-none focus:border-indigo-500";

let nextId = 1;

export default function PageManager() {
  const [mainFiles, setMainFiles] = useState([]);
  const [extraFiles, setExtraFiles] = useState([]);
  const [counts, setCounts] = useState({}); // { main: 5, extra_0: 2, ... }
  const [plan, setPlan] = useState([]); // [{ uid, source, page }]
  const [src, setSrc] = useState("main");
  const [pageInput, setPageInput] = useState("1");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const sources = [
    ...(mainFiles[0] ? [{ key: "main", name: mainFiles[0].name }] : []),
    ...extraFiles.map((f, i) => ({ key: `extra_${i}`, name: f.name })),
  ];
  const labelOf = (key) => sources.find((s) => s.key === key)?.name ?? key;

  const onMainChange = async (files) => {
    setMainFiles(files);
    setPlan([]);
    setResult(null);
    setError("");
    if (!files[0]) { setCounts((c) => ({ ...c, main: undefined })); return; }
    try {
      const n = await getPageCount(files[0]);
      setCounts((c) => ({ ...c, main: n }));
    } catch (err) { setError(err.message); }
  };

  const onExtraChange = async (files) => {
    setExtraFiles(files);
    // drop plan items that point at files which no longer exist
    setPlan((p) => p.filter((item) => item.source === "main" || Number(item.source.split("_")[1]) < files.length));
    try {
      const list = await Promise.all(files.map((f) => getPageCount(f)));
      setCounts((c) => {
        const next = { main: c.main };
        list.forEach((n, i) => { next[`extra_${i}`] = n; });
        return next;
      });
    } catch (err) { setError(err.message); }
  };

  const addPage = () => {
    setError("");
    const page = Number(pageInput);
    const max = counts[src];
    if (!Number.isInteger(page) || page < 1 || (max && page > max)) {
      setError(`Page must be between 1 and ${max ?? "?"} for ${labelOf(src)}.`);
      return;
    }
    setPlan((p) => [...p, { uid: nextId++, source: src, page }]);
  };

  const addAllMain = () =>
    setPlan((p) => [...p, ...Array.from({ length: counts.main }, (_, i) => ({ uid: nextId++, source: "main", page: i + 1 }))]);

  const move = (index, delta) =>
    setPlan((p) => {
      const target = index + delta;
      if (target < 0 || target >= p.length) return p;
      const copy = [...p];
      [copy[index], copy[target]] = [copy[target], copy[index]];
      return copy;
    });

  const build = async () => {
    setError("");
    setResult(null);
    if (!mainFiles[0]) { setError("Please choose the main PDF first."); return; }
    if (plan.length === 0) { setError("Your page list is empty. Add at least one page."); return; }

    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("main_file", mainFiles[0]);
      extraFiles.forEach((f) => fd.append("extra_files", f));
      fd.append("plan", JSON.stringify(plan.map(({ source, page }) => ({ source, page }))));
      setResult(await postForm("/api/pdf/manage-pages", fd, "organized.pdf"));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <PageHeader icon="🧩" title="Page Manager" theme={THEMES.cyan}
        description="Describe the final page order you want. Leave a page out to delete it, repeat a page to duplicate it, or pull pages from other PDFs to insert them anywhere." />

      <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 font-semibold">1. Main PDF</h2>
        <FileDropzone files={mainFiles} onChange={onMainChange} accept=".pdf" />
        {counts.main && <p className="mt-2 text-sm text-slate-500">{counts.main} pages</p>}
      </section>

      <section className="mt-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 font-semibold">2. Extra PDFs to take pages from <span className="font-normal text-slate-400">(optional)</span></h2>
        <FileDropzone files={extraFiles} onChange={onExtraChange} multiple accept=".pdf" />
        {extraFiles.map((f, i) => counts[`extra_${i}`] && (
          <p key={i} className="mt-1 text-sm text-slate-500">extra_{i}: {f.name} ({counts[`extra_${i}`]} pages)</p>
        ))}
      </section>

      <section className="mt-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 font-semibold">3. Build the final page order</h2>

        <div className="flex flex-wrap items-center gap-2">
          <select className={inputClass} value={src} onChange={(e) => setSrc(e.target.value)}>
            {sources.length === 0 && <option value="main">Choose a PDF first</option>}
            {sources.map((s) => <option key={s.key} value={s.key}>{s.name}</option>)}
          </select>
          <input className={`${inputClass} w-24`} type="number" min="1" value={pageInput} onChange={(e) => setPageInput(e.target.value)} />
          <button type="button" onClick={addPage} disabled={sources.length === 0}
            className="rounded-lg bg-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-40">
            + Add page
          </button>
          {counts.main && (
            <button type="button" onClick={addAllMain} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:border-indigo-400">
              Add all pages of main PDF
            </button>
          )}
          {plan.length > 0 && (
            <button type="button" onClick={() => setPlan([])} className="px-2 text-sm text-slate-500 hover:text-red-600">Clear</button>
          )}
        </div>

        {plan.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">Nothing yet. Tip: click "Add all pages of main PDF", then remove or move pages.</p>
        ) : (
          <ol className="mt-4 space-y-2">
            {plan.map((item, i) => (
              <li key={item.uid} className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm">
                <span className="grid h-6 w-6 place-items-center rounded-full bg-indigo-600 text-xs font-bold text-white">{i + 1}</span>
                <span className="flex-1 truncate">{labelOf(item.source)} · page {item.page}</span>
                <button type="button" onClick={() => move(i, -1)} disabled={i === 0} className="px-1 text-slate-500 hover:text-indigo-600 disabled:opacity-30">↑</button>
                <button type="button" onClick={() => move(i, 1)} disabled={i === plan.length - 1} className="px-1 text-slate-500 hover:text-indigo-600 disabled:opacity-30">↓</button>
                <button type="button" onClick={() => setPlan((p) => p.filter((x) => x.uid !== item.uid))} className="px-1 text-slate-400 hover:text-red-600">✕</button>
              </li>
            ))}
          </ol>
        )}
      </section>

      <button type="button" onClick={build} disabled={loading}
        className={`mt-5 w-full rounded-lg bg-linear-to-r ${THEMES.cyan.gradient} py-3 font-semibold text-white shadow-md hover:brightness-110 disabled:cursor-wait disabled:opacity-60`}>
        {loading ? "Building..." : "Build new PDF"}
      </button>

      {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">⚠️ {error}</div>}
      <ResultPanel result={result} />
    </div>
  );
}
