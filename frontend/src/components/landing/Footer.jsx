import React from "react";
import { Eye, Shield, FileText, ArrowUpRight } from "lucide-react";

export const Footer = ({ onOpenAuth, onOpenDashboard, onOpenPrivacy, onOpenTerms }) => {
  return (
    <footer className="border-t border-neutral-800/80 bg-[#06070B] py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-[#0D1017] border border-neutral-800 flex items-center justify-center">
            <Eye className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <span className="font-mono text-xs text-neutral-400">
            AURA TELEMETRY // AI STUDY COMPANION &copy; {new Date().getFullYear()}
          </span>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-6 font-mono text-xs text-neutral-500">
          <button onClick={onOpenDashboard} className="hover:text-cyan-400 transition-colors cursor-pointer">
            DASHBOARD
          </button>
          <button onClick={onOpenAuth} className="hover:text-cyan-400 transition-colors cursor-pointer">
            SIGN IN
          </button>
          <button onClick={onOpenPrivacy} className="hover:text-cyan-400 transition-colors flex items-center gap-1 cursor-pointer">
            <Shield className="w-3 h-3 text-neutral-600" /> PRIVACY POLICY
          </button>
          <button onClick={onOpenTerms} className="hover:text-cyan-400 transition-colors flex items-center gap-1 cursor-pointer">
            <FileText className="w-3 h-3 text-neutral-600" /> TERMS OF SERVICE
          </button>
          <a
            href="https://www.npmjs.com/package/@driftcli/drift"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-cyan-400 transition-colors flex items-center gap-1"
          >
            DRIFT_CLI <ArrowUpRight className="w-3 h-3" />
          </a>
        </div>
      </div>
    </footer>
  );
};
