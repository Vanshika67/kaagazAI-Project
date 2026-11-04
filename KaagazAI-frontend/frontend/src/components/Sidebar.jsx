import { Link, useLocation } from "react-router-dom";
import { NAV_SECTIONS } from "../config/navConfig";

export default function Sidebar() {
  const { pathname, search } = useLocation();
  const isActive = (path) =>
    path.includes("?") ? pathname + search === path : pathname === path;

  return (
    <aside className="sticky top-0 hidden h-screen w-60 shrink-0 overflow-y-auto border-r border-white/10 bg-slate-950 px-3 py-5 md:block">
      {NAV_SECTIONS.map((section) => (
        <div key={section.title} className="mb-6">
          <h4 className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            {section.title}
          </h4>
          {section.items.map((item) =>
            item.soon ? (
              <span key={item.label} className="flex cursor-not-allowed items-center justify-between rounded-lg px-3 py-2 text-sm text-slate-500">
                {item.label}
                <small className="rounded-full bg-white/10 px-2 py-0.5 text-[10px]">Soon</small>
              </span>
            ) : (
              <Link
                key={item.label}
                to={item.path}
                className={
                  "block rounded-lg px-3 py-2 text-sm transition " +
                  (isActive(item.path) ? "bg-indigo-600 text-white" : "text-slate-300 hover:bg-white/5")
                }
              >
                {item.label}
              </Link>
            )
          )}
        </div>
      ))}
    </aside>
  );
}