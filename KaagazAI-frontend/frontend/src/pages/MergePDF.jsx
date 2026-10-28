import React, { useState } from "react";
import FileUploader from "../components/FileUploader";
import OutputFormatSelector from "../components/OutputFormatSelector";

export default function MergePDF() {
  const [files, setFiles] = useState([]);
  const [outputFormat, setOutputFormat] = useState("pdf");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleMerge = async () => {
    if (files.length < 2) {
      setError("Please select at least 2 files to merge.");
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      files.forEach((f) => formData.append("files", f));
      formData.append("output_format", outputFormat);

      const response = await fetch("/api/tools/merge", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Merge failed. Please try again.");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = outputFormat === "word" ? "merged.docx" : "merged.pdf";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-16 px-4">
      <h1 className="text-3xl font-bold text-center mb-2">Merge PDF files</h1>
      <p className="text-center text-gray-500 mb-8">
        Combine PDF and Word files, in any order, into one file.
      </p>

      <FileUploader files={files} setFiles={setFiles} multiple />

      {files.length > 0 && (
        <div className="flex items-center justify-between mt-6">
          <OutputFormatSelector value={outputFormat} onChange={setOutputFormat} />
          <button
            onClick={handleMerge}
            disabled={loading}
            className="bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white font-semibold px-6 py-2.5 rounded-full transition"
          >
            {loading ? "Merging..." : "Merge"}
          </button>
        </div>
      )}

      {error && <p className="text-red-500 text-sm mt-3">{error}</p>}
    </div>
  );
}