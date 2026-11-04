import { useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import FileDropzone from "../components/FileDropzone";
import ResultPanel from "../components/ResultPanel";
import { runTool } from "../api/apiClient";
import PageHeader from "../components/PageHeader";
import { getTool } from "../config/tools";
import { themeForCategory } from "../config/theme";

const inputClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200";

// CHANGE 1: ab ye URL params (?template_style=modern) bhi leta hai
function initialValues(tool, params) {
  const values = {};
  tool.fields.forEach((f) => {
    values[f.name] = f.type === "file" ? [] : params.get(f.name) ?? f.default ?? "";
  });
  return values;
}

/** One generic page that builds its form from the tool's config. */
function ToolForm({ tool }) {
  // CHANGE 2: searchParams yahan, ToolForm ke andar sabse upar
  const [searchParams] = useSearchParams();
  const [values, setValues] = useState(() => initialValues(tool, searchParams));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const theme = themeForCategory(tool.category);

  const setValue = (name, value) => setValues((v) => ({ ...v, [name]: value }));

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await runTool(tool, values));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <PageHeader icon={tool.icon} title={tool.name} description={tool.description} theme={theme} />

      <form onSubmit={submit} className="mt-6 space-y-5 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        {tool.fields.map((f) => (
          <div key={f.name}>
            <label className="mb-1 block text-sm font-medium">
              {f.label} {f.optional && <span className="font-normal text-slate-400">(optional)</span>}
            </label>

            {f.type === "file" && (
              <FileDropzone files={values[f.name]} multiple={f.multiple} accept={f.accept} onChange={(files) => setValue(f.name, files)} />
            )}
            {f.type === "select" && (
              <select className={inputClass} value={values[f.name]} onChange={(e) => setValue(f.name, e.target.value)}>
                {f.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            )}
            {f.type === "textarea" && (
              <textarea rows={6} className={`${inputClass} font-mono text-sm`} placeholder={f.placeholder}
                value={values[f.name]} onChange={(e) => setValue(f.name, e.target.value)} />
            )}
            {["text", "number", "password"].includes(f.type) && (
              <input type={f.type} className={inputClass} placeholder={f.placeholder}
                value={values[f.name]} onChange={(e) => setValue(f.name, e.target.value)} />
            )}

            {f.help && <p className="mt-1 text-xs text-slate-500">{f.help}</p>}
          </div>
        ))}

        <button type="submit" disabled={loading}
          className={`w-full rounded-lg bg-linear-to-r ${theme.gradient} py-3 font-semibold text-white shadow-md transition hover:brightness-110 disabled:cursor-wait disabled:opacity-60`}>
          {loading ? "Processing..." : tool.name}
        </button>
      </form>

      {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">⚠️ {error}</div>}
      <ResultPanel result={result} />
    </div>
  );
}

export default function ToolPage() {
  const { id } = useParams();
  // CHANGE 3: ToolPage ke andar, `if (!tool)` se PEHLE
  const [sp] = useSearchParams();
  const tool = getTool(id);

  if (!tool) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center">
        <h1 className="text-2xl font-bold">Tool not found</h1>
        <Link to="/" className="mt-3 inline-block text-indigo-600 hover:underline">Back to all tools</Link>
      </div>
    );
  }
  // key mein sp daalne se Simple <-> Modern badalne par form reset hota hai
  return <ToolForm key={tool.id + sp.toString()} tool={tool} />;
}