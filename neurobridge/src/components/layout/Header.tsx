"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import { navigation } from "@/lib/data";
import { BrandLogo } from "@/components/brand/BrandLogo";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

export function Header() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  return (
    <header
      className={cn(
        "site-header fixed inset-x-0 top-0 z-50 transition-all duration-300",
        scrolled
          ? "glass shadow-sm shadow-navy-900/5"
          : "bg-transparent"
      )}
    >
      <div className="container-custom">
        <div className="flex min-h-[4.5rem] items-center justify-between py-4 lg:min-h-20">
          <Link href="/" className="flex shrink-0 items-center">
            <BrandLogo
              priority
              className="h-10 w-auto max-w-[11.5rem] sm:h-12 sm:max-w-none"
            />
          </Link>

          <nav className="hidden items-center gap-1 lg:flex" aria-label="Main">
            {navigation.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              const isCta = item.href === "/contact";

              if (isCta) return null;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "rounded-full px-4 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-navy-900/5 text-navy-900"
                      : "text-navy-700/80 hover:text-navy-900"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
            <Button href="/contact" size="sm" className="ml-3">
              Contact
            </Button>
          </nav>

          <button
            type="button"
            className="inline-flex items-center justify-center rounded-xl p-2 text-navy-900 lg:hidden"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="border-t border-navy-900/5 bg-white/95 backdrop-blur-xl lg:hidden">
          <nav className="container-custom flex flex-col gap-1 py-4" aria-label="Mobile">
            {navigation.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "rounded-xl px-4 py-3 text-base font-medium transition-colors",
                    isActive
                      ? "bg-navy-900/5 text-navy-900"
                      : "text-navy-700 hover:bg-navy-900/5"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      )}
    </header>
  );
}
