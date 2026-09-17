import React from "react";
import { motion } from "framer-motion";
import { FileText, CheckCircle2, AlertTriangle, Scale, ArrowLeft, ShieldAlert } from "lucide-react";
import { BorderBeam } from "../ui/BorderBeam";

export const TermsOfService = ({ onBack }) => {
  return (
    <div className="min-h-screen bg-[#08090D] text-neutral-200 py-12 px-6 engineering-grid">
      <div className="max-w-4xl mx-auto">
        {/* Return Button */}
        <div className="mb-8">
          <button
            onClick={onBack}
            className="inline-flex items-center gap-2 text-xs font-mono text-neutral-400 hover:text-cyan-400 px-3.5 py-2 rounded-lg border border-neutral-800 bg-[#0C0E14] transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> RETURN TO WORKSPACE
          </button>
        </div>

        {/* Header */}
        <div className="relative rounded-2xl bg-[#0D1017] border border-[#1E2433] p-8 md:p-10 mb-10 overflow-hidden shadow-2xl">
          <BorderBeam size={250} duration={9} colorFrom="#00F2FE" colorTo="#3B82F6" />
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-950/20 text-cyan-400 text-xs font-mono mb-4">
            <FileText className="w-3.5 h-3.5" /> TERMS OF SERVICE & OPERATING AGREEMENT
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold font-sans text-white tracking-tight">
            Terms & Conditions of Service
          </h1>
          <p className="text-sm font-mono text-neutral-400 mt-2">
            LAST REVISED: September 2026 // AURA TELEMETRY PLATFORM CONTRACT // LEGAL VERSION 2.4
          </p>
        </div>

        {/* Sections */}
        <div className="space-y-8 text-neutral-300 leading-relaxed font-sans text-sm">
          {/* Section 1 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-cyan-400 flex items-center gap-2 mb-3">
              <CheckCircle2 className="w-4 h-4 text-cyan-400" /> 1. ACCEPTANCE OF TERMS
            </h2>
            <p className="text-neutral-300">
              By initializing an operator account, launching a study session, or deploying the AURA AI Study Companion interface, you agree to be bound by these Terms of Service. If you do not agree to these terms, you must discontinue use of the platform immediately.
            </p>
          </div>

          {/* Section 2 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-purple-400 flex items-center gap-2 mb-3">
              <Scale className="w-4 h-4 text-purple-400" /> 2. EDUCATIONAL INTENDED USE & ACADEMIC INTEGRITY
            </h2>
            <p className="mb-2">
              AURA is designed solely as a cognitive productivity booster, biometric posture/gaze telemetry gauge, and active-recall tutor.
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-neutral-400 text-xs font-mono">
              <li>Users agree not to use the Gemini AI engine for academic dishonesty, plagiarism, or unauthorized exam assistance.</li>
              <li>Users are responsible for ensuring that study materials uploaded comply with copyright and institutional confidentiality policies.</li>
              <li>AURA does not guarantee specific exam outcomes or academic performance metrics.</li>
            </ul>
          </div>

          {/* Section 3 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-amber-400 flex items-center gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-amber-400" /> 3. AI-GENERATED CONTENT DISCLAIMER
            </h2>
            <p className="mb-2">
              The AI Study Studio utilizes large language models (Google Gemini). While tuned with high-accuracy study instructions:
            </p>
            <p className="text-xs text-neutral-400 font-mono">
              AI outputs, summaries, and flashcards may occasionally contain inaccuracies, hallucinations, or simplified models. Operators must cross-examine critical scientific, mathematical, or medical facts against certified reference textbooks.
            </p>
          </div>

          {/* Section 4 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-emerald-400 flex items-center gap-2 mb-3">
              <ShieldAlert className="w-4 h-4 text-emerald-400" /> 4. ACCEPTABLE USE & PLATFORM INTEGRITY
            </h2>
            <p className="mb-2">You agree not to:</p>
            <ul className="list-disc pl-5 space-y-1 text-neutral-400 text-xs font-mono">
              <li>Automate unauthorized high-frequency requests, API scraping, or denial-of-service attempts against study endpoints.</li>
              <li>Attempt to reverse-engineer, inject hostile payloads, or exploit computer vision telemetry hooks.</li>
              <li>Upload malicious executables or non-educational binaries disguised as study documents.</li>
            </ul>
          </div>

          {/* Section 5 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-white flex items-center gap-2 mb-3">
              <Scale className="w-4 h-4 text-cyan-400" /> 5. LIMITATION OF LIABILITY
            </h2>
            <p className="text-xs font-mono text-neutral-400">
              AURA is provided on an "AS IS" and "AS AVAILABLE" basis. To the maximum extent permitted by applicable law, the maintainers and developers shall not be held liable for any indirect, incidental, special, or consequential damages resulting from platform downtime, camera hardware incompatibilities, or data loss.
            </p>
          </div>
        </div>

        {/* Footer Return */}
        <div className="mt-12 text-center">
          <button
            onClick={onBack}
            className="px-6 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-semibold text-xs transition-colors"
          >
            I UNDERSTAND & RETURN
          </button>
        </div>
      </div>
    </div>
  );
};
