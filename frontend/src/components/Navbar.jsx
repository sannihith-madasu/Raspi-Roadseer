import { Link, useLocation } from "react-router-dom";
import { Map, BarChart3, FileText, Home, Radio } from "lucide-react";

const navItems = [
  { path: "/", label: "Home", icon: Home },
  { path: "/map", label: "Live Map", icon: Map },
  { path: "/dashboard", label: "Analytics", icon: BarChart3 },
  { path: "/reports", label: "Reports", icon: FileText },
];

export default function Navbar() {
  const location = useLocation();

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-orange-500/20">
            <Radio className="h-5 w-5 text-orange-400" />
          </div>
          <span className="text-lg font-bold">
            Raspi <span className="text-orange-400">Roadseer</span>
          </span>
        </Link>

        {/* Nav Links */}
        <div className="flex items-center gap-1">
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-orange-500/15 text-orange-400"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            );
          })}
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-2 rounded-full bg-slate-800 px-3 py-1.5">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500"></span>
          </span>
          <span className="text-xs text-slate-400">
            Mock Data
          </span>
        </div>
      </div>
    </nav>
  );
}