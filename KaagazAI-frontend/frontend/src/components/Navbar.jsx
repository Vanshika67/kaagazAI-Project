import { Link, NavLink } from "react-router-dom";

const linkClass = ({ isActive }) =>
  `whitespace-nowrap rounded-lg px-2.5 py-2 text-sm font-medium transition sm:px-3 ${
    isActive ? "bg-white/10 text-white" : "text-slate-300 hover:bg-white/5 hover:text-white"
  }`;

export default function Navbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950 shadow-lg shadow-black/20">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="flex items-center gap-2 text-xl font-extrabold text-white">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-linear-to-br from-amber-300 via-pink-500 to-sky-500 text-slate-950 shadow-lg shadow-pink-500/30">K</span>
          <span>
            Kaagaz<span className="bg-linear-to-r from-amber-300 to-pink-400 bg-clip-text text-transparent">AI</span>
          </span>
        </Link>
        <nav className="flex items-center gap-1">
          <NavLink to="/" end className={linkClass}>
            <span className="hidden sm:inline">All tools</span><span className="sm:hidden">Tools</span>
          </NavLink>
          <NavLink to="/workflow" className={linkClass}>Workflow</NavLink>
          <NavLink to="/page-manager" className={linkClass}>
            <span className="hidden sm:inline">Page Manager</span><span className="sm:hidden">Pages</span>
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
