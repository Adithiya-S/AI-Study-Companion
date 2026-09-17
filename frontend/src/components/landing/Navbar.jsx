import React from "react";
import { Eye, Shield, Terminal, ArrowRight } from "lucide-react";
import { MagneticButton } from "../ui/MagneticButton";
import { GlowBadge } from "../ui/GlowBadge";

export const Navbar = ({ onOpenAuth, onOpenDashboard }) => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-neutral-800/80 bg-[#08090D]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
          <div className="relative w-8 h-8 rounded-lg bg-[#0E1118] border border-cyan-500/40 flex items-center justify-center shadow-[0_0_12px_rgba(0,242,254,0.2)]">
            <Eye className="w-4 h-4 text-cyan-400" />
            <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          </div>
          <div>
            <div className="font-mono text-sm font-bold tracking-wider text-white flex items-center gap-2">
              AURA <span className="text-cyan-400">//</span> OS
            </div>
            <div className="text-[10px] font-mono text-neutral-500 tracking-tight">AI VISION & TELEMETRY</div>
          </div>
        </div>

        {/* Center status */}
        <div className="hidden md:flex items-center gap-4">
          <GlowBadge status="active">TELEMETRY ENGINE v2.4</GlowBadge>
          <span className="text-neutral-600 font-mono text-xs">|</span>
          <span className="text-neutral-400 font-mono text-xs flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-neutral-500" /> MEDIAPIPE + GEMINI 2.5
          </span>
        </div>

        {/* Right CTA */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenAuth}
            className="text-xs font-mono text-neutral-400 hover:text-white px-3 py-1.5 transition-colors"
          >
            SIGN IN
          </button>
          <MagneticButton
            variant="primary"
            onClick={onOpenDashboard}
            className="text-xs font-mono px-4 py-2 flex items-center gap-1.5"
          >
            LAUNCH APP <ArrowRight className="w-3.5 h-3.5" />
          </MagneticButton>
        </div>
      </div>
    </header>
  );
};
