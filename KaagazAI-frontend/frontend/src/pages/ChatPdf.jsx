import { useState, useRef, useEffect } from "react";

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export default function ChatPdf() {
  const [docId, setDocId] = useState(null);
  const [fileName, setFileName] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const upload = async (file) => {
    if (!file) return;
    setBusy(true);
    setError("");
    setMessages([]);
    setDocId(null);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res = await fetch(`${API}/api/chat-pdf/upload`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setDocId(data.doc_id);
      setFileName(file.name);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const send = async () => {
    const q = input.trim();
    if (!q || !docId || busy) return;
    const history = messages;
    setMessages([...history, { role: "user", content: q }]);
    setInput("");
    setBusy(true);
    setError("");
    try {
      const res = await fetch(`${API}/api/chat-pdf/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doc_id: docId, question: q, history }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Error");
      setMessages((m) => [...m, { role: "assistant", content: data.answer }]);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 text-white">
      <h1 className="text-3xl font-bold">Chat with PDF</h1>
      <p className="mt-2 text-slate-400">Upload a PDF and ask questions about it.</p>

      <input
        type="file"
        accept=".pdf"
        onChange={(e) => upload(e.target.files[0])}
        className="mt-6 block w-full text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-indigo-600 file:px-4 file:py-2 file:text-white"
      />
      {fileName && <p className="mt-2 text-sm text-emerald-400">Loaded: {fileName}</p>}

      <div className="mt-6 h-96 space-y-3 overflow-y-auto rounded-2xl border border-white/10 bg-white/5 p-4">
        {messages.length === 0 && (
          <p className="text-slate-500">Koi bhi sawal poochhein, jaise "Is document ka summary do".</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : "text-left"}>
            <span
              className={
                "inline-block max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2 " +
                (m.role === "user" ? "bg-indigo-600" : "bg-white/10")
              }
            >
              {m.content}
            </span>
          </div>
        ))}
        {busy && <p className="text-slate-500">{docId ? "Thinking..." : "Uploading..."}</p>}
        <div ref={endRef} />
      </div>

      {error && <p className="mt-2 text-red-400">{error}</p>}

      <div className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={!docId}
          placeholder={docId ? "Apna sawal likhein..." : "Pehle PDF upload karein"}
          className="flex-1 rounded-lg border border-white/10 bg-black/30 px-4 py-3 outline-none focus:border-indigo-500"
        />
        <button
          onClick={send}
          disabled={!docId || busy}
          className="rounded-lg bg-gradient-to-r from-pink-500 to-indigo-500 px-6 font-semibold disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
