import { CATEGORIES, TOOLS } from "./tools";

export const NON_PDF_TOOL_IDS = [
  "resume-builder", "handwriting", "ai-draft",
  "ai-summarize", "ai-translate", "ai-extract", "hindi-ocr", "chat-pdf",
];
export const PDF_TOOLS = TOOLS.filter((t) => !NON_PDF_TOOL_IDS.includes(t.id));
export const PDF_CATEGORIES = CATEGORIES.filter((c) => c.id !== "ai");