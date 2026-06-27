"use client";

import { Printer } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function PrintCapabilityButton() {
  return (
    <Button
      onClick={() => window.print()}
      size="md"
      className="print:hidden"
    >
      <Printer className="h-4 w-4" />
      Save as PDF
    </Button>
  );
}
