import { COMING_SOON } from "./comingSoon";

export const NAV_SECTIONS = [
  { title: "Main", color: "violet", items: [{ label: "Dashboard", path: "/" }] },
  {
    title: "PDF Tools", color: "blue",
    items: [
      { label: "All PDF Tools", path: "/pdf-tools" },
      { label: "Workflow Builder", path: "/workflow" },
      { label: "Page Manager", path: "/page-manager" },
    ],
  },
  {
    title: "Create", color: "emerald",
    items: [
      { label: "Resume - Simple", path: "/tool/resume-builder?template_style=simple" },
      { label: "Resume - Modern", path: "/tool/resume-builder?template_style=modern" },
      { label: "Handwriting Notes / Assignment Helper", path: "/handwriting" },
      { label: "Report Generator", path: "/tool/report-generator" },
    ],
  },
  {
    title: "AI Tools", color: "fuchsia",
    items: [
      { label: "AI Summarization", path: "/tool/ai-summarize" },
      { label: "AI Translation", path: "/tool/ai-translate" },
      { label: "AI Answer Draft", path: "/tool/ai-draft" },
      { label: "Chat with PDF", path: "/tool/chat-pdf" },
      { label: "Extract Data", path: "/tool/ai-extract" },
      { label: "Hindi / Scanned OCR", path: "/tool/hindi-ocr" },
      { label: "Concept Visualizer", path: "/tool/concept-visualizer" },
      { label: "Voice to Notes", path: "/tool/voice-to-notes" },
    ],
  },
  {
    title: "Coming Soon", color: "amber",
    items: COMING_SOON.map((c) => ({ label: `${c.icon} ${c.label}`, path: "#", soon: true })),
  },
];