import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Eye, Activity, Cpu, ShieldCheck, Zap, Sparkles, ArrowRight, Play } from "lucide-react";
import { TiltCard } from "../ui/TiltCard";
import { BorderBeam } from "../ui/BorderBeam";
import { MagneticButton } from "../ui/MagneticButton";
import { GlowBadge } from "../ui/GlowBadge";
import { Spotlight } from "../ui/Spotlight";

export const Hero = ({ onOpenAuth, onOpenDashboard }) => {
  // Live simulated telemetry ticks for hero visual demonstration
  const [telemetry, setTelemetry] = useState({
    focusScore: 96.4,
    ear: 0.31,
    gazeX: 0.02,
    gazeY: -0.01,
    distractionCount: 0,
    fps: 29.8,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setTelemetry((prev) => ({
        focusScore: +(95 + Math.random() * 3.8).toFixed(1),
        ear: +(0.29 + Math.random() * 0.05).toFixed(2),
        gazeX: +(Math.sin(Date.now() / 1500) * 0.06).toFixed(2),
        gazeY: +(Math.cos(Date.now() / 2000) * 0.04).toFixed(2),
        distractionCount: prev.distractionCount,
        fps: +(29.2 + Math.random() * 0.9).toFixed(1),
      }));
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative pt-20 pb-28 px-6 overflow-hidden">
      <Spotlight fill="rgba(0, 242, 254, 0.15)" size={550} />

      <div className="max-w-7xl mx-auto">
        {/* Top telemetry status pill */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex justify-center mb-8"
        >
          <div className="inline-flex items-center gap-3 px-4 py-1.5 rounded-full border border-neutral-800 bg-[#0E121A] text-xs font-mono text-neutral-300">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
            </span>
            <span>SYSTEM STATE: OPTIMAL FOCUS TELEMETRY</span>
            <span className="text-neutral-600">|</span>
            <span className="text-cyan-400 font-semibold">ZERO DISTRACTION PROTOCOL</span>
          </div>
        </motion.div>

        {/* Main Headline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-center max-w-4xl mx-auto space-y-6"
        >
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-white font-sans">
            DEEP FOCUS THROUGH{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-emerald-400 to-cyan-300">
              INTELLIGENT EYE TRACKING
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-neutral-400 font-normal max-w-2xl mx-auto leading-relaxed">
            The no-nonsense study assistant engineered for developers and students. Real-time eye-tracking,
            sub-second distraction alerting, adaptive Pomodoro rhythm, and Gemini-powered lecture tutoring.
          </p>

          {/* CTA Row */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <MagneticButton
              variant="primary"
              onClick={onOpenDashboard}
              className="text-base px-8 py-3.5 flex items-center gap-2 shadow-[0_0_30px_rgba(0,242,254,0.35)]"
            >
              <Play className="w-4 h-4 fill-black text-black" /> INITIALIZE WORKSPACE
            </MagneticButton>
            <MagneticButton
              variant="secondary"
              onClick={onOpenAuth}
              className="text-base px-6 py-3.5 flex items-center gap-2"
            >
              SIGN IN // REGISTER <ArrowRight className="w-4 h-4" />
            </MagneticButton>
          </div>

          <div className="flex items-center justify-center gap-8 pt-6 text-xs font-mono text-neutral-500">
            <span className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> LOCAL CAMERA PRIVACY</span>
            <span className="flex items-center gap-1.5"><Zap className="w-3.5 h-3.5 text-cyan-400" /> ZERO LATENCY HUD</span>
            <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-purple-400" /> GEMINI MULTI-MODAL</span>
          </div>
        </motion.div>

        {/* Hero Interactive Telemetry Card (3D Tilt with Border Beam) */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mt-16 max-w-5xl mx-auto"
        >
          <TiltCard className="p-1 rounded-2xl bg-[#0B0D14] border border-[#1C212E] shadow-2xl relative">
            <BorderBeam size={280} duration={10} colorFrom="#00F2FE" colorTo="#10B981" />

            {/* Inner HUD Terminal */}
            <div className="bg-[#090B10] rounded-xl p-6 lg:p-8 space-y-6">
              {/* Terminal Window Header */}
              <div className="flex items-center justify-between border-b border-neutral-800/80 pb-4">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
                  <span className="w-3 h-3 rounded-full bg-yellow-500/80 inline-block" />
                  <span className="w-3 h-3 rounded-full bg-green-500/80 inline-block" />
                  <span className="ml-3 font-mono text-xs text-neutral-400">
                    AURA_CORE_DAEMON // PID: 8044 // OPENCV_WEBCAM_NODE
                  </span>
                </div>
                <GlowBadge status="active">TELEMETRY STREAM: 30 FPS</GlowBadge>
              </div>

              {/* Grid: Left Simulated Camera Wireframe, Right Telemetry Matrix */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
                {/* Visualizer Simulation Box */}
                <div className="md:col-span-7 bg-[#05060A] border border-neutral-800 rounded-lg p-6 relative overflow-hidden h-64 flex flex-col justify-between corner-bracket">
                  <div className="flex justify-between items-start text-[11px] font-mono text-neutral-500">
                    <div>FOV: 78° // GAZE: ({telemetry.gazeX}, {telemetry.gazeY})</div>
                    <div className="text-cyan-400">IRIS_LOCK: TRUE</div>
                  </div>

                  {/* Wireframe Face & Iris Simulation */}
                  <div className="relative mx-auto my-auto w-36 h-36 border border-dashed border-cyan-500/30 rounded-full flex items-center justify-center">
                    {/* Concentric scan rings */}
                    <div className="w-24 h-24 rounded-full border border-cyan-500/50 animate-ping opacity-25" />
                    <div className="absolute w-28 h-28 rounded-full border border-cyan-400/40" />

                    {/* Left & Right Pupil tracking crosses */}
                    <div className="absolute left-6 top-12 w-4 h-4 border-t border-l border-cyan-400 flex items-center justify-center">
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                    </div>
                    <div className="absolute right-6 top-12 w-4 h-4 border-t border-r border-cyan-400 flex items-center justify-center">
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                    </div>

                    {/* Center focus indicator */}
                    <div className="w-3 h-3 rounded-full bg-emerald-400 shadow-[0_0_15px_#10B981]" />
                  </div>

                  <div className="flex justify-between items-end text-[11px] font-mono">
                    <span className="text-emerald-400 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> STATE: DEEP WORK
                    </span>
                    <span className="text-neutral-500">EAR: {telemetry.ear}</span>
                  </div>
                </div>

                {/* Telemetry Matrix Rows */}
                <div className="md:col-span-5 space-y-4">
                  <div className="p-4 rounded-lg bg-[#0D1017] border border-neutral-800/80">
                    <div className="text-xs font-mono text-neutral-400 mb-1 flex justify-between">
                      <span>LIVE FOCUS EFFICIENCY</span>
                      <span className="text-emerald-400 font-bold">{telemetry.focusScore}%</span>
                    </div>
                    <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all duration-500 rounded-full"
                        style={{ width: `${telemetry.focusScore}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3.5 rounded-lg bg-[#0D1017] border border-neutral-800/80">
                      <div className="text-[10px] font-mono text-neutral-500">CURRENT STREAK</div>
                      <div className="text-xl font-mono font-bold text-white mt-1">42m 18s</div>
                    </div>
                    <div className="p-3.5 rounded-lg bg-[#0D1017] border border-neutral-800/80">
                      <div className="text-[10px] font-mono text-neutral-500">DISTRACTIONS</div>
                      <div className="text-xl font-mono font-bold text-emerald-400 mt-1">0 DETECTED</div>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-lg bg-[#0D1017] border border-neutral-800/80 flex items-center justify-between">
                    <div>
                      <div className="text-[10px] font-mono text-neutral-500">AI TUTOR SYNC</div>
                      <div className="text-xs font-mono text-neutral-300">3 LECTURE NOTES LOADED</div>
                    </div>
                    <GlowBadge status="cyan">READY</GlowBadge>
                  </div>
                </div>
              </div>
            </div>
          </TiltCard>
        </motion.div>
      </div>
    </section>
  );
};
