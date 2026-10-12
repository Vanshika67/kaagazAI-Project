import { Link, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import ToolPage from "./pages/ToolPage";
import WorkflowBuilder from "./pages/WorkflowBuilder";
import PageManager from "./pages/PageManager";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/tool/:id" element={<ToolPage />} />
          <Route path="/workflow" element={<WorkflowBuilder />} />
          <Route path="/page-manager" element={<PageManager />} />
          <Route
            path="*"
            element={
              <div className="py-24 text-center">
                <h1 className="text-2xl font-bold">Page not found</h1>
                <Link to="/" className="mt-3 inline-block text-indigo-600 hover:underline">Go home</Link>
              </div>
            }
          />
        </Routes>
      </main>
      <footer className="border-t border-white/10 bg-slate-950 py-6 text-center text-sm text-slate-400">
        KaagazAI · Files are processed temporarily and deleted automatically.
      </footer>
    </div>
  );
}
