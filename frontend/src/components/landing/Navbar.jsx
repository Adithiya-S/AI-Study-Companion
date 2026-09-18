import React from "react";
import { Terminal, ArrowRight } from "lucide-react";
import { MagneticButton } from "../ui/MagneticButton";

export const Navbar = ({ onOpenAuth, onOpenDashboard }) => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-neutral-800/80 bg-[#08090D]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
          <div className="relative w-8 h-8 rounded-lg bg-[#0E1118] border border-cyan-500/40 flex items-center justify-center shadow-[0_0_12px_rgba(0,242,254,0.2)] p-1.5">
            <img src="/favicon.svg" alt="AURA" className="w-full h-full object-contain" />
            <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          </div>
          <div>
            <div className="font-mono text-sm font-bold tracking-wider text-white flex items-center gap-2">
              AURA <span className="text-cyan-400">//</span> AI STUDY COMPANION
            </div>
            <div className="text-[10px] font-mono text-neutral-500 tracking-tight">AI VISION & TELEMETRY</div>
          </div>
        </div>

        {/* Center status */}
        <div className="hidden md:flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-neutral-800/80 bg-[#0C0F17] text-xs font-mono">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
          </span>
          <span className="text-neutral-400">VISION & AI:</span>
          <span className="text-cyan-400 font-semibold flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5" /> MEDIAPIPE + GEMINI 3.6 FLASH
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
