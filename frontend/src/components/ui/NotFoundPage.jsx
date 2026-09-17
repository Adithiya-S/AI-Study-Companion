import React from "react";
import { motion } from "framer-motion";
import { AlertCircle, EyeOff, Home, ArrowLeft, Terminal, ShieldAlert } from "lucide-react";
import { BorderBeam } from "./BorderBeam";
import { MagneticButton } from "./MagneticButton";

export const NotFoundPage = ({ onBackToLanding, onOpenDashboard }) => {
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6 relative bg-[#08090D] engineering-grid">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-lg text-center"
      >
        <div className="relative rounded-2xl bg-[#0D1017] border border-[#232B3D] p-8 md:p-10 shadow-[0_0_50px_rgba(0,0,0,0.8)] overflow-hidden">
          <BorderBeam size={260} duration={8} colorFrom="#EF4444" colorTo="#00F2FE" />

          {/* Icon HUD */}
          <div className="inline-flex w-16 h-16 rounded-2xl bg-[#151822] border border-red-500/40 items-center justify-center mb-6 shadow-[0_0_25px_rgba(239,68,68,0.25)]">
            <EyeOff className="w-8 h-8 text-red-400" />
          </div>

          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-red-500/30 bg-red-950/20 text-red-400 text-xs font-mono mb-4">
            <ShieldAlert className="w-3.5 h-3.5" /> ERROR CODE: 404_TELEMETRY_DISCONNECTED
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold font-mono text-white tracking-tight mb-3">
            COORDINATES <span className="text-red-400">LOST</span>
          </h1>

          <p className="text-sm font-mono text-neutral-400 max-w-md mx-auto leading-relaxed mb-8">
            The telemetry vector or study node you attempted to access does not exist or has been relocated to an unmapped workspace.
          </p>

          <div className="p-3.5 rounded-xl bg-[#07090E] border border-neutral-800 text-left font-mono text-xs text-neutral-400 mb-8 space-y-1">
            <div className="text-neutral-500">// DIAGNOSTIC TRACE</div>
            <div className="text-red-400/90">&gt; STATUS: HTTP_404_NOT_FOUND</div>
            <div className="text-neutral-300">&gt; REQUEST_URI: {window.location.pathname || "/unknown"}</div>
            <div className="text-cyan-400/80">&gt; SUGGESTION: RETURN TO CENTRAL COMMAND</div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <MagneticButton
              variant="primary"
              onClick={onBackToLanding}
              className="w-full sm:w-auto text-xs font-mono px-5 py-3 flex items-center justify-center gap-2"
            >
              <Home className="w-3.5 h-3.5" /> RETURN TO LANDING
            </MagneticButton>
            {onOpenDashboard && (
              <MagneticButton
                variant="secondary"
                onClick={onOpenDashboard}
                className="w-full sm:w-auto text-xs font-mono px-5 py-3 flex items-center justify-center gap-2"
              >
                <Terminal className="w-3.5 h-3.5" /> LAUNCH DASHBOARD
              </MagneticButton>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
};
