"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  UserPlus,
  MessageSquare,
  Calendar,
  GitBranch,
  FileText,
  Activity,
  Shield,
} from "lucide-react";
import { APP_NAME, APP_TAGLINE } from "@/lib/constants";

const navItems = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/leads", label: "Leads", icon: Users },
  { href: "/leads/new", label: "Add Lead", icon: UserPlus },
  { href: "/messages", label: "Messages", icon: MessageSquare },
  { href: "/calendar", label: "Content Calendar", icon: Calendar },
  { href: "/pipeline", label: "Pipeline", icon: GitBranch },
  { href: "/documents", label: "Documents", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-white/8 bg-navy-900/95">
      <div className="border-b border-white/8 px-5 py-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-teal-500">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="font-display text-sm font-semibold text-white">{APP_NAME}</p>
            <p className="text-[10px] uppercase tracking-wider text-slate-500">NeuroBridge</p>
          </div>
        </div>
        <p className="mt-3 text-xs leading-relaxed text-slate-500">{APP_TAGLINE}</p>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto p-3 scrollbar-thin">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active =
            href === "/"
              ? pathname === "/"
              : pathname === href || pathname.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
                active
                  ? "bg-teal-500/15 text-teal-400"
                  : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
              }`}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/8 p-4">
        <div className="flex items-start gap-2 rounded-lg bg-navy-800/50 p-3">
          <Shield className="mt-0.5 h-4 w-4 shrink-0 text-teal-400" />
          <p className="text-[11px] leading-relaxed text-slate-500">
            Manual outreach only. No LinkedIn automation or scraping.
          </p>
        </div>
      </div>
    </aside>
  );
}

export function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-navy-950">
      <Sidebar />
      <main className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="mx-auto max-w-7xl px-6 py-8">{children}</div>
      </main>
    </div>
  );
}
