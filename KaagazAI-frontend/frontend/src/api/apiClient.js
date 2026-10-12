/**
 * apiClient.js - the ONLY place that talks to the backend.
 * Every page uses these helpers, so changing the backend URL or
 * error handling later needs a change in just one file.
 */

const API_URL = import.meta.env?.VITE_API_URL ?? "http://127.0.0.1:8000";

/** Builds the multipart form a backend endpoint expects, from a tool's field config + user values. */
export function buildFormData(tool, values) {
  const fd = new FormData();

  for (const field of tool.fields) {
    const value = values[field.name];

    if (field.type === "file") {
      const files = value || [];
      if (files.length === 0) {
        if (!field.optional) throw new Error(`Please choose: ${field.label}`);
        continue;
      }
      files.forEach((file) => fd.append(field.name, file));
    } else {
      const text = (value ?? "").toString().trim();
      if (text === "") {
        if (!field.optional) throw new Error(`Please fill in: ${field.label}`);
        continue; // optional + empty -> let the backend use its default
      }
      fd.append(field.name, text);
    }
  }

  return fd;
}

function filenameFromHeader(header) {
  if (!header) return null;
  const match = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(header);
  return match ? decodeURIComponent(match[1]) : null;
}

/**
 * POSTs a form to the backend. Returns either
 *   { kind: "file", blob, filename, meta }   (PDF, ZIP, HTML, MD, PNG...)
 *   { kind: "json", data }                   (compare, form-fields, page-info...)
 * and throws an Error with a readable message if anything goes wrong.
 */
export async function postForm(endpoint, formData, fallbackFilename = "result") {
  let response;
  try {
    response = await fetch(`${API_URL}${endpoint}`, { method: "POST", body: formData });
  } catch {
    throw new Error(
      "Could not reach the backend. Make sure the server is running (uvicorn app.main:app --reload)."
    );
  }

  if (!response.ok) {
    let detail = `Server error (${response.status})`;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* response was not JSON, keep the generic message */
    }
    throw new Error(detail);
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return { kind: "json", data: await response.json() };
  }

  const blob = await response.blob();
  const removed = response.headers.get("x-removed-pages");
  return {
    kind: "file",
    blob,
    filename: filenameFromHeader(response.headers.get("content-disposition")) || fallbackFilename,
    meta: removed ? { removedPages: removed } : undefined,
  };
}

/** Runs a tool from config/tools.js with the values the user entered. */
export function runTool(tool, values) {
  return postForm(tool.endpoint, buildFormData(tool, values), tool.output);
}

/** Asks the backend how many pages a PDF has (used by the Page Manager). */
export async function getPageCount(file) {
  const fd = new FormData();
  fd.append("file", file);
  const result = await postForm("/api/pdf/page-info", fd);
  return result.data.total_pages;
}

/** Saves a blob to the user's computer. */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
