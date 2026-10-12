import { useRef, useState } from "react";

const formatSize = (bytes) =>
  bytes > 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`;

/**
 * Drag-and-drop (or click) file picker.
 * `files` is an array of File objects owned by the parent; we call
 * onChange(newArray) whenever the user adds, removes or reorders files.
 * For multi-file tools like Merge, the order of the list is the order sent.
 */
export default function FileDropzone({ files, onChange, multiple = false, accept }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const addFiles = (fileList) => {
    const incoming = Array.from(fileList);
    onChange(multiple ? [...files, ...incoming] : incoming.slice(0, 1));
  };

  const remove = (index) => onChange(files.filter((_, i) => i !== index));

  const move = (index, delta) => {
    const target = index + delta;
    if (target < 0 || target >= files.length) return;
    const copy = [...files];
    [copy[index], copy[target]] = [copy[target], copy[index]];
    onChange(copy);
  };

  return (
    <div>
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); addFiles(e.dataTransfer.files); }}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-6 text-center transition ${
          dragging ? "border-indigo-500 bg-indigo-50" : "border-slate-300 bg-white hover:border-indigo-400"
        }`}
      >
        <p className="font-medium text-slate-700">
          Drag & drop {multiple ? "files" : "a file"} here, or <span className="text-indigo-600">browse</span>
        </p>
        <input
          ref={inputRef}
          type="file"
          hidden
          multiple={multiple}
          accept={accept}
          onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }}
        />
      </div>

      {files.length > 0 && (
        <ul className="mt-3 space-y-2">
          {files.map((file, i) => (
            <li key={`${file.name}-${i}`} className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
              <span className="w-5 text-slate-400">{i + 1}</span>
              <span className="min-w-0 flex-1 truncate font-medium">{file.name}</span>
              <span className="text-slate-400">{formatSize(file.size)}</span>
              {multiple && files.length > 1 && (
                <>
                  <button type="button" onClick={() => move(i, -1)} disabled={i === 0} className="px-1 text-slate-500 hover:text-indigo-600 disabled:opacity-30" title="Move up">↑</button>
                  <button type="button" onClick={() => move(i, 1)} disabled={i === files.length - 1} className="px-1 text-slate-500 hover:text-indigo-600 disabled:opacity-30" title="Move down">↓</button>
                </>
              )}
              <button type="button" onClick={() => remove(i)} className="px-1 text-slate-400 hover:text-red-600" title="Remove">✕</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
