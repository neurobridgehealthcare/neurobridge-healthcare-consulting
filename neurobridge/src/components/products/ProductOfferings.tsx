import { ArrowRight, ArrowUpRight } from "lucide-react";
import { getProductCta, type Product } from "@/lib/products";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

function ProductCard({
  product,
  compact = false,
}: {
  product: Product;
  compact?: boolean;
}) {
  const cta = getProductCta(product);
  const Icon = product.icon;

  return (
    <article
      id={product.id}
      className={cn(
        "group flex h-full scroll-mt-28 flex-col rounded-2xl border border-navy-900/5 bg-white shadow-sm",
        compact ? "p-5" : "p-6 sm:p-7"
      )}
    >
      <div
        className={cn(
          "inline-flex items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/10 to-teal-500/10 text-teal-600",
          compact ? "mb-3 h-9 w-9" : "mb-5 h-12 w-12"
        )}
      >
        <Icon className={compact ? "h-4 w-4" : "h-5 w-5"} aria-hidden />
      </div>
      <h3
        className={cn(
          "font-display font-bold text-navy-900",
          compact ? "text-lg" : "text-xl"
        )}
      >
        {product.name}
      </h3>
      <p
        className={cn(
          "mt-1 font-semibold tracking-tight text-teal-700",
          compact ? "text-base" : "text-lg"
        )}
      >
        {product.price}
      </p>
      <p className="mt-3 flex-1 text-sm leading-relaxed text-navy-700/75">
        {product.description}
      </p>
      <div className={compact ? "mt-4" : "mt-6"}>
        <Button
          href={cta.href}
          external={cta.external}
          size={compact ? "sm" : "md"}
          className="w-full sm:w-auto"
        >
          {cta.label}
          {cta.external ? (
            <ArrowUpRight className="h-4 w-4" aria-hidden />
          ) : (
            <ArrowRight className="h-4 w-4" aria-hidden />
          )}
        </Button>
      </div>
    </article>
  );
}

export function StrategyCallCard({ product }: { product: Product }) {
  const cta = getProductCta(product);

  return (
    <article
      id={product.id}
      className="scroll-mt-28 rounded-2xl border border-teal-500/25 bg-navy-900 p-6 text-white sm:p-8"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-400">
        Start here
      </p>
      <div className="mt-3 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div className="max-w-2xl">
          <h3 className="font-display text-2xl font-bold">{product.name}</h3>
          <p className="mt-1 text-lg font-semibold text-teal-300">{product.price}</p>
          <p className="mt-3 text-sm leading-relaxed text-white/75">
            {product.description}
          </p>
        </div>
        <Button href={cta.href} external={cta.external} className="shrink-0">
          {cta.label}
          {cta.external ? (
            <ArrowUpRight className="h-4 w-4" aria-hidden />
          ) : (
            <ArrowRight className="h-4 w-4" aria-hidden />
          )}
        </Button>
      </div>
    </article>
  );
}

export function ProductGrid({
  products,
  compact = false,
}: {
  products: Product[];
  compact?: boolean;
}) {
  return (
    <div className={cn("grid gap-4", compact ? "md:grid-cols-2" : "gap-6")}>
      {products.map((product) => (
        <ProductCard key={product.id} product={product} compact={compact} />
      ))}
    </div>
  );
}
