import React from "react";
import { motion } from "framer-motion";
import { Eye, BookOpen, Clock, Database, Sparkles, AlertCircle, ArrowUpRight } from "lucide-react";
import { TiltCard } from "../ui/TiltCard";

export const FeaturesBento = ({ onOpenDashboard }) => {
  const features = [
    {
      id: "01",
      title: "SUB-SECOND EYE & GAZE TRACKING",
      subtitle: "Eye Aspect Ratio (EAR) & Gaze Vectors",
      description:
        "MediaPipe face mesh calculates eye openness and head orientation 30 times per second. Looking away or phone usage triggers instant subtle haptic/audio recovery cues.",
      icon: Eye,
      tag: "COMPUTER VISION",
      accent: "from-cyan-500/20 to-cyan-500/0",
      borderAccent: "hover:border-cyan-500/40",
      colSpan: "col-span-1 md:col-span-8",
    },
    {
      id: "02",
      title: "MULTI-MODAL GEMINI TUTOR",
      subtitle: "Contextual Document Ingestion",
      description:
        "Upload PDFs, slide decks, or markdown notes. Ask questions, generate flashcards, or take active-recall quizzes directly from your material.",
      icon: BookOpen,
      tag: "LLM INTEGRATION",
      accent: "from-purple-500/20 to-purple-500/0",
      borderAccent: "hover:border-purple-500/40",
      colSpan: "col-span-1 md:col-span-4",
    },
    {
      id: "03",
      title: "ADAPTIVE POMODORO ENGINE",
      subtitle: "Dynamic Rest Durations",
      description:
        "Standard 25/5 timers ignore cognitive load. Our engine lengthens rest intervals if prolonged deep focus fatigue or heavy distraction spikes are logged.",
      icon: Clock,
      tag: "COGNITIVE ERGONOMICS",
      accent: "from-emerald-500/20 to-emerald-500/0",
      borderAccent: "hover:border-emerald-500/40",
      colSpan: "col-span-1 md:col-span-4",
    },
    {
      id: "04",
      title: "POSTGRESQL & DRIFT SNAPSHOTS",
      subtitle: "Zero Data Leakage & Row Auditing",
      description:
        "Engineered with clean SQL models for sessions, distractions, and study notes. Fully compatible with @driftcli/drift for instant fixture rollback and row-level diffing.",
      icon: Database,
      tag: "DATA RESILIENCE",
      accent: "from-amber-500/20 to-amber-500/0",
      borderAccent: "hover:border-amber-500/40",
      colSpan: "col-span-1 md:col-span-8",
    },
  ];

  return (
    <section className="py-24 px-6 relative border-t border-neutral-800/60 bg-[#06080C]">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
          <div>
            <div className="text-xs font-mono text-cyan-400 mb-2">// SPECIFICATIONS</div>
            <h2 className="text-3xl sm:text-4xl font-bold font-sans text-white">
              BUILT FOR HIGH-COGNITION PERFORMANCE
            </h2>
          </div>
          <p className="text-sm font-mono text-neutral-500 mt-2 md:mt-0 max-w-sm">
            Engineered from ground up with zero UI bloat. Every pixel serves deliberate focus.
          </p>
        </div>

        {/* Bento Grid with 3D Tilt */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {features.map((item, idx) => {
            const Icon = item.icon;
            return (
              <TiltCard
                key={item.id}
                intensity={10}
                className={`${item.colSpan} p-8 bg-[#090C12] border border-[#181D2A] ${item.borderAccent} flex flex-col justify-between group cursor-pointer`}
                onClick={onOpenDashboard}
              >
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <span className="font-mono text-xs text-neutral-500">[{item.id}] // {item.tag}</span>
                    <div className="w-9 h-9 rounded-lg bg-[#101522] border border-neutral-800 flex items-center justify-center text-neutral-300 group-hover:text-cyan-400 transition-colors">
                      <Icon className="w-4 h-4" />
                    </div>
                  </div>

                  <h3 className="text-xl font-bold text-white mb-1 group-hover:text-cyan-300 transition-colors">
                    {item.title}
                  </h3>
                  <div className="text-xs font-mono text-neutral-400 mb-4">{item.subtitle}</div>
                  <p className="text-sm text-neutral-400 leading-relaxed">{item.description}</p>
                </div>

                <div className="pt-8 flex items-center justify-between border-t border-neutral-800/60 mt-6 text-xs font-mono text-neutral-500 group-hover:text-cyan-400 transition-colors">
                  <span>DEPLOY MODULE</span>
                  <ArrowUpRight className="w-4 h-4 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </div>
              </TiltCard>
            );
          })}
        </div>
      </div>
    </section>
  );
};
