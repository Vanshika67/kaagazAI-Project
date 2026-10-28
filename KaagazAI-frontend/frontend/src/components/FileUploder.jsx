import React, { useRef } from "react";

/**
 * Accepts PDF and Word files, shows a reorderable/removable list.
 *
 * Usage:
 *   const [files, setFiles] = useState([]);
 *   <FileUploader files={files} setFiles={setFiles} multiple />
 */
export default function FileUploader({ files, setFiles, multiple = true }) {
  const inputRef = useRef(null);

  const handleSelect = (e) => {
    const picked = Array.from(e.target.files);
    setFiles(multiple ? [...files, ...picked] : picked);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files);
    setFiles(multiple ? [...files, ...dropped] : dropped);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const moveFile = (index, direction) => {
    const newFiles = [...files];
    const target = index + direction;
    if (target < 0 || target >= newFiles.length) return;
    [newFiles[index], newFiles[target]] = [newFiles[target], newFiles[index]];
    setFiles(newFiles);
  };

  const badge = (name) => (name.toLowerCase().endsWith(".pdf") ? "PDF" : "DOCX");

  return (
    <div>
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
        className="border-2 border-dashed border-red-300 rounded-xl p-10 text-center cursor-pointer hover:bg-red-50 transition"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.doc,.docx"
          multiple={multiple}
          onChange={handleSelect}
          className="hidden"
        />
        <p className="text-lg font-semibold text-red-500">
          Select PDF or Word files
        </p>
        <p className="text-sm text-gray-400 mt-1">or drop files here</p>
      </div>

      {files.length > 0 && (
        <ul className="mt-4 space-y-2">
          {files.map((file, index) => (
            <li
              key={`${file.name}-${index}`}
              className="flex items-center justify-between bg-gray-50 border rounded-lg px-3 py-2"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold bg-gray-200 rounded px-2 py-0.5">
                  {badge(file.name)}
                </span>
                <span className="text-sm text-gray-700">{file.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => moveFile(index, -1)} className="text-gray-400 hover:text-gray-700">↑</button>
                <button onClick={() => moveFile(index, 1)} className="text-gray-400 hover:text-gray-700">↓</button>
                <button onClick={() => removeFile(index)} className="text-red-400 hover:text-red-600">✕</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}