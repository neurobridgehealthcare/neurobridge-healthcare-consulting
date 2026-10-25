import type { LucideIcon } from "lucide-react";
import { Brain, Calculator, Hospital, Phone } from "lucide-react";

/**
 * Paid offerings.
 *
 * There is no payment provider in this project yet. Leave `checkoutUrl`
 * unset and each call to action opens the contact form with this product
 * selected. To turn on live checkout later, set `checkoutUrl` to that
 * product's Stripe Payment Link (or other hosted checkout URL). Use the
 * public link only. Do not put Stripe secret keys in this file.
 */
export type Product = {
  id: string;
  name: string;
  price: string;
  description: string;
  interest: string;
  inquiryCtaLabel: string;
  /** Label used when `checkoutUrl` is set. */
  checkoutCtaLabel?: string;
  /**
   * Stripe Payment Link or other hosted checkout URL.
   * Omit until a real payment link exists.
   */
  checkoutUrl?: string;
  icon: LucideIcon;
};

export const products: Product[] = [
  {
    id: "strategy-call",
    name: "60-Minute Strategy Call",
    price: "$250–$400",
    interest: "60-Minute Strategy Call",
    inquiryCtaLabel: "Request this call",
    checkoutCtaLabel: "Book this call",
    icon: Phone,
    description:
      "The place to start, for an IONM or TMS question. Bring your situation. You’ll cover what is realistic, what it would take, and what to watch. Book a feasibility assessment within 30 days and the call is credited toward it.",
  },
  {
    id: "ionm-feasibility",
    name: "IONM Program Feasibility Assessment",
    price: "$1,500–$3,000",
    interest: "IONM Program Feasibility Assessment",
    inquiryCtaLabel: "Request this assessment",
    checkoutCtaLabel: "Purchase this assessment",
    icon: Hospital,
    description:
      "For hospitals, surgery centers, and surgeon groups choosing in-house neuromonitoring or an outside service. The written report covers volume, staffing, equipment, credentialing, billing, and risk, and recommends which option fits. From a CNIM, R. EP T.",
  },
  {
    id: "tms-feasibility",
    name: "TMS Feasibility Assessment",
    price: "$1,500–$3,000",
    interest: "TMS Feasibility Assessment",
    inquiryCtaLabel: "Request this assessment",
    checkoutCtaLabel: "Purchase this assessment",
    icon: Brain,
    description:
      "Before you lease TMS equipment, see whether the numbers work: patients, payers, space, staffing, and local competition. You get a written go or no-go, and a launch outline if it makes sense.",
  },
  {
    id: "tms-roi-calculator",
    name: "TMS Startup ROI Calculator",
    price: "$99–$199",
    interest: "TMS Startup ROI Calculator",
    inquiryCtaLabel: "Request the calculator",
    checkoutCtaLabel: "Buy the calculator",
    icon: Calculator,
    description:
      "A spreadsheet for expected patients, reimbursement, equipment, and staffing. It returns monthly revenue, profit, and break-even, with instructions and examples. Download follows purchase.",
  },
];

export const productInterests = products.map((product) => product.interest);

export const strategyCall = products[0];
export const ionmProducts = [products[1]];
export const tmsProducts = products.filter((product) => product.id.startsWith("tms"));

export const productsNote =
  "Prices are published ranges. The fee is confirmed in writing before work starts. Not diagnosis or physician oversight.";

/** Not a priced offer. No availability date and no claim that coverage is provided today. */
export const ionmCoverageNote =
  "Technologist coverage in the operating room is not offered yet. That service is in development. No price is listed.";

export function productByInterest(interest: string): Product | undefined {
  return products.find((product) => product.interest === interest);
}

export type ProductCta = {
  href: string;
  label: string;
  external: boolean;
};

function hostedCheckoutUrl(value: string | undefined): string | undefined {
  if (!value) return undefined;
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  try {
    const parsed = new URL(trimmed);
    if (parsed.protocol !== "https:" && parsed.protocol !== "http:") {
      return undefined;
    }
    return trimmed;
  } catch {
    return undefined;
  }
}

/** Contact inquiry until `checkoutUrl` is a real http(s) checkout link. */
export function getProductCta(product: Product): ProductCta {
  const checkout = hostedCheckoutUrl(product.checkoutUrl);
  if (checkout) {
    return {
      href: checkout,
      label: product.checkoutCtaLabel ?? "Continue to checkout",
      external: true,
    };
  }
  return {
    href: `/contact?interest=${encodeURIComponent(product.interest)}`,
    label: product.inquiryCtaLabel,
    external: false,
  };
}
