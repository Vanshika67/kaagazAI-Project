export const NAV_SECTIONS = [
  { title: "Main", items: [{ label: "Dashboard", path: "/" }] },
  {
    title: "PDF Tools",
    items: [
      { label: "All PDF Tools", path: "/pdf-tools" },
      { label: "Workflow Builder", path: "/workflow" },
      { label: "Page Manager", path: "/page-manager" },
    ],
  },
  {
    title: "Create",
    items: [
      { label: "Resume - Simple", path: "/tool/resume-builder?template_style=simple" },
      { label: "Resume - Modern", path: "/tool/resume-builder?template_style=modern" },
      { label: "Handwriting Notes", path: "#", soon: true },
    ],
  },
  {
    title: "AI Tools",
    items: [
      { label: "AI Summarization", path: "/tool/ai-summarize" },
      { label: "AI Translation", path: "/tool/ai-translate" },
      { label: "Chat with PDF", path: "/tool/chat-pdf" },
      { label: "Extract Data", path: "/tool/ai-extract" },
      { label: "Hindi / Scanned OCR", path: "/tool/hindi-ocr" },
      { label: "Context Visualizer", path: "#", soon: true },
      { label: "Handwriting Notes", path: "/tool/handwriting" },
      { label: "AI Answer Draft", path: "/tool/ai-draft" },

    ],
  },
];