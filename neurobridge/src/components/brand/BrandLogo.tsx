import Image from "next/image";
import { siteConfig } from "@/lib/data";

type BrandLogoProps = {
  variant?: "horizontal" | "mark" | "icon";
  className?: string;
  alt?: string;
  priority?: boolean;
};

const sources = {
  horizontal: {
    src: "/brand/neurobridge-logo-horizontal.png",
    width: 3200,
    height: 1024,
  },
  mark: {
    src: "/brand/neurobridge-mark.svg",
    width: 512,
    height: 512,
  },
  icon: {
    src: "/brand/neurobridge-app-icon.svg",
    width: 512,
    height: 512,
  },
} as const;

export function BrandLogo({
  variant = "horizontal",
  className,
  alt = siteConfig.name,
  priority = false,
}: BrandLogoProps) {
  const image = sources[variant];
  return (
    <Image
      src={image.src}
      alt={alt}
      width={image.width}
      height={image.height}
      priority={priority}
      unoptimized={image.src.endsWith(".svg")}
      className={className}
    />
  );
}
