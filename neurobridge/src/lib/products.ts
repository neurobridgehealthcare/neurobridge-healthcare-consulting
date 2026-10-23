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
    id: "tms-feasibility",
    name: "TMS Feasibility Assessment",
    price: "$1,500–$3,000",
    interest: "TMS Feasibility Assessment",
    inquiryCtaLabel: "Request this assessment",
    checkoutCtaLabel: "Purchase this assessment",
    icon: Brain,
    description:
      "Thinking about adding TMS therapy to your practice? Before you sign an equipment lease, find out whether the numbers work. We look at your patient base, payer mix, space, staffing and local competition, then give you a clear written report with projected volume, revenue, startup costs and break-even timeline. You’ll come away with a go or no-go recommendation and a step-by-step launch plan if it makes sense.",
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
      "For hospitals, surgery centers and surgeon groups deciding how to handle intraoperative neuromonitoring. We compare building an in-house program with outsourcing, covering case volume, staffing, equipment, credentialing, billing and risk. Delivered by a certified neuromonitoring professional (CNIM, R. EP T.) with hands-on experience at major hospital systems, the report shows what each option would cost, what it could earn, and which one fits your organization.",
  },
  {
    id: "strategy-call",
    name: "60-Minute Strategy Call",
    price: "$250–$400",
    interest: "60-Minute Strategy Call",
    inquiryCtaLabel: "Request this call",
    checkoutCtaLabel: "Book this call",
    icon: Phone,
    description:
      "Not sure where to start? Book a one-on-one call to talk through your TMS or neuromonitoring questions with someone who’s done the work. Bring your situation and we’ll cover what’s realistic, what it would take, and what to watch out for. If you go on to book a full feasibility assessment within 30 days, the cost of the call is credited toward it.",
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
      "A ready-to-use spreadsheet that shows whether TMS would pay off at your practice. Enter your expected patients, reimbursement rates, equipment and staffing costs, and it calculates monthly revenue, profit and your break-even point. It includes instructions and example scenarios, and you can download it right after purchase.",
  },
];

export const productInterests = products.map((product) => product.interest);

export const productsNote =
  "Prices are published ranges. The fee inside that range is confirmed before work starts. TMS planning draws on experience preparing a clinic launch; that clinic did not open, and these offerings are not a claim of having operated one. NeuroBridge does not diagnose patients or provide physician oversight.";

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
