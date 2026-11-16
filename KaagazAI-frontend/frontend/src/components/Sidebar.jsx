import { Link, useLocation } from "react-router-dom";
import { NAV_SECTIONS } from "../config/navConfig";

const COLORS = {
  violet: { title: "text-violet-300", dot: "bg-violet-400", active: "bg-linear-to-r from-violet-500 to-purple-600 text-white shadow-lg shadow-violet-500/30", hover: "hover:bg-violet-500/15 hover:text-violet-200" },
  blue: { title: "text-sky-300", dot: "bg-sky-400", active: "bg-linear-to-r from-sky-500 to-blue-600 text-white shadow-lg shadow-blue-500/30", hover: "hover:bg-sky-500/15 hover:text-sky-200" },
  emerald: { title: "text-emerald-300", dot: "bg-emerald-400", active: "bg-linear-to-r from-emerald-500 to-green-600 text-white shadow-lg shadow-emerald-500/30", hover: "hover:bg-emerald-500/15 hover:text-emerald-200" },
  fuchsia: { title: "text-fuchsia-300", dot: "bg-fuchsia-400", active: "bg-linear-to-r from-fuchsia-500 to-pink-600 text-white shadow-lg shadow-fuchsia-500/30", hover: "hover:bg-fuchsia-500/15 hover:text-fuchsia-200" },
  amber: { title: "text-amber-300", dot: "bg-amber-400", active: "", hover: "" },
};

export default function Sidebar() {
  const { pathname, search } = useLocation();
  const isActive = (path) =>
    path.includes("?") ? pathname + search === path : pathname === path;

  return (
    <aside className="sticky top-0 hidden h-screen w-64 shrink-0 overflow-y-auto border-r border-white/10 bg-linear-to-b from-slate-950 via-indigo-950 to-slate-950 px-3 py-5 md:block">
      {NAV_SECTIONS.map((section) => {
        const c = COLORS[section.color];
        return (
          <div key={section.title} className="mb-6">
            <h4 className={`mb-2 flex items-center gap-2 px-3 text-[11px] font-bold uppercase tracking-wider ${c.title}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${c.dot}`} />
              {section.title}
            </h4>
            {section.items.map((item) =>
              item.soon ? (
                <span key={item.label} className="flex cursor-not-allowed items-center justify-between rounded-lg px-3 py-2 text-sm text-slate-500">
                  {item.label}
                  <small className="rounded-full bg-amber-400/15 px-2 py-0.5 text-[10px] text-amber-300">Soon</small>
                </span>
              ) : (
                <Link
                  key={item.label}
                  to={item.path}
                  className={
                    "block rounded-lg px-3 py-2 text-sm font-medium transition " +
                    (isActive(item.path) ? c.active : `text-slate-300 ${c.hover}`)
                  }
                >
                  {item.label}
                </Link>
              )
            )}
          </div>
        );
      })}
    </aside>
  );
}