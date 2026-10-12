import { Link } from "react-router-dom";

/** Colourful banner shown at the top of every tool page. */
export default function PageHeader({ icon, title, description, theme, backTo = "/" }) {
  return (
    <div className={`relative mb-6 overflow-hidden rounded-3xl bg-linear-to-br ${theme.gradient} p-6 text-white shadow-lg sm:p-8`}>
      {/* decorative circles */}
      <div className="pointer-events-none absolute -right-10 -top-10 h-44 w-44 rounded-full bg-white/20" />
      <div className="pointer-events-none absolute -bottom-12 right-24 h-32 w-32 rounded-full bg-white/10" />
      <div className="pointer-events-none absolute -left-8 bottom-0 h-24 w-24 rounded-full bg-black/10" />

      <Link to={backTo} className="relative text-sm font-medium text-white/80 hover:text-white">← All tools</Link>
      <div className="relative mt-3 flex items-center gap-4">
        <span className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-white/20 text-3xl backdrop-blur">{icon}</span>
        <div>
          <h1 className="text-2xl font-extrabold sm:text-3xl">{title}</h1>
          <p className="mt-1 max-w-xl text-white/90">{description}</p>
        </div>
      </div>
    </div>
  );
}
