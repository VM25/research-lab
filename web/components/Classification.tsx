"use client";

import { clsClass } from "@/lib/format";

/* Formal classification marker — fill pattern + word, never colour.
   filled square = Survived, half square = Conditional, hollow = Rejected. */
export default function Classification({ verdict, size }: { verdict: string; size?: "sm" | "md" }) {
  return (
    <span className={`cls ${clsClass(verdict)}`}>
      <span className="cls-mark" aria-hidden="true" />
      <span className="cls-name" style={size === "md" ? { fontSize: "12.5px" } : undefined}>{verdict}</span>
    </span>
  );
}
