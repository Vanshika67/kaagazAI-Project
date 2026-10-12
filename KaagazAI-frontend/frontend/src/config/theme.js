/**
 * theme.js - the colour palettes used across the dashboard.
 *
 * Class names are written out in full on purpose: Tailwind only creates
 * CSS for class names it can find as complete strings in the source code,
 * so we can't build them like `bg-${color}-500`.
 */
export const THEMES = {
  blue: {
    gradient: "from-sky-400 to-blue-600",
    tile: "bg-blue-500/15 text-blue-300 ring-1 ring-blue-400/30",
    hover: "hover:border-blue-400/60 hover:shadow-blue-500/20",
    text: "text-blue-300",
    badge: "bg-blue-500/15 text-blue-300",
  },
  green: {
    gradient: "from-emerald-400 to-green-600",
    tile: "bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-400/30",
    hover: "hover:border-emerald-400/60 hover:shadow-emerald-500/20",
    text: "text-emerald-300",
    badge: "bg-emerald-500/15 text-emerald-300",
  },
  yellow: {
    gradient: "from-amber-300 to-orange-500",
    tile: "bg-amber-400/15 text-amber-300 ring-1 ring-amber-300/30",
    hover: "hover:border-amber-300/60 hover:shadow-amber-400/20",
    text: "text-amber-300",
    badge: "bg-amber-400/15 text-amber-300",
  },
  rose: {
    gradient: "from-rose-400 to-red-600",
    tile: "bg-rose-500/15 text-rose-300 ring-1 ring-rose-400/30",
    hover: "hover:border-rose-400/60 hover:shadow-rose-500/20",
    text: "text-rose-300",
    badge: "bg-rose-500/15 text-rose-300",
  },
  violet: {
    gradient: "from-violet-400 to-purple-600",
    tile: "bg-violet-500/15 text-violet-300 ring-1 ring-violet-400/30",
    hover: "hover:border-violet-400/60 hover:shadow-violet-500/20",
    text: "text-violet-300",
    badge: "bg-violet-500/15 text-violet-300",
  },
  fuchsia: {
    gradient: "from-fuchsia-500 via-pink-500 to-orange-400",
    tile: "bg-fuchsia-500/15 text-fuchsia-300 ring-1 ring-fuchsia-400/30",
    hover: "hover:border-fuchsia-400/60 hover:shadow-fuchsia-500/20",
    text: "text-fuchsia-300",
    badge: "bg-fuchsia-500/15 text-fuchsia-300",
  },
  cyan: {
    gradient: "from-cyan-400 via-teal-500 to-emerald-500",
    tile: "bg-cyan-500/15 text-cyan-300 ring-1 ring-cyan-400/30",
    hover: "hover:border-cyan-400/60 hover:shadow-cyan-500/20",
    text: "text-cyan-300",
    badge: "bg-cyan-500/15 text-cyan-300",
  },
};

// which colour each tool category uses
export const CATEGORY_THEME = {
  organize: "blue",
  convert: "green",
  optimize: "yellow",
  security: "rose",
  edit: "violet",
};

export const themeForCategory = (categoryId) => THEMES[CATEGORY_THEME[categoryId] ?? "blue"];
