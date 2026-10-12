/**
 * tools.js - describes every tool in one place.
 * The generic ToolPage reads this config and builds the form, so adding
 * a new tool later = adding one object here (no new React page needed).
 *
 * Field types: file | text | number | select | textarea | password
 * A field is required unless it has `optional: true`.
 */

export const CATEGORIES = [
  { id: "organize", name: "Organize PDF", icon: "🗂️" },
  { id: "convert", name: "Convert", icon: "🔄" },
  { id: "optimize", name: "Optimize", icon: "⚡" },
  { id: "security", name: "Security", icon: "🔒" },
  { id: "edit", name: "Edit & Forms", icon: "✏️" },
];

const PDF = ".pdf";
const IMAGES = "image/*";

export const TOOLS = [
  // ---------- Organize ----------
  {
    id: "merge", name: "Merge PDF", icon: "🔗", category: "organize",
    description: "Combine several PDFs into one, in the order you choose.",
    endpoint: "/api/pdf/merge", output: "merged.pdf",
    fields: [{ name: "files", label: "PDF files (at least 2)", type: "file", multiple: true, accept: PDF }],
  },
  {
    id: "split", name: "Split PDF", icon: "✂️", category: "organize",
    description: "Split a PDF into separate files (one per page, or by page ranges).",
    endpoint: "/api/pdf/split", output: "split_result.zip",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "ranges", label: "Page ranges", type: "text", optional: true, placeholder: "1-3,4-4,5-7",
        help: "Leave empty to get one PDF per page." },
    ],
  },
  {
    id: "insert-page", name: "Insert Page", icon: "➕", category: "organize",
    description: "Insert pages from another PDF at an exact position (not just first or last).",
    endpoint: "/api/pdf/insert-page", output: "inserted.pdf",
    fields: [
      { name: "original_file", label: "Original PDF", type: "file", accept: PDF },
      { name: "new_pages_file", label: "PDF with the page(s) to insert", type: "file", accept: PDF },
      { name: "after_page", label: "Insert after page number", type: "number", placeholder: "5",
        help: "Use 0 to insert at the very beginning." },
    ],
  },
  {
    id: "delete-pages", name: "Delete Pages", icon: "🗑️", category: "organize",
    description: "Remove the pages you don't need.",
    endpoint: "/api/pdf/delete-pages", output: "deleted_pages.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "pages", label: "Pages to delete", type: "text", placeholder: "2,5,7" },
    ],
  },
  {
    id: "extract-pages", name: "Extract Pages", icon: "📑", category: "organize",
    description: "Create a new PDF from selected pages, in the order you type them.",
    endpoint: "/api/pdf/extract-pages", output: "extracted.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "pages", label: "Pages to extract", type: "text", placeholder: "3,1,5" },
    ],
  },
  {
    id: "reorder-pages", name: "Reorder Pages", icon: "🔀", category: "organize",
    description: "Rearrange all pages into a new order.",
    endpoint: "/api/pdf/reorder-pages", output: "reordered.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "new_order", label: "New order", type: "text", placeholder: "3,1,2",
        help: "Every page number must appear exactly once." },
    ],
  },
  {
    id: "remove-blank-pages", name: "Remove Blank Pages", icon: "📄", category: "organize",
    description: "Detect and delete empty pages automatically.",
    endpoint: "/api/pdf/remove-blank-pages", output: "no_blanks.pdf",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "rotate", name: "Rotate PDF", icon: "🔃", category: "organize",
    description: "Rotate all pages, or only the ones you pick.",
    endpoint: "/api/pdf/rotate", output: "rotated.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "angle", label: "Angle", type: "select", default: "90",
        options: [{ value: "90", label: "90° clockwise" }, { value: "180", label: "180°" }, { value: "270", label: "90° counter-clockwise" }] },
      { name: "pages", label: "Only these pages", type: "text", optional: true, placeholder: "1,3",
        help: "Leave empty to rotate every page." },
    ],
  },
  {
    id: "crop", name: "Crop PDF", icon: "🔲", category: "organize",
    description: "Trim margins off every page (values in points, 72 points = 1 inch).",
    endpoint: "/api/pdf/crop", output: "cropped.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "left", label: "Trim left", type: "number", default: "0", optional: true },
      { name: "right", label: "Trim right", type: "number", default: "0", optional: true },
      { name: "top", label: "Trim top", type: "number", default: "0", optional: true },
      { name: "bottom", label: "Trim bottom", type: "number", default: "0", optional: true },
    ],
  },
  {
    id: "add-page-numbers", name: "Add Page Numbers", icon: "🔢", category: "organize",
    description: "Stamp page numbers like '3 / 10' on every page.",
    endpoint: "/api/pdf/add-page-numbers", output: "numbered.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "position", label: "Position", type: "select", default: "bottom-center",
        options: [{ value: "bottom-center", label: "Bottom center" }, { value: "bottom-right", label: "Bottom right" }, { value: "bottom-left", label: "Bottom left" }] },
    ],
  },

  // ---------- Convert ----------
  {
    id: "images-to-pdf", name: "Images to PDF", icon: "🖼️", category: "convert",
    description: "Turn JPG/PNG images into one PDF, one image per page.",
    endpoint: "/api/convert/images-to-pdf", output: "images_to_pdf.pdf",
    fields: [{ name: "files", label: "Images", type: "file", multiple: true, accept: IMAGES }],
  },
  {
    id: "pdf-to-images", name: "PDF to Images", icon: "📷", category: "convert",
    description: "Save every PDF page as a PNG image (downloaded as a ZIP).",
    endpoint: "/api/convert/pdf-to-images", output: "pdf_to_images.zip",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "dpi", label: "Quality (DPI)", type: "number", default: "150", optional: true,
        help: "150 is good for screens, 300 for printing." },
    ],
  },
  {
    id: "office-to-pdf", name: "Word / Excel / PPT to PDF", icon: "📝", category: "convert",
    description: "Convert Office documents to PDF.",
    endpoint: "/api/convert/office-to-pdf", output: "converted.pdf",
    fields: [{ name: "file", label: "Office file", type: "file", accept: ".doc,.docx,.xls,.xlsx,.ppt,.pptx" }],
  },
  {
    id: "html-to-pdf", name: "HTML to PDF", icon: "🌐", category: "convert",
    description: "Paste HTML and get a PDF.",
    endpoint: "/api/convert/html-to-pdf", output: "html_to_pdf.pdf",
    fields: [{ name: "html_content", label: "HTML", type: "textarea", placeholder: "<h1>Hello</h1><p>My page</p>" }],
  },
  {
    id: "pdf-to-html", name: "PDF to HTML", icon: "🧩", category: "convert",
    description: "Convert a PDF into an HTML page.",
    endpoint: "/api/convert/pdf-to-html", output: "converted.html",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "pdf-to-markdown", name: "PDF to Markdown", icon: "⬇️", category: "convert",
    description: "Extract text as Markdown, with headings detected from font sizes.",
    endpoint: "/api/convert/pdf-to-markdown", output: "converted.md",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "scan-to-pdf", name: "Scan to PDF", icon: "📱", category: "convert",
    description: "Turn photos of documents into clean, scanner-style PDF pages.",
    endpoint: "/api/convert/scan-to-pdf", output: "scanned.pdf",
    fields: [{ name: "files", label: "Photos", type: "file", multiple: true, accept: IMAGES }],
  },

  // ---------- Optimize ----------
  {
    id: "compress", name: "Compress PDF", icon: "📦", category: "optimize",
    description: "Reduce the file size of a PDF.",
    endpoint: "/api/pdf/compress", output: "compressed.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "quality", label: "Quality", type: "select", default: "medium",
        options: [{ value: "low", label: "Smallest file" }, { value: "medium", label: "Balanced" }, { value: "high", label: "Best quality" }] },
    ],
  },
  {
    id: "repair", name: "Repair PDF", icon: "🛠️", category: "optimize",
    description: "Try to fix a damaged or corrupted PDF.",
    endpoint: "/api/pdf/repair", output: "repaired.pdf",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "ocr", name: "OCR PDF", icon: "🔍", category: "optimize",
    description: "Make a scanned PDF searchable and copyable.",
    endpoint: "/api/pdf/ocr", output: "ocr.pdf",
    fields: [
      { name: "file", label: "Scanned PDF", type: "file", accept: PDF },
      { name: "language", label: "Language code", type: "text", default: "eng", optional: true,
        help: "eng = English. Other languages need their Tesseract language pack installed." },
    ],
  },

  // ---------- Security ----------
  {
    id: "protect", name: "Protect PDF", icon: "🔐", category: "security",
    description: "Lock a PDF with a password.",
    endpoint: "/api/pdf/protect", output: "protected.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "password", label: "Password", type: "password" },
    ],
  },
  {
    id: "unlock", name: "Unlock PDF", icon: "🔓", category: "security",
    description: "Remove the password from a PDF (you need the current password).",
    endpoint: "/api/pdf/unlock", output: "unlocked.pdf",
    fields: [
      { name: "file", label: "Protected PDF", type: "file", accept: PDF },
      { name: "password", label: "Current password", type: "password" },
    ],
  },
  {
    id: "watermark", name: "Watermark PDF", icon: "💧", category: "security",
    description: "Add a diagonal text watermark to every page.",
    endpoint: "/api/pdf/watermark", output: "watermarked.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "text", label: "Watermark text", type: "text", default: "CONFIDENTIAL" },
    ],
  },
  {
    id: "redact", name: "Redact PDF", icon: "⬛", category: "security",
    description: "Permanently black out and delete sensitive text.",
    endpoint: "/api/pdf/redact", output: "redacted.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "search_text", label: "Text to redact", type: "text", placeholder: "Account number, phone, name..." },
    ],
  },

  // ---------- Edit & Forms ----------
  {
    id: "edit-add-text", name: "Edit PDF (Add Text)", icon: "✍️", category: "edit",
    description: "Write new text onto a page at a position you choose.",
    endpoint: "/api/pdf/edit-add-text", output: "edited.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "page_number", label: "Page number", type: "number", default: "1" },
      { name: "text", label: "Text to add", type: "text" },
      { name: "x", label: "X position (from left)", type: "number", default: "72",
        help: "In points. A4 page is about 595 wide and 842 tall." },
      { name: "y", label: "Y position (from top)", type: "number", default: "100" },
      { name: "font_size", label: "Font size", type: "number", default: "12", optional: true },
    ],
  },
  {
    id: "sign", name: "Sign PDF", icon: "🖊️", category: "edit",
    description: "Place your signature image on a page.",
    endpoint: "/api/pdf/sign", output: "signed.pdf",
    fields: [
      { name: "pdf_file", label: "PDF file", type: "file", accept: PDF },
      { name: "signature_image", label: "Signature image (PNG/JPG)", type: "file", accept: IMAGES },
      { name: "page_number", label: "Page number", type: "number", default: "-1", optional: true,
        help: "-1 means the last page." },
      { name: "position", label: "Position", type: "select", default: "bottom-right",
        options: [{ value: "bottom-right", label: "Bottom right" }, { value: "bottom-left", label: "Bottom left" }, { value: "bottom-center", label: "Bottom center" }] },
    ],
  },
  {
    id: "form-fields", name: "List Form Fields", icon: "📋", category: "edit",
    description: "See the names of the fillable fields inside a PDF form.",
    endpoint: "/api/pdf/form-fields", output: "form_fields.json",
    fields: [{ name: "file", label: "PDF form", type: "file", accept: PDF }],
  },
  {
    id: "fill-form", name: "Fill PDF Form", icon: "🧾", category: "edit",
    description: "Fill a fillable PDF form. Use 'List Form Fields' first to get the field names.",
    endpoint: "/api/pdf/fill-form", output: "filled_form.pdf",
    fields: [
      { name: "file", label: "PDF form", type: "file", accept: PDF },
      { name: "field_values", label: "Field values (JSON)", type: "textarea",
        placeholder: '{"name": "Vanshika", "email": "me@example.com"}' },
    ],
  },
  {
    id: "compare", name: "Compare PDFs", icon: "⚖️", category: "edit",
    description: "Find the text differences between two PDFs.",
    endpoint: "/api/pdf/compare", output: "compare.txt",
    fields: [
      { name: "file_a", label: "First PDF", type: "file", accept: PDF },
      { name: "file_b", label: "Second PDF", type: "file", accept: PDF },
    ],
  },
];

export const getTool = (id) => TOOLS.find((t) => t.id === id);
