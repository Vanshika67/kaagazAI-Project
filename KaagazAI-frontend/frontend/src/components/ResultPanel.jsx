import { useEffect, useMemo } from "react";
import { downloadBlob } from "../api/apiClient";

/** Shows what came back from the backend: a download (+ PDF preview) or JSON. */
export default function ResultPanel({ result }) {
  const previewUrl = useMemo(
    () => (result?.kind === "file" && result.blob.type === "application/pdf" ? URL.createObjectURL(result.blob) : null),
    [result]
  );
  useEffect(() => () => previewUrl && URL.revokeObjectURL(previewUrl), [previewUrl]);

  if (!result) return null;

  if (result.kind === "json") {
    const text = result.data.diff_report ?? JSON.stringify(result.data, null, 2);
    return (
      <div className="mt-6 rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="mb-2 font-semibold">Result</h3>
        <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-900 p-3 text-sm text-slate-100">{text}</pre>
      </div>
    );
  }

  return (
    <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-semibold text-emerald-800">Done! Your file is ready.</h3>
          <p className="text-sm text-emerald-700">{result.filename}</p>
          {result.meta?.removedPages && (
            <p className="text-sm text-emerald-700">Removed blank pages: {result.meta.removedPages}</p>
          )}
        </div>
        <button
          type="button"
          onClick={() => downloadBlob(result.blob, result.filename)}
          className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700"
        >
          Download
        </button>
      </div>
      {previewUrl && <iframe src={previewUrl} title="Preview" className="mt-4 h-[480px] w-full rounded-lg border border-emerald-200 bg-white" />}
    </div>
  );
}
