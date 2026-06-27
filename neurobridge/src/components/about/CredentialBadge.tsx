import { cn } from "@/lib/utils";

type Credential = {
  abbr: string;
  full: string;
};

export function CredentialBadge({
  credential,
  variant = "light",
}: {
  credential: Credential;
  variant?: "light" | "dark" | "document";
}) {
  const variants = {
    light:
      "border-navy-900/10 bg-white text-navy-900 shadow-sm hover:border-teal-500/30 hover:shadow-md",
    dark: "border-white/15 bg-white/5 text-white hover:bg-white/10",
    document:
      "border-navy-900/15 bg-surface-muted text-navy-900",
  };

  return (
    <div
      className={cn(
        "group relative rounded-xl border px-5 py-4 transition-all duration-300",
        variants[variant]
      )}
      title={credential.full}
    >
      <p className="font-display text-xl font-bold tracking-tight">
        {credential.abbr}
      </p>
      <p
        className={cn(
          "mt-1 text-[11px] leading-snug",
          variant === "dark" ? "text-white/55" : "text-navy-700/55"
        )}
      >
        {credential.full}
      </p>
    </div>
  );
}

export function CredentialBadgeRow({
  credentials,
  variant = "light",
}: {
  credentials: Credential[];
  variant?: "light" | "dark" | "document";
}) {
  return (
    <div className="flex flex-wrap gap-3">
      {credentials.map((cred) => (
        <CredentialBadge key={cred.abbr} credential={cred} variant={variant} />
      ))}
    </div>
  );
}
