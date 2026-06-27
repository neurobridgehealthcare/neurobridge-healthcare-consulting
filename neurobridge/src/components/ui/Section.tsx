import { cn } from "@/lib/utils";

export function Container({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <div className={cn("container-custom", className)}>{children}</div>;
}

export function Section({
  children,
  className,
  id,
  dark = false,
}: {
  children: React.ReactNode;
  className?: string;
  id?: string;
  dark?: boolean;
}) {
  return (
    <section
      id={id}
      className={cn(
        "section-padding",
        dark ? "bg-navy-900 text-white" : "",
        className
      )}
    >
      {children}
    </section>
  );
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  align = "center",
  light = false,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "left" | "center";
  light?: boolean;
}) {
  return (
    <div
      className={cn(
        "mb-14 md:mb-16",
        align === "center" ? "mx-auto max-w-3xl text-center" : "max-w-2xl"
      )}
    >
      {eyebrow && (
        <p
          className={cn(
            "section-eyebrow mb-3",
            light ? "text-teal-400" : "text-teal-500"
          )}
        >
          {eyebrow}
        </p>
      )}
      <h2
        className={cn(
          "font-display text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl",
          light ? "text-white" : "text-navy-900"
        )}
      >
        {title}
      </h2>
      {description && (
        <p
          className={cn(
            "mt-5 text-lg leading-relaxed",
            light ? "text-white/70" : "text-navy-700/70"
          )}
        >
          {description}
        </p>
      )}
    </div>
  );
}
