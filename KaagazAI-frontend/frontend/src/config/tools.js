/**
 * tools.js - describes every tool in one place.
 * The generic ToolPage reads this config and builds the form, so adding
 * a new tool later = adding one object here (no new React page needed).
 *
 * Field types: file | text | number | select | textarea | password
 * A field is required unless it has `optional: true`.
 *
 * IMPORTANT: every field `name` must match the backend parameter name
 * exactly (check http://127.0.0.1:8000/docs).
 */

import { LANGUAGE_OPTIONS, TRANSLATE_OPTIONS } from "./languages";

export const CATEGORIES = [
  { id: "organize", name: "Organize PDF", icon: "🗂️" },
  { id: "convert", name: "Convert", icon: "🔄" },
  { id: "optimize", name: "Optimize", icon: "⚡" },
  { id: "security", name: "Security", icon: "🔒" },
  { id: "edit", name: "Edit & Forms", icon: "✏️" },
  { id: "ai", name: "AI Tools", icon: "🤖" },
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
  {
    id: "label-organize", name: "Label & Organize Documents", icon: "🗂️", category: "organize",
    description: "Combine photos of multiple documents (Aadhaar, PAN, etc.) into one labeled PDF.",
    endpoint: "/api/tools/label-organize", output: "my_documents.pdf",
    fields: [
      { name: "files", label: "Document photos (in order)", type: "file", multiple: true, accept: IMAGES },
      { name: "groups", label: "Groups (JSON)", type: "textarea",
        placeholder: '[{"label": "Aadhaar Card", "count": 2}, {"label": "PAN Card", "count": 2}, {"label": "Bhamashah Card", "count": 2}]',
        help: "Each group's count must match how many photos you uploaded for it, in the same order (e.g. Aadhaar front, Aadhaar back, then PAN front, PAN back...)." },
    ],
  },
  // --- new organize tools ---
  {
    id: "split-size", name: "Split by Size", icon: "📏", category: "organize",
    description: "Split a big PDF into parts, each under a size limit (ZIP).",
    endpoint: "/api/api/split-size", output: "split-by-size.zip",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "max_mb", label: "Max size per part (MB)", type: "number", default: "1", optional: true },
    ],
  },
  {
    id: "split-smart", name: "Split by Blank Page / Bookmarks", icon: "✂️", category: "organize",
    description: "Automatically split a PDF at blank pages or top-level bookmarks (ZIP).",
    endpoint: "/api/api/split-smart", output: "split.zip",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "mode", label: "Split at", type: "select", default: "blank",
        options: [{ value: "blank", label: "Blank pages" }, { value: "bookmarks", label: "Bookmarks" }] },
    ],
  },
  {
    id: "nup", name: "N-up / Booklet", icon: "📚", category: "organize",
    description: "Put 2 or 4 pages on one sheet, or make a printable booklet.",
    endpoint: "/api/api/nup", output: "n-up.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "mode", label: "Mode", type: "select", default: "nup",
        options: [{ value: "nup", label: "N-up (pages per sheet)" }, { value: "booklet", label: "Booklet (print double-sided)" }] },
      { name: "per_sheet", label: "Pages per sheet", type: "select", default: "4", optional: true,
        options: [{ value: "2", label: "2 per sheet" }, { value: "4", label: "4 per sheet" }],
        help: "Only used in N-up mode." },
    ],
  },
  {
    id: "resize-page", name: "Resize Page", icon: "📐", category: "organize",
    description: "Change the page size to A4, Letter and more.",
    endpoint: "/api/api/resize-page", output: "resized.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "size", label: "Page size", type: "select", default: "A4",
        options: [
          { value: "A4", label: "A4" }, { value: "A3", label: "A3" }, { value: "A5", label: "A5" },
          { value: "Letter", label: "Letter" }, { value: "Legal", label: "Legal" },
        ] },
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
    id: "pdf-to-pages", name: "PDF to Pages", icon: "🗃️", category: "convert",
    description: "Save each PDF page as a separate image (PNG or JPG) in a ZIP.",
    endpoint: "/api/convert/pdf-to-pages", output: "pages.zip",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "image_format", label: "Image format", type: "select", default: "png", optional: true,
        options: [{ value: "png", label: "PNG" }, { value: "jpg", label: "JPG" }] },
      { name: "dpi", label: "Quality (DPI)", type: "number", default: "150", optional: true },
    ],
  },
  {
    id: "office-to-pdf", name: "Word / Excel / PPT to PDF", icon: "📝", category: "convert",
    description: "Convert Office documents to PDF.",
    endpoint: "/api/convert/office-to-pdf", output: "converted.pdf",
    fields: [{ name: "file", label: "Office file", type: "file", accept: ".doc,.docx,.xls,.xlsx,.ppt,.pptx" }],
  },
  {
    id: "pdf-to-word", name: "PDF to Word", icon: "📘", category: "convert",
    description: "Convert a PDF into an editable Word document.",
    endpoint: "/api/convert/pdf-to-word", output: "converted.docx",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "pdf-to-excel", name: "PDF to Excel", icon: "📗", category: "convert",
    description: "Extract tables from a PDF into an Excel sheet.",
    endpoint: "/api/convert/pdf-to-excel", output: "converted.xlsx",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "pdf-to-pptx", name: "PDF to PowerPoint", icon: "📙", category: "convert",
    description: "Turn every PDF page into a PowerPoint slide.",
    endpoint: "/api/convert/pdf-to-pptx", output: "converted.pptx",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "dpi", label: "Slide quality (DPI)", type: "number", default: "150", optional: true },
    ],
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
  // --- new convert tools ---
  {
    id: "pdf-to-text", name: "PDF to Text", icon: "📃", category: "convert",
    description: "Extract all text from a PDF as a .txt file.",
    endpoint: "/api/api/pdf-to-text", output: "output.txt",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "pdf-to-csv", name: "PDF to CSV", icon: "📊", category: "convert",
    description: "Extract tables from a PDF into a CSV file.",
    endpoint: "/api/api/pdf-to-csv", output: "tables.csv",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "pdf-to-pdfa", name: "PDF to PDF/A", icon: "🗄️", category: "convert",
    description: "Convert a PDF to the PDF/A archive format (needs Ghostscript).",
    endpoint: "/api/api/pdf-to-pdfa", output: "pdfa.pdf",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "markdown-to-pdf", name: "Markdown to PDF", icon: "🧾", category: "convert",
    description: "Paste Markdown and get a PDF.",
    endpoint: "/api/api/markdown-to-pdf", output: "markdown.pdf",
    fields: [{ name: "text", label: "Markdown", type: "textarea", placeholder: "# Hello\n\nWrite here..." }],
  },
  {
    id: "table-to-pdf", name: "CSV / JSON to PDF Table", icon: "🧮", category: "convert",
    description: "Turn a CSV or JSON file into a formatted PDF table.",
    endpoint: "/api/api/table-to-pdf", output: "table.pdf",
    fields: [{ name: "file", label: "CSV or JSON file", type: "file", accept: ".csv,.json" }],
  },
  {
    id: "url-to-pdf", name: "URL to PDF", icon: "🔗", category: "convert",
    description: "Save a public webpage as a PDF.",
    endpoint: "/api/api/url-to-pdf", output: "webpage.pdf",
    fields: [{ name: "url", label: "Page URL", type: "text", placeholder: "https://example.com" }],
  },
  {
    id: "passport-photo", name: "Passport Photo Maker", icon: "🧑", category: "convert",
    description: "35x45 mm photo at 300 DPI, or a 4x6 sheet with 6 copies.",
    endpoint: "/api/api/passport-photo", output: "passport-photo.jpg",
    fields: [
      { name: "file", label: "Photo", type: "file", accept: IMAGES },
      { name: "sheet", label: "4x6 sheet with 6 copies?", type: "select", default: "no",
        options: [{ value: "no", label: "No, single photo" }, { value: "yes", label: "Yes, 6-copy sheet" }] },
    ],
  },
  {
    id: "remove-bg", name: "Remove Background", icon: "🪄", category: "convert",
    description: "Make the image background transparent.",
    endpoint: "/api/api/remove-bg", output: "no-background.png",
    fields: [{ name: "file", label: "Image", type: "file", accept: IMAGES }],
  },

  // ---------- Optimize ----------
  {
    id: "compress", name: "Compress PDF", icon: "📦", category: "optimize",
    description: "Reduce the file size of a PDF.",
    endpoint: "/api/api/pdf/compress", output: "compressed.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "quality", label: "Quality", type: "select", default: "medium",
        options: [{ value: "low", label: "Smallest file" }, { value: "medium", label: "Balanced" }, { value: "high", label: "Best quality" }] },
    ],
  },
  {
    id: "repair", name: "Repair PDF", icon: "🛠️", category: "optimize",
    description: "Try to fix a damaged or corrupted PDF.",
    endpoint: "/api/api/pdf/repair", output: "repaired.pdf",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "ocr", name: "OCR PDF", icon: "🔍", category: "optimize",
    description: "Make a scanned PDF searchable and copyable.",
    endpoint: "/api/api/pdf/ocr", output: "ocr.pdf",
    fields: [
      { name: "file", label: "Scanned PDF", type: "file", accept: PDF },
      { name: "language", label: "Language code", type: "text", default: "eng", optional: true,
        help: "eng = English. Other languages need their Tesseract language pack installed." },
      { name: "dpi", label: "Scan quality (DPI)", type: "number", default: "200", optional: true },
    ],
  },
  // --- new optimize tools ---
  {
    id: "compress-target", name: "Compress to Target Size", icon: "🎯", category: "optimize",
    description: "Shrink a PDF to your target size, e.g. under 200 KB for form uploads.",
    endpoint: "/api/api/compress-target", output: "compressed.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "target_kb", label: "Target size (KB)", type: "number", default: "200" },
    ],
  },
  {
    id: "grayscale", name: "Grayscale PDF", icon: "⚫", category: "optimize",
    description: "Convert a colour PDF to black and white. Text becomes an image (not selectable).",
    endpoint: "/api/api/grayscale", output: "grayscale.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "dpi", label: "Quality (DPI)", type: "number", default: "150", optional: true,
        help: "Lower DPI (100-120) gives a smaller file." },
    ],
  },
  {
    id: "image-compress", name: "Image Compress", icon: "🗜️", category: "optimize",
    description: "Reduce the size of a JPG/PNG.",
    endpoint: "/api/api/image-compress", output: "compressed.jpg",
    fields: [
      { name: "file", label: "Image", type: "file", accept: IMAGES },
      { name: "quality", label: "Quality (5-95)", type: "number", default: "70", optional: true },
      { name: "max_width", label: "Max width in px (0 = keep)", type: "number", default: "0", optional: true },
    ],
  },
  {
    id: "photo-resize", name: "Photo Resizer (exact KB)", icon: "📸", category: "optimize",
    description: "Resize a photo or signature under a target size for exam and government forms.",
    endpoint: "/api/api/photo-resize", output: "resized.jpg",
    fields: [
      { name: "file", label: "Photo / signature", type: "file", accept: IMAGES },
      { name: "target_kb", label: "Target size (KB)", type: "number", default: "50" },
      { name: "width", label: "Width in px (0 = original)", type: "number", default: "0", optional: true,
        help: "Passport photo is usually 200x230, signature 140x60. Check your form's rules." },
      { name: "height", label: "Height in px (0 = original)", type: "number", default: "0", optional: true },
    ],
  },

  // ---------- Security ----------
  {
    id: "protect", name: "Protect File", icon: "🔐", category: "security",
    description: "Lock a PDF, Word, Excel, PowerPoint or any other file with a password.",
    endpoint: "/api/api/security/protect", output: "protected_file",
    fields: [
      { name: "file", label: "File", type: "file", accept: "*/*" },
      { name: "password", label: "Password", type: "password" },
    ],
  },
  {
    id: "unlock", name: "Unlock File", icon: "🔓", category: "security",
    description: "Remove the password from a protected PDF, Word, Excel, PowerPoint or ZIP file.",
    endpoint: "/api/api/security/unlock", output: "unlocked_file",
    fields: [
      { name: "file", label: "Protected file", type: "file", accept: "*/*" },
      { name: "password", label: "Current password", type: "password" },
    ],
  },
  {
    id: "crack-password", name: "Recover Forgotten Password", icon: "🔑", category: "security",
    description: "Try to unlock a PDF, Word, Excel or PowerPoint file you forgot the password to.",
    endpoint: "/api/api/security/crack-password", output: "unlocked_file",
    fields: [
      { name: "file", label: "Protected file", type: "file", accept: ".pdf,.docx,.xlsx,.pptx" },
      { name: "wordlist", label: "Wordlist (.txt, one password per line)", type: "file", accept: ".txt", optional: true },
      { name: "use_digits_bruteforce", label: "Also try numeric passwords", type: "select", default: "false",
        options: [{ value: "false", label: "No" }, { value: "true", label: "Yes (slow)" }] },
      { name: "min_length", label: "Min length (numeric)", type: "number", default: "4", optional: true },
      { name: "max_length", label: "Max length (numeric)", type: "number", default: "6", optional: true },
      { name: "max_attempts", label: "Max attempts", type: "number", default: "20000", optional: true },
    ],
  },
  {
    id: "watermark", name: "Watermark PDF", icon: "💧", category: "security",
    description: "Add a diagonal text watermark to every page.",
    endpoint: "/api/api/pdf/watermark", output: "watermarked.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "text", label: "Watermark text", type: "text", default: "CONFIDENTIAL" },
    ],
  },
  {
    id: "redact", name: "Redact PDF", icon: "⬛", category: "security",
    description: "Permanently black out and delete sensitive text.",
    endpoint: "/api/api/pdf/redact", output: "redacted.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "terms", label: "Text to redact", type: "text", placeholder: "Account number, phone, name",
        help: "Separate multiple words with commas. Works on text PDFs; for scanned PDFs run OCR first." },
    ],
  },
  // --- new security tools ---
  {
    id: "flatten", name: "Flatten PDF", icon: "🧱", category: "security",
    description: "Make form fields and annotations permanent so they can't be edited.",
    endpoint: "/api/api/flatten", output: "flattened.pdf",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "remove-metadata", name: "Remove Metadata", icon: "🧹", category: "security",
    description: "Erase author, title and hidden info from a PDF.",
    endpoint: "/api/api/remove-metadata", output: "clean.pdf",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },
  {
    id: "digital-sign", name: "Digital Signature", icon: "🪪", category: "security",
    description: "Sign a PDF with your .p12 / .pfx certificate.",
    endpoint: "/api/api/digital-sign", output: "signed.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "cert", label: "Certificate (.p12 / .pfx)", type: "file", accept: ".p12,.pfx" },
      { name: "password", label: "Certificate password", type: "password", optional: true },
    ],
  },
  {
    id: "auto-redact", name: "Auto Redact", icon: "🕶️", category: "security",
    description: "Detect and black out email, phone, Aadhaar and PAN automatically (text PDFs only).",
    endpoint: "/api/api/auto-redact", output: "redacted.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "types", label: "What to hide", type: "text", default: "email,phone,aadhaar,pan", optional: true,
        help: "Comma separated. Options: email, phone, aadhaar, pan." },
    ],
  },
  {
    id: "aadhaar-mask", name: "Aadhaar Masking", icon: "🙈", category: "security",
    description: "Hide the first 8 digits of Aadhaar numbers. Works on text PDFs only.",
    endpoint: "/api/api/aadhaar-mask", output: "aadhaar-masked.pdf",
    fields: [{ name: "file", label: "PDF file", type: "file", accept: PDF }],
  },

  // ---------- Edit & Forms ----------
  {
    id: "edit-add-text", name: "Edit PDF (Add Text)", icon: "✍️", category: "edit",
    description: "Write new text onto a page at a position you choose.",
    endpoint: "/api/api/pdf/edit-add-text", output: "edited.pdf",
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
    endpoint: "/api/api/pdf/sign", output: "signed.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "signature", label: "Signature image (PNG/JPG)", type: "file", accept: IMAGES },
      { name: "page_number", label: "Page number", type: "number", default: "1", optional: true },
      { name: "x", label: "X position (from left)", type: "number", default: "72", optional: true,
        help: "In points. A4 page is about 595 wide and 842 tall." },
      { name: "y", label: "Y position (from top)", type: "number", default: "650", optional: true },
      { name: "width", label: "Signature width", type: "number", default: "150", optional: true },
      { name: "height", label: "Signature height", type: "number", default: "60", optional: true },
    ],
  },
  {
    id: "form-fields", name: "List Form Fields", icon: "📋", category: "edit",
    description: "See the names of the fillable fields inside a PDF form.",
    endpoint: "/api/api/pdf/form-fields", output: "form_fields.json",
    fields: [{ name: "file", label: "PDF form", type: "file", accept: PDF }],
  },
  {
    id: "fill-form", name: "Fill PDF Form", icon: "🧾", category: "edit",
    description: "Fill a fillable PDF form. Use 'List Form Fields' first to get the field names.",
    endpoint: "/api/api/pdf/fill-form", output: "filled_form.pdf",
    fields: [
      { name: "file", label: "PDF form", type: "file", accept: PDF },
      { name: "fields", label: "Field values (JSON)", type: "textarea",
        placeholder: '{"Name": "Vanshika", "Agree": true}',
        help: "Field names are case-sensitive and must match 'List Form Fields'." },
    ],
  },
  {
    id: "compare", name: "Compare PDFs", icon: "⚖️", category: "edit",
    description: "Find the text differences between two PDFs.",
    endpoint: "/api/api/pdf/compare", output: "compare.json",
    fields: [
      { name: "file1", label: "First PDF", type: "file", accept: PDF },
      { name: "file2", label: "Second PDF", type: "file", accept: PDF },
    ],
  },
  {
    id: "generate-document", name: "Generate Document", icon: "🪪", category: "edit",
    description: "Fill a sample ID card or marksheet template and get a PDF (demo use only).",
    endpoint: "/api/api/tools/generate-document-form", output: "document.pdf",
    fields: [
      { name: "template_key", label: "Template", type: "select", default: "marksheet",
        options: [{ value: "marksheet", label: "Marksheet" }, { value: "generic_id_card", label: "ID card" }] },
      { name: "document_title", label: "Title", type: "text", default: "Sample Document" },
      { name: "fields", label: "Fields (JSON)", type: "textarea",
        placeholder: '[{"label": "Student Name", "value": "Test"}, {"label": "Roll No", "value": "123"}]' },
    ],
  },
  {
    id: "resume-builder", name: "Resume Builder", icon: "📄", category: "edit",
    description: "Build a resume in a simple ATS-friendly style, or a colorful modern 2-column style with a photo.",
    endpoint: "/api/api/tools/resume-builder", output: "resume.pdf",
    fields: [
      { name: "template_style", label: "Template", type: "select", default: "simple",
        options: [
          { value: "simple", label: "Simple (ATS-friendly, no photo)" },
          { value: "modern", label: "Modern (colorful, 2-column, photo)" },
        ] },
      { name: "output_format", label: "Format", type: "select", default: "pdf",
        options: [{ value: "pdf", label: "PDF" }, { value: "word", label: "Word (editable)" }],
        help: "The Modern look (sidebar + photo) only applies to PDF. Word is always single-column." },
      { name: "photo", label: "Photo (only used for Modern PDF)", type: "file", accept: IMAGES, optional: true },
      { name: "full_name", label: "Full name", type: "text" },
      { name: "email", label: "Email", type: "text", optional: true },
      { name: "phone", label: "Phone", type: "text", optional: true },
      { name: "location", label: "Location", type: "text", optional: true },
      { name: "summary", label: "Professional summary", type: "textarea", optional: true,
        placeholder: "2-3 lines about yourself" },
      { name: "education", label: "Education", type: "textarea", optional: true,
        placeholder: "B.Tech CSE, XYZ University, 2022-2026\n12th, ABC School, 2022" },
      { name: "experience", label: "Experience", type: "textarea", optional: true,
        placeholder: "Software Intern at ABC Pvt Ltd (Jun-Aug 2025)\nBuilt a PDF tools web app" },
      { name: "skills", label: "Skills", type: "textarea", optional: true,
        placeholder: "Python\nReact\nFastAPI" },
      { name: "projects", label: "Projects", type: "textarea", optional: true },
      { name: "certifications", label: "Certifications", type: "textarea", optional: true },
    ],
  },
  // NEW: Handwriting Notes (apne handwriting font mein ruled-page PDF)
  {
    id: "handwriting", name: "Handwriting Notes", icon: "📓", category: "edit",
    description: "Apne handwriting font mein ruled-page notes PDF banao.",
    endpoint: "/api/api/tools/handwriting", output: "handwriting_notes.pdf",
    fields: [
      { name: "font", label: "Aapka handwriting font (.ttf / .otf)", type: "file", accept: ".ttf,.otf", optional: true,
        help: "Apni handwriting se font banane ke liye Calligraphr jaisa free tool use karo. Khaali chhodoge to default font use hoga." },
      { name: "text", label: "Notes / answer text", type: "textarea", placeholder: "Yahan apna text likho ya paste karo..." },
      { name: "font_size", label: "Font size", type: "number", default: "18", optional: true },
      { name: "line_spacing", label: "Line spacing (1.2 - 3)", type: "number", default: "1.6", optional: true },
      { name: "margin", label: "Margin (points)", type: "number", default: "50", optional: true },
      { name: "max_pages", label: "Max pages (0 = no limit)", type: "number", default: "0", optional: true },
      { name: "ink", label: "Ink colour", type: "select", default: "blue",
        options: [{ value: "blue", label: "Blue" }, { value: "dark_blue", label: "Dark blue" }, { value: "black", label: "Black" }] },
      { name: "ruled", label: "Ruled lines", type: "select", default: "yes",
        options: [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }] },
    ],
  },
  // --- new edit tools ---
  {
    id: "edit-metadata", name: "Edit Metadata", icon: "🏷️", category: "edit",
    description: "Change the title, author, subject and keywords of a PDF.",
    endpoint: "/api/api/edit-metadata", output: "metadata-updated.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "title", label: "Title", type: "text", optional: true },
      { name: "author", label: "Author", type: "text", optional: true },
      { name: "subject", label: "Subject", type: "text", optional: true },
      { name: "keywords", label: "Keywords", type: "text", optional: true },
    ],
  },
  {
    id: "header-footer", name: "Add Header / Footer", icon: "📑", category: "edit",
    description: "Add text at the top and bottom of every page.",
    endpoint: "/api/api/header-footer", output: "header-footer.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "header", label: "Header text", type: "text", optional: true },
      { name: "footer", label: "Footer text", type: "text", optional: true },
      { name: "fontsize", label: "Font size", type: "number", default: "10", optional: true },
    ],
  },
  {
    id: "highlight", name: "Highlight Text", icon: "🖍️", category: "edit",
    description: "Highlight words in a PDF. Separate multiple words with commas.",
    endpoint: "/api/api/highlight", output: "highlighted.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "text", label: "Words to highlight", type: "text", placeholder: "invoice, total, due date" },
    ],
  },
  {
    id: "qr-pdf", name: "Add QR Code", icon: "🔳", category: "edit",
    description: "Stamp a QR code on your PDF pages.",
    endpoint: "/api/api/qr-pdf", output: "with-qr.pdf",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "text", label: "QR content (link or text)", type: "text", placeholder: "https://example.com" },
      { name: "position", label: "Position", type: "select", default: "br",
        options: [
          { value: "br", label: "Bottom right" }, { value: "bl", label: "Bottom left" },
          { value: "tr", label: "Top right" }, { value: "tl", label: "Top left" },
        ] },
      { name: "pages", label: "Pages", type: "select", default: "all",
        options: [{ value: "all", label: "All pages" }, { value: "first", label: "First page only" }] },
      { name: "size", label: "Size (points)", type: "number", default: "80", optional: true },
    ],
  },
  {
    id: "invoice", name: "Invoice Generator", icon: "💰", category: "edit",
    description: "Create a GST invoice PDF.",
    endpoint: "/api/api/invoice", output: "invoice.pdf",
    fields: [
      { name: "seller", label: "Seller name & address", type: "text" },
      { name: "buyer", label: "Buyer name & address", type: "text" },
      { name: "invoice_no", label: "Invoice number", type: "text", default: "INV-001" },
      { name: "items", label: "Items (one per line: Item, Qty, Rate)", type: "textarea",
        placeholder: "Website design, 1, 15000\nHosting, 12, 500" },
      { name: "gst", label: "GST %", type: "number", default: "18" },
    ],
  },

  // ---------- AI Tools ----------
  {
    id: "chat-pdf", name: "Chat with PDF", icon: "💬", category: "ai",
    description: "Upload a PDF and ask questions about it using AI.",
    // Custom page: needs <Route path="/tool/chat-pdf" element={<ChatPdf />} /> ABOVE the /tool/:id route.
    custom: true,
    fields: [],
  },
 
    {
    id: "ai-summarize", name: "AI Summarizer", icon: "🧠", category: "ai",
    description: "Get a summary of any text PDF in the language you choose.",
    endpoint: "/api/api/ai-summarize", output: "summary.txt",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "length", label: "Length", type: "select", default: "medium",
        options: [{ value: "short", label: "Short" }, { value: "medium", label: "Medium" }, { value: "detailed", label: "Detailed" }] },
      { name: "language", label: "Summary language", type: "select", default: "English",
        options: LANGUAGE_OPTIONS },
    ],
  },
  {
    id: "ai-extract", name: "Extract Data (Invoice / Resume)", icon: "🗃️", category: "ai",
    description: "Turn an invoice or resume PDF into structured JSON or Excel.",
    endpoint: "/api/api/ai-extract", output: "data.json",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "doc_type", label: "Document type", type: "select", default: "invoice",
        options: [{ value: "invoice", label: "Invoice" }, { value: "resume", label: "Resume" }, { value: "other", label: "Other" }] },
      { name: "fmt", label: "Output", type: "select", default: "json",
        options: [{ value: "json", label: "JSON" }, { value: "xlsx", label: "Excel (.xlsx)" }] },
    ],
  },
  {
    id: "hindi-ocr", name: "Hindi / Scanned OCR", icon: "🔤", category: "ai",
    description: "Read Hindi + English text from scanned PDFs or photos (downloads a .txt file).",
    endpoint: "/api/api/hindi-ocr", output: "ocr.txt",
    fields: [
      { name: "file", label: "Scanned PDF or photo", type: "file", accept: ".pdf,image/*" },
      { name: "lang", label: "Language code", type: "text", default: "hin+eng", optional: true,
        help: "hin+eng = Hindi + English. Hindi language data must be installed in Tesseract." },
    ],
  },
    {
    id: "ai-draft", name: "AI Answer Draft", icon: "📝", category: "ai",
    description: "Question daalo, AI answer ka draft banayega. Edit karo aur apni handwriting mein PDF banao.",
    // Custom page: App.jsx mein /tool/ai-draft route /tool/:id se pehle hai.
    custom: true,
    fields: [],
  },
    {
    id: "ai-translate", name: "PDF Translation", icon: "🌍", category: "ai",
    description: "Translate a PDF into 30+ Indian and international languages (downloads a .txt file).",
    endpoint: "/api/api/ai-translate", output: "translated.txt",
    fields: [
      { name: "file", label: "PDF file", type: "file", accept: PDF },
      { name: "target", label: "Translate to", type: "select", default: "Hindi",
        options: TRANSLATE_OPTIONS },
    ],
  },
];

export const getTool = (id) => TOOLS.find((t) => t.id === id);