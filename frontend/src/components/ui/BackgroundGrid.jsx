import React from "react";
import { cn } from "../../lib/utils";

export const BackgroundGrid = ({
  children,
  className,
  variant = "dots", // "dots" | "crosshair"
  glowColor = "rgba(0, 242, 254, 0.05)",
}) => {
  return (
    <div
      className={cn(
        "relative w-full min-h-screen bg-[#08090D] overflow-hidden",
        variant === "dots" ? "engineering-grid" : "engineering-crosshair",
        className
      )}
    >
      {/* Ambient center laser illumination (minimalist, zero frosted glass) */}
      <div
        className="pointer-events-none absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 rounded-full blur-[140px] w-[700px] h-[400px]"
        style={{ background: glowColor }}
      />
      {children}
    </div>
  );
};
