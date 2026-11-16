import { Link, Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Home from "./pages/Home";
import PdfTools from "./pages/PdfTools";
import ToolPage from "./pages/ToolPage";
import WorkflowBuilder from "./pages/WorkflowBuilder";
import PageManager from "./pages/PageManager";
import ChatPdf from "./pages/ChatPdf";
import AiDraft from "./pages/AiDraft";
import HandwritingStudio from "./pages/HandwritingStudio";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="min-w-0 flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/pdf-tools" element={<PdfTools />} />
            <Route path="/handwriting" element={<HandwritingStudio />} />

            {/* Custom pages: /tool/:id se PEHLE rakhna */}
            <Route path="/tool/chat-pdf" element={<ChatPdf />} />
            <Route path="/tool/ai-draft" element={<AiDraft />} />

            <Route path="/tool/:id" element={<ToolPage />} />
            <Route path="/workflow" element={<WorkflowBuilder />} />
            <Route path="/page-manager" element={<PageManager />} />

            <Route
              path="*"
              element={
                <div className="py-24 text-center">
                  <h1 className="text-2xl font-bold">Page not found</h1>
                  <Link to="/" className="mt-3 inline-block text-indigo-600 hover:underline">
                    Go home
                  </Link>
                </div>
              }
            />
          </Routes>
        </main>
      </div>

      <footer className="border-t border-white/10 bg-slate-950 py-6 text-center text-sm text-slate-400">
        KaagazAI &middot; Files are processed temporarily and deleted automatically.
      </footer>
    </div>
  );
}