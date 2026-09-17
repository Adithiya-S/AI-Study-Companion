import React from "react";
import { motion } from "framer-motion";
import { Shield, Eye, Lock, Database, ArrowLeft, Cpu, HardDrive, Bell } from "lucide-react";
import { BorderBeam } from "../ui/BorderBeam";

export const PrivacyPolicy = ({ onBack }) => {
  return (
    <div className="min-h-screen bg-[#08090D] text-neutral-200 py-12 px-6 engineering-grid">
      <div className="max-w-4xl mx-auto">
        {/* Navigation / Return */}
        <div className="mb-8">
          <button
            onClick={onBack}
            className="inline-flex items-center gap-2 text-xs font-mono text-neutral-400 hover:text-cyan-400 px-3.5 py-2 rounded-lg border border-neutral-800 bg-[#0C0E14] transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> RETURN TO WORKSPACE
          </button>
        </div>

        {/* Header Container */}
        <div className="relative rounded-2xl bg-[#0D1017] border border-[#1E2433] p-8 md:p-10 mb-10 overflow-hidden shadow-2xl">
          <BorderBeam size={250} duration={9} colorFrom="#00F2FE" colorTo="#10B981" />
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-950/20 text-cyan-400 text-xs font-mono mb-4">
            <Shield className="w-3.5 h-3.5" /> PRIVACY & TELEMETRY CHARTER
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold font-sans text-white tracking-tight">
            Privacy Policy & Biometric Protection
          </h1>
          <p className="text-sm font-mono text-neutral-400 mt-2">
            EFFECTIVE DATE: September 2026 // SYSTEM PROTOCOL v2.4 // ZERO-KNOWLEDGE CAMERA ARCHITECTURE
          </p>
        </div>

        {/* Content Sections */}
        <div className="space-y-8 text-neutral-300 leading-relaxed font-sans text-sm">
          {/* Section 1 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-cyan-400 flex items-center gap-2 mb-3">
              <Eye className="w-4 h-4 text-cyan-400" /> 1. LOCAL BIOMETRIC DATA & CAMERA PROCESSING
            </h2>
            <p className="mb-3 text-neutral-300">
              AURA employs in-browser computer vision (powered by Google MediaPipe and OpenCV WebAssembly) to detect eye aspect ratios (EAR), gaze vectors, and physical smartphone distractions in real time.
            </p>
            <div className="p-4 rounded-lg bg-[#07090E] border border-emerald-500/20 text-emerald-400/90 text-xs font-mono space-y-1">
              <div>✔ ZERO VIDEO TRANSMISSION: Live camera frames never leave your local computer memory.</div>
              <div>✔ ZERO FACIAL RECORDINGS: Video feeds are processed strictly frame-by-frame in client-side RAM and instantly discarded.</div>
              <div>✔ ZERO FACIAL RECOGNITION: The platform does not identify human identity, demographic characteristics, or retain biometric face templates.</div>
            </div>
          </div>

          {/* Section 2 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-purple-400 flex items-center gap-2 mb-3">
              <Database className="w-4 h-4 text-purple-400" /> 2. STORED STUDY TELEMETRY
            </h2>
            <p className="mb-3">
              To deliver focus charts, streak analytics, and Pomodoro efficiency logs, we record only aggregated mathematical telemetry:
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-neutral-400 text-xs font-mono">
              <li>Study session duration (minutes started, ended, paused).</li>
              <li>Distraction counts and anonymized timestamps (e.g. "Looking away detected at 14:22").</li>
              <li>Calculated aggregate Focus Score index (50.0 - 100.0).</li>
              <li>Account profile records: Name, email address, and hashed authentication credentials.</li>
            </ul>
          </div>

          {/* Section 3 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-cyan-400 flex items-center gap-2 mb-3">
              <Cpu className="w-4 h-4 text-cyan-400" /> 3. GOOGLE GEMINI AI TUTOR & DOCUMENT INGESTION
            </h2>
            <p className="mb-2">
              When using the AI Study Studio, text prompts and study notes uploaded for Q&A or flashcard synthesis are securely processed via the official Google Gemini API (model: <code className="text-cyan-300 bg-neutral-900 px-1 py-0.5 rounded">gemini-3.5-flash</code>).
            </p>
            <p className="text-xs text-neutral-400 font-mono">
              We do not sell, rent, or lease your educational notes or AI prompts to third-party ad brokers. Data is processed strictly to provide dynamic explanations, flashcard flips, and active-recall tests.
            </p>
          </div>

          {/* Section 4 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-emerald-400 flex items-center gap-2 mb-3">
              <HardDrive className="w-4 h-4 text-emerald-400" /> 4. COOKIES & LOCAL STORAGE
            </h2>
            <p className="mb-2">
              AURA rejects invasive third-party tracking scripts. We utilize standard browser <code className="text-neutral-200">localStorage</code> and session tokens exclusively for:
            </p>
            <ul className="list-disc pl-5 space-y-1 text-neutral-400 text-xs font-mono">
              <li>Maintaining your authenticated study session (<code className="text-neutral-300">aura_auth_token</code>).</li>
              <li>Preserving offline focus timers, sound preferences, and streak counts.</li>
              <li>Remembering your cookie consent decision.</li>
            </ul>
          </div>

          {/* Section 5 */}
          <div className="p-6 rounded-xl bg-[#0B0E14] border border-neutral-800">
            <h2 className="text-base font-bold font-mono text-white flex items-center gap-2 mb-3">
              <Lock className="w-4 h-4 text-cyan-400" /> 5. DATA SOVEREIGNTY & USER RIGHTS
            </h2>
            <p className="mb-3">
              Under GDPR, CCPA, and global privacy standards, you maintain absolute control over your study data:
            </p>
            <p className="text-xs font-mono text-neutral-400">
              You may purge your telemetry history, delete uploaded lecture documents, or terminate your operator node at any time via the Settings panel or by submitting an eradication request to privacy@aura-study.internal.
            </p>
          </div>
        </div>

        {/* Footer Back */}
        <div className="mt-12 text-center">
          <button
            onClick={onBack}
            className="px-6 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-semibold text-xs transition-colors"
          >
            RETURN TO HOMEPAGE
          </button>
        </div>
      </div>
    </div>
  );
};
