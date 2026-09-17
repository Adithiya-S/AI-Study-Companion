import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldCheck, Cookie, X, ArrowUpRight } from "lucide-react";

export const CookieConsentBanner = ({ onOpenPrivacy }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem("aura_cookie_consent");
    if (!consent) {
      // Delay display slightly for smooth page entry
      const timer = setTimeout(() => setIsVisible(true), 1200);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAccept = (type) => {
    localStorage.setItem("aura_cookie_consent", JSON.stringify({ type, timestamp: new Date().toISOString() }));
    setIsVisible(false);
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
          className="fixed bottom-4 left-4 right-4 md:left-auto md:right-6 md:max-w-md z-50"
        >
          <div className="p-4 rounded-xl bg-[#0D1017]/95 border border-[#1E2433] backdrop-blur-md shadow-[0_10px_35px_rgba(0,0,0,0.8)]">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#141924] border border-cyan-500/30 flex items-center justify-center shrink-0 mt-0.5">
                <Cookie className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-mono font-bold text-white flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> LOCAL TELEMETRY & STORAGE
                  </h4>
                  <button
                    onClick={() => handleAccept("essential")}
                    className="text-neutral-500 hover:text-neutral-300 p-0.5"
                    title="Dismiss"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
                <p className="text-[11px] text-neutral-400 leading-relaxed font-sans">
                  We use essential local storage for authenticated operator tokens and focus telemetry. We reject invasive third-party ad trackers.
                </p>
                <div className="flex items-center gap-2 pt-2">
                  <button
                    onClick={() => handleAccept("all")}
                    className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-semibold text-[10px] transition-colors"
                  >
                    ACCEPT ALL
                  </button>
                  <button
                    onClick={() => handleAccept("essential")}
                    className="px-3 py-1.5 rounded-lg bg-[#141A26] hover:bg-[#1C2436] text-neutral-300 border border-neutral-700 font-mono text-[10px] transition-colors"
                  >
                    ESSENTIAL ONLY
                  </button>
                  <button
                    onClick={onOpenPrivacy}
                    className="text-[10px] font-mono text-cyan-400 hover:underline flex items-center gap-0.5 ml-auto"
                  >
                    PRIVACY CHARTER <ArrowUpRight className="w-2.5 h-2.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
