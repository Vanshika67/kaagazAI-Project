import React from "react";

/**
 * Small PDF / Word toggle, used next to every tool's action button.
 *
 * Usage:
 *   const [outputFormat, setOutputFormat] = useState("pdf");
 *   <OutputFormatSelector value={outputFormat} onChange={setOutputFormat} />
 */
export default function OutputFormatSelector({ value, onChange }) {
  return (
    <div className="flex items-center gap-3 bg-gray-100 rounded-full p-1 w-fit">
      <span className="text-sm text-gray-500 pl-2">Output as:</span>
      {["pdf", "word"].map((format) => (
        <button
          key={format}
          type="button"
          onClick={() => onChange(format)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
            value === format
              ? "bg-red-500 text-white shadow"
              : "text-gray-600 hover:bg-gray-200"
          }`}
        >
          {format === "pdf" ? "PDF" : "Word"}
        </button>
      ))}
    </div>
  );
}