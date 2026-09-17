import React from "react";
import { cn } from "../../lib/utils";

export const GlowBadge = ({
  children,
  className,
  status = "active", // "active" | "warning" | "danger" | "idle"
}) => {
  const statusStyles = {
    active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    warning: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    danger: "bg-red-500/10 text-red-400 border-red-500/30",
    idle: "bg-neutral-800/40 text-neutral-400 border-neutral-700/40",
    cyan: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30",
  };

  const dotStyles = {
    active: "bg-emerald-400 shadow-[0_0_8px_#10B981]",
    warning: "bg-amber-400 shadow-[0_0_8px_#F59E0B]",
    danger: "bg-red-400 shadow-[0_0_8px_#EF4444]",
    idle: "bg-neutral-500",
    cyan: "bg-cyan-400 shadow-[0_0_8px_#00F2FE]",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium border tracking-wide",
        statusStyles[status] || statusStyles.active,
        className
      )}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full animate-pulse", dotStyles[status] || dotStyles.active)} />
      {children}
    </span>
  );
};
