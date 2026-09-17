import React, { useRef } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";
import { cn } from "../../lib/utils";

export const MagneticButton = ({
  children,
  className,
  onClick,
  variant = "primary", // "primary" | "secondary" | "danger" | "ghost"
  ...props
}) => {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const springX = useSpring(x, { stiffness: 250, damping: 20 });
  const springY = useSpring(y, { stiffness: 250, damping: 20 });

  const handleMouseMove = (e) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    x.set((e.clientX - centerX) * 0.25);
    y.set((e.clientY - centerY) * 0.25);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  const variantStyles = {
    primary:
      "bg-cyan-500 text-black font-semibold hover:bg-cyan-400 active:scale-95 shadow-[0_0_20px_rgba(0,242,254,0.25)] border border-cyan-400/50",
    secondary:
      "bg-[#121622] text-neutral-200 hover:text-white hover:bg-[#181E2E] border border-neutral-800 hover:border-neutral-700 active:scale-95",
    danger:
      "bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30 hover:border-red-500/60 active:scale-95",
    ghost:
      "bg-transparent text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/40 border border-transparent",
  };

  return (
    <motion.button
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      style={{ x: springX, y: springY }}
      className={cn(
        "relative inline-flex items-center justify-center px-5 py-2.5 rounded-lg text-sm transition-colors duration-150 select-none cursor-pointer",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </motion.button>
  );
};
