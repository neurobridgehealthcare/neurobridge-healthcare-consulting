import type { MetadataRoute } from "next";
import { siteConfig } from "@/lib/data";

const routes = [
  "",
  "/services",
  "/solutions",
  "/about",
  "/capability-statement",
  "/ventures",
  "/contact",
];

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date();
  return routes.map((path) => ({
    url: `${siteConfig.url}${path}`,
    lastModified,
    changeFrequency: path === "" ? "weekly" : "monthly",
    priority: path === "" ? 1 : 0.7,
  }));
}
