import { useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import FileDropzone from "../components/FileDropzone";
import ResultPanel from "../components/ResultPanel";
import { runTool } from "../api/apiClient";
import { getTool } from "../config/tools";
import { themeForCategory, bgForCategory } from "../config/theme";

const inputClass =
  "w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2 text-white placeholder-slate-400 outline-none backdrop-blur focus:border-white/40 focus:ring-2 focus:ring-white/20";

// Har category ke liye alag hilte hue decorative icons
const CATEGORY_ICONS = {
  organize: ["🗂️", "📑", "🔀"],
  convert: ["🔄", "🖼️", "📘"],
  optimize: ["⚡", "📦", "🗜️"],
  security: ["🔒", "🔑", "🛡️"],
  edit: ["✏️", "🖊️", "🧾"],
  ai: ["🤖", "🧠", "💬"],
};

function initialValues(tool, params) {
  const values = {};
  tool.fields.forEach((f) => {
    values[f.name] = f.type === "file" ? [] : params.get(f.name) ?? f.default ?? "";
  });
  return values;
}

/** One generic page that builds its form from the tool's config. */
function ToolForm({ tool }) {
  const [searchParams] = useSearchParams();
  const [values, setValues] = useState(() => initialValues(tool, searchParams));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const theme = themeForCategory(tool.category);
  const pageBg = bgForCategory(tool.category);
  const icons = CATEGORY_ICONS[tool.category] ?? ["✨", "📄", "⭐"];

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
    <div className={`relative min-h-screen overflow-hidden ${pageBg} text-white`}>
      {/* colorful blurred background blobs, category ke theme se */}
      <div className={`pointer-events-none absolute -left-40 -top-20 h-96 w-96 rounded-full bg-linear-to-br ${theme.gradient} opacity-25 blur-3xl`} />
      <div className={`pointer-events-none absolute -right-32 top-60 h-80 w-80 rounded-full bg-linear-to-br ${theme.gradient} opacity-15 blur-3xl`} />
      <div className="pointer-events-none absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-fuchsia-600/10 blur-3xl" />

      {/* hilte hue decorative icons */}
      <span className="float-a pointer-events-none absolute left-4 top-10 text-4xl opacity-30 sm:left-10">{icons[0]}</span>
      <span className="float-b pointer-events-none absolute right-4 top-16 text-4xl opacity-30 sm:right-12">{icons[1]}</span>
      <span className="float-c pointer-events-none absolute bottom-10 left-10 hidden text-4xl opacity-20 sm:block">{icons[2]}</span>

      <div className="relative mx-auto max-w-2xl px-4 py-10">
        <Link to="/" className="mb-4 inline-flex items-center gap-1 text-sm text-slate-200 hover:text-white">
          ← Back to all tools
        </Link>

        <div className="mb-6 flex items-center gap-4 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur">
          <span className={`grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-linear-to-br ${theme.gradient} text-3xl shadow-lg`}>
            {tool.icon}
          </span>
          <div>
            <h1 className="text-2xl font-extrabold">{tool.name}</h1>
            <p className="mt-1 text-sm text-slate-200">{tool.description}</p>
          </div>
        </div>

        <form onSubmit={submit} className="space-y-5 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur">
          {tool.fields.map((f) => (
            <div key={f.name}>
              <label className="mb-1 block text-sm font-medium text-slate-100">
                {f.label} {f.optional && <span className="font-normal text-slate-300">(optional)</span>}
              </label>

              {f.type === "file" && (
                <FileDropzone files={values[f.name]} multiple={f.multiple} accept={f.accept} onChange={(files) => setValue(f.name, files)} />
              )}
              {f.type === "select" && (
                <select className={inputClass} value={values[f.name]} onChange={(e) => setValue(f.name, e.target.value)}>
                  {f.options.map((o) => (
                    <option key={o.value} value={o.value} className="text-black">{o.label}</option>
                  ))}
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

              {f.help && <p className="mt-1 text-xs text-slate-300">{f.help}</p>}
            </div>
          ))}

          <button type="submit" disabled={loading}
            className={`w-full rounded-lg ${theme.solid} py-3 font-semibold text-white shadow-lg transition disabled:cursor-wait disabled:opacity-60`}>
            {loading ? "Processing..." : tool.name}
          </button>
        </form>

        {error && (
          <div className="mt-4 rounded-lg border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-200">
            ⚠️ {error}
          </div>
        )}
        <ResultPanel result={result} />
      </div>
    </div>
  );
}

export default function ToolPage() {
  const { id } = useParams();
  const [sp] = useSearchParams();
  const tool = getTool(id);

  if (!tool) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-linear-to-br from-sky-900 via-cyan-800 to-teal-900 text-center text-white">
        <div>
          <h1 className="text-2xl font-bold">Tool not found</h1>
          <Link to="/" className="mt-3 inline-block text-cyan-200 hover:underline">Back to all tools</Link>
        </div>
      </div>
    );
  }
  // key mein sp daalne se Simple <-> Modern badalne par form reset hota hai
  return <ToolForm key={tool.id + sp.toString()} tool={tool} />;
}