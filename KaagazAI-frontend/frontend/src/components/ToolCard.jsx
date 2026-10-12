import { Link } from "react-router-dom";

/** Dark "glass" tool card with a glow in the category colour. */
export default function ToolCard({ to, icon, name, description, theme }) {
  return (
    <Link
      to={to}
      className={`group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur transition duration-300 hover:-translate-y-1 hover:bg-white/10 hover:shadow-xl ${theme.hover}`}
    >
      <div className={`pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-linear-to-br ${theme.gradient} opacity-20 blur-xl transition duration-300 group-hover:opacity-70`} />
      <div className={`relative mb-3 grid h-11 w-11 place-items-center rounded-xl text-2xl ${theme.tile}`}>{icon}</div>
      <h3 className="relative font-semibold text-white">{name}</h3>
      <p className="relative mt-1 text-sm text-slate-400">{description}</p>
      <span className={`relative mt-3 inline-block text-sm font-medium opacity-0 transition duration-300 group-hover:opacity-100 ${theme.text}`}>
        Open →
      </span>
    </Link>
  );
}
