import Link from "next/link";
import { cn } from "@/lib/utils";

type ButtonProps = {
  href?: string;
  /** Open http(s) links in a new tab. Ignored for in-site paths. */
  external?: boolean;
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  className?: string;
  children: React.ReactNode;
  type?: "button" | "submit";
  onClick?: () => void;
};

const variants = {
  primary:
    "bg-gradient-to-r from-blue-500 to-teal-500 text-white shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 hover:brightness-110",
  secondary:
    "bg-navy-900 text-white hover:bg-navy-800 shadow-lg shadow-navy-900/20",
  outline:
    "border-2 border-navy-900/15 text-navy-900 hover:border-teal-500/50 hover:bg-teal-500/5",
  ghost: "text-navy-700 hover:text-teal-500 hover:bg-teal-500/5",
};

const sizes = {
  sm: "px-4 py-2 text-sm",
  md: "px-6 py-3 text-sm",
  lg: "px-8 py-4 text-base",
};

export function Button({
  href,
  external = false,
  variant = "primary",
  size = "md",
  className,
  children,
  type = "button",
  onClick,
}: ButtonProps) {
  const classes = cn(
    "inline-flex items-center justify-center gap-2 rounded-full font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2",
    variants[variant],
    sizes[size],
    className
  );

  if (href) {
    const isExternal =
      external || href.startsWith("https://") || href.startsWith("http://");
    if (isExternal) {
      return (
        <a
          href={href}
          className={classes}
          target="_blank"
          rel="noopener noreferrer"
        >
          {children}
        </a>
      );
    }
    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button type={type} className={classes} onClick={onClick}>
      {children}
    </button>
  );
}
