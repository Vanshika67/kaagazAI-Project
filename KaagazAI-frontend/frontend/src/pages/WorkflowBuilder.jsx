import { useState } from "react";
import FileDropzone from "../components/FileDropzone";
import ResultPanel from "../components/ResultPanel";
import PageHeader from "../components/PageHeader";
import { THEMES } from "../config/theme";
import { postForm } from "../api/apiClient";
import { WORKFLOW_TOOLS, defaultParams, serializeSteps } from "../config/workflowTools";

const inputClass =
  "w-full rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-sm outline-none focus:border-indigo-500";

let nextId = 1;

export default function WorkflowBuilder() {
  const [files, setFiles] = useState([]);
  const [steps, setSteps] = useState([]);
  const [toAdd, setToAdd] = useState("rotate");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const addStep = () =>
    setSteps((s) => [...s, { uid: nextId++, tool: toAdd, params: defaultParams(toAdd) }]);

  const removeStep = (uid) => setSteps((s) => s.filter((x) => x.uid !== uid));

  const moveStep = (index, delta) =>
    setSteps((s) => {
      const target = index + delta;
      if (target < 0 || target >= s.length) return s;
      const copy = [...s];
      [copy[index], copy[target]] = [copy[target], copy[index]];
      return copy;
    });

  const setParam = (uid, name, value) =>
    setSteps((s) => s.map((x) => (x.uid === uid ? { ...x, params: { ...x.params, [name]: value } } : x)));

  const run = async () => {
    setError("");
    setResult(null);
    try {
      if (files.length === 0) throw new Error("Please choose a PDF first.");
      if (steps.length === 0) throw new Error("Add at least one step.");
      const payload = serializeSteps(steps);

      setLoading(true);
      const fd = new FormData();
      fd.append("file", files[0]);
      fd.append("steps", JSON.stringify(payload));
      setResult(await postForm("/api/workflow/run", fd, "workflow_result.pdf"));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <PageHeader icon="⛓️" title="Workflow Builder" theme={THEMES.fuchsia}
        description="Upload one PDF, add tools, set their order. Each step's output becomes the next step's input." />

      <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 font-semibold">1. Choose your PDF</h2>
        <FileDropzone files={files} onChange={setFiles} accept=".pdf" />
      </section>

      <section className="mt-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 font-semibold">2. Build your steps</h2>

        <div className="flex gap-2">
          <select className={inputClass} value={toAdd} onChange={(e) => setToAdd(e.target.value)}>
            {Object.entries(WORKFLOW_TOOLS).map(([key, def]) => <option key={key} value={key}>{def.label}</option>)}
          </select>
          <button type="button" onClick={addStep} className="shrink-0 rounded-lg bg-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-indigo-700">
            + Add step
          </button>
        </div>

        {steps.length === 0 && <p className="mt-4 text-sm text-slate-500">No steps yet. Add your first one above.</p>}

        <ol className="mt-4 space-y-3">
          {steps.map((step, i) => {
            const def = WORKFLOW_TOOLS[step.tool];
            return (
              <li key={step.uid} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <div className="flex items-center gap-2">
                  <span className="grid h-7 w-7 place-items-center rounded-full bg-indigo-600 text-sm font-bold text-white">{i + 1}</span>
                  <span className="flex-1 font-medium">{def.label}</span>
                  <button type="button" onClick={() => moveStep(i, -1)} disabled={i === 0} className="px-1 text-slate-500 hover:text-indigo-600 disabled:opacity-30">↑</button>
                  <button type="button" onClick={() => moveStep(i, 1)} disabled={i === steps.length - 1} className="px-1 text-slate-500 hover:text-indigo-600 disabled:opacity-30">↓</button>
                  <button type="button" onClick={() => removeStep(step.uid)} className="px-1 text-slate-400 hover:text-red-600">✕</button>
                </div>

                {def.params.length > 0 && (
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    {def.params.map((p) => (
                      <div key={p.name}>
                        <label className="mb-1 block text-xs font-medium text-slate-600">
                          {p.label}{p.optional && " (optional)"}
                        </label>
                        {p.type === "select" ? (
                          <select className={inputClass} value={step.params[p.name]} onChange={(e) => setParam(step.uid, p.name, e.target.value)}>
                            {p.options.map((o) => <option key={o} value={o}>{o}</option>)}
                          </select>
                        ) : (
                          <input className={inputClass} type={p.type === "number" ? "number" : "text"} placeholder={p.placeholder}
                            value={step.params[p.name]} onChange={(e) => setParam(step.uid, p.name, e.target.value)} />
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </li>
            );
          })}
        </ol>
      </section>

      <button type="button" onClick={run} disabled={loading}
        className={`mt-5 w-full rounded-lg bg-linear-to-r ${THEMES.fuchsia.gradient} py-3 font-semibold text-white shadow-md hover:brightness-110 disabled:cursor-wait disabled:opacity-60`}>
        {loading ? "Running workflow..." : "Run workflow"}
      </button>

      {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">⚠️ {error}</div>}
      <ResultPanel result={result} />
    </div>
  );
}
