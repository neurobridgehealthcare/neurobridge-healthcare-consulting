import { ArrowRight, ArrowUpRight } from "lucide-react";
import { getProductCta, products, productsNote, type Product } from "@/lib/products";
import { Button } from "@/components/ui/Button";

function ProductCard({ product }: { product: Product }) {
  const cta = getProductCta(product);
  const Icon = product.icon;

  return (
    <article
      id={product.id}
      className="group flex h-full scroll-mt-28 flex-col rounded-2xl border border-navy-900/5 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-teal-500/20 hover:shadow-lg hover:shadow-teal-500/5 sm:p-7"
    >
      <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/10 to-teal-500/10 text-teal-600 transition-colors group-hover:from-blue-500 group-hover:to-teal-500 group-hover:text-white">
        <Icon className="h-5 w-5" aria-hidden />
      </div>
      <h3 className="font-display text-xl font-bold text-navy-900">
        {product.name}
      </h3>
      <p className="mt-2 text-lg font-semibold tracking-tight text-teal-700">
        {product.price}
      </p>
      <p className="mt-4 flex-1 text-sm leading-relaxed text-navy-700/75">
        {product.description}
      </p>
      <div className="mt-6">
        <Button href={cta.href} external={cta.external} className="w-full sm:w-auto">
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

export function ProductOfferings() {
  return (
    <div>
      <div className="grid gap-6 md:grid-cols-2">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
      <p className="mx-auto mt-8 max-w-3xl text-center text-sm leading-relaxed text-navy-700/60">
        {productsNote}
      </p>
    </div>
  );
}
