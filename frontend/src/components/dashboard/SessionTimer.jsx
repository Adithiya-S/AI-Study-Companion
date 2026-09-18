import React, { useState, useEffect, useRef } from "react";
import { Play, Pause, RotateCcw, Flame, CheckCircle, BellRing, Coffee, Award, X, Sparkles } from "lucide-react";
import { MagneticButton } from "../ui/MagneticButton";
import { GlowBadge } from "../ui/GlowBadge";
import { sounds } from "../../lib/audio";
import { apiUrl } from "../../lib/api";
import confetti from "canvas-confetti";

export const SessionTimer = ({
  user,
  onSessionFinished,
  onSessionStateChange,
  distractions = 0,
  focusScore = 95,
}) => {
  const [mode, setMode] = useState("pomodoro"); // "pomodoro" (25) | "deepwork" (50) | "break" (5) | "longbreak" (15)
  const [totalTime, setTotalTime] = useState(25 * 60);
  const [timeLeft, setTimeLeft] = useState(25 * 60);
  const [isActive, setIsActive] = useState(false);
  const [sessionCount, setSessionCount] = useState(0);
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const sessionIdRef = useRef(null);
  const prevDistractionsRef = useRef(distractions);

  const startSessionBackend = async () => {
    if (!user?.id) return;
    try {
      const res = await fetch(apiUrl("/api/sessions/start"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          mode: mode,
          duration_minutes: Math.round(totalTime / 60),
        }),
      });
      if (res.ok) {
        const data = await res.json();
        sessionIdRef.current = data.session_id;
      }
    } catch (e) {
      console.warn("Could not record session start:", e);
    }
  };

  const endSessionBackend = async (completed = false) => {
    if (!sessionIdRef.current) return;
    const elapsedMinutes = Math.max(1, Math.round((totalTime - timeLeft) / 60));
    try {
      await fetch(apiUrl("/api/sessions/end"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionIdRef.current,
          focus_score: focusScore,
          actual_duration_minutes: completed ? Math.round(totalTime / 60) : elapsedMinutes,
        }),
      });
      sessionIdRef.current = null;
      if (onSessionFinished) {
        onSessionFinished();
      }
    } catch (e) {
      console.warn("Could not record session end:", e);
    }
  };

  // Log live distractions to session if active
  useEffect(() => {
    if (isActive && distractions > prevDistractionsRef.current && sessionIdRef.current) {
      fetch(apiUrl("/api/sessions/log-distraction"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionIdRef.current,
          distraction_type: "looking_away",
          ear_value: 0.18,
        }),
      }).catch((e) => console.warn("Distraction log error:", e));
    }
    prevDistractionsRef.current = distractions;
  }, [distractions, isActive]);

  // Set mode times
  const selectMode = (newMode) => {
    if (isActive && sessionIdRef.current) {
      endSessionBackend(false);
    }
    setIsActive(false);
    setMode(newMode);
    let seconds = 25 * 60;
    if (newMode === "pomodoro") seconds = 25 * 60;
    else if (newMode === "deepwork") seconds = 50 * 60;
    else if (newMode === "break") seconds = 5 * 60;
    else if (newMode === "longbreak") seconds = 15 * 60;

    setTotalTime(seconds);
    setTimeLeft(seconds);
    onSessionStateChange && onSessionStateChange({ isActive: false, mode: newMode });
  };

  // Timer interval
  useEffect(() => {
    let interval = null;
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((time) => time - 1);
      }, 1000);
    } else if (timeLeft === 0 && isActive) {
      setIsActive(false);
      sounds.playComplete();
      confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
      setSessionCount((prev) => prev + 1);
      setShowSummaryModal(true);
      endSessionBackend(true);
      onSessionStateChange && onSessionStateChange({ isActive: false, completed: true });
    }
    return () => clearInterval(interval);
  }, [isActive, timeLeft, onSessionStateChange]);

  const toggleTimer = () => {
    if (!isActive) {
      sounds.playStart();
      setIsActive(true);
      startSessionBackend();
      onSessionStateChange && onSessionStateChange({ isActive: true, mode });
    } else {
      setIsActive(false);
      onSessionStateChange && onSessionStateChange({ isActive: false, mode });
    }
  };

  const resetTimer = () => {
    if (isActive && sessionIdRef.current) {
      endSessionBackend(false);
    }
    setIsActive(false);
    setTimeLeft(totalTime);
    onSessionStateChange && onSessionStateChange({ isActive: false, mode });
  };

  const handleEndEarly = () => {
    if (isActive || timeLeft < totalTime) {
      setIsActive(false);
      setShowSummaryModal(true);
      endSessionBackend(false);
      onSessionStateChange && onSessionStateChange({ isActive: false, completed: false });
    }
  };

  // SVG Circular progress
  const radius = 105;
  const circumference = 2 * Math.PI * radius;
  const progress = (timeLeft / totalTime) * circumference;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const minutesStudied = Math.max(1, Math.round((totalTime - timeLeft) / 60));
  // Under 7 distractions is evaluated as really good & highly focused:
  const isReallyGood = distractions < 7;
  const efficiency = isReallyGood
    ? Math.max(90, Math.round(99 - distractions * 1.3))
    : Math.max(45, Math.round(90 - (distractions - 6) * 4.5));

  return (
    <div className="rounded-xl border border-neutral-800 bg-[#0B0E14] p-6 flex flex-col items-center justify-between relative overflow-hidden">
      {/* Modes Bar */}
      <div className="flex items-center gap-1.5 p-1 bg-[#07090D] border border-neutral-800 rounded-lg text-xs font-mono mb-6">
        <button
          onClick={() => selectMode("pomodoro")}
          className={`px-3 py-1.5 rounded-md transition-colors ${
            mode === "pomodoro" ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/40 font-bold" : "text-neutral-400 hover:text-white"
          }`}
        >
          POMODORO (25M)
        </button>
        <button
          onClick={() => selectMode("deepwork")}
          className={`px-3 py-1.5 rounded-md transition-colors ${
            mode === "deepwork" ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/40 font-bold" : "text-neutral-400 hover:text-white"
          }`}
        >
          DEEP WORK (50M)
        </button>
        <button
          onClick={() => selectMode("break")}
          className={`px-3 py-1.5 rounded-md transition-colors ${
            mode === "break" ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/40 font-bold" : "text-neutral-400 hover:text-white"
          }`}
        >
          BREAK (5M)
        </button>
      </div>

      {/* Circular SVG Timer */}
      <div className="relative w-64 h-64 flex items-center justify-center my-2">
        <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 240 240">
          {/* Background Track */}
          <circle
            cx="120"
            cy="120"
            r={radius}
            stroke="#161B26"
            strokeWidth="8"
            fill="transparent"
          />
          {/* Active Animated Progress Arc */}
          <circle
            cx="120"
            cy="120"
            r={radius}
            stroke={mode === "break" ? "#10B981" : "#00F2FE"}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-500 ease-linear shadow-[0_0_20px_#00F2FE]"
          />
        </svg>

        {/* Center Digital Display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <div className="font-mono text-5xl font-bold tracking-tight text-white select-none">
            {formatTime(timeLeft)}
          </div>
          <div className="text-[11px] font-mono tracking-widest text-neutral-500 mt-2">
            {isActive ? (
              <span className="text-cyan-400 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" /> SPRINT ACTIVE
              </span>
            ) : (
              "READY TO START"
            )}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3 mt-4">
        <MagneticButton
          variant={isActive ? "secondary" : "primary"}
          onClick={toggleTimer}
          className="text-sm px-6 py-2.5 font-mono flex items-center gap-2"
        >
          {isActive ? (
            <>
              <Pause className="w-4 h-4" /> PAUSE
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" /> START SPRINT
            </>
          )}
        </MagneticButton>

        <button
          onClick={resetTimer}
          title="Reset Timer"
          className="p-2.5 rounded-lg border border-neutral-800 bg-[#0E121A] text-neutral-400 hover:text-white hover:border-neutral-700 transition-colors cursor-pointer"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        <button
          onClick={handleEndEarly}
          title="End Session & Review Stats"
          className="px-3 py-2 rounded-lg border border-neutral-800 bg-[#0E121A] text-xs font-mono text-neutral-400 hover:text-red-400 hover:border-red-500/40 transition-colors cursor-pointer"
        >
          END
        </button>
      </div>

      {/* Bottom status badges */}
      <div className="w-full mt-6 pt-4 border-t border-neutral-800/80 flex items-center justify-between text-xs font-mono text-neutral-400">
        <span className="flex items-center gap-1.5">
          <Flame className="w-3.5 h-3.5 text-amber-400" /> SESSIONS: <strong className="text-white">{sessionCount}</strong>
        </span>
        <span className="flex items-center gap-1.5">
          DISTRACTIONS: <strong className={distractions > 0 ? "text-amber-400" : "text-emerald-400"}>{distractions}</strong>
        </span>
      </div>

      {/* Session Completion Summary Modal (Replicates original show_session_summary) */}
      {showSummaryModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-[#0B0E14] border border-cyan-500/40 rounded-2xl max-w-md w-full p-6 space-y-5 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
              <div className="flex items-center gap-2 font-mono text-sm font-bold text-white">
                <Award className="w-5 h-5 text-cyan-400" /> SPRINT TELEMETRY REPORT
              </div>
              <button
                onClick={() => setShowSummaryModal(false)}
                className="p-1 text-neutral-400 hover:text-white rounded hover:bg-neutral-800 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-center py-2">
              <div className="text-3xl font-mono font-bold text-cyan-300">
                {efficiency}%
              </div>
              <div className="text-xs font-mono text-neutral-400 tracking-wider mt-1">
                COMPOSITE FOCUS EFFICIENCY
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 font-mono text-xs text-center">
              <div className="p-3 rounded-lg bg-[#07090D] border border-neutral-800">
                <div className="text-[10px] text-neutral-500">TIME STUDIED</div>
                <div className="text-white font-bold mt-0.5">{minutesStudied}m</div>
              </div>
              <div className="p-3 rounded-lg bg-[#07090D] border border-neutral-800">
                <div className="text-[10px] text-neutral-500">DISTRACTIONS</div>
                <div className="text-amber-400 font-bold mt-0.5">{distractions}</div>
              </div>
              <div className="p-3 rounded-lg bg-[#07090D] border border-neutral-800">
                <div className="text-[10px] text-neutral-500">AVG SCORE</div>
                <div className="text-emerald-400 font-bold mt-0.5">{focusScore}%</div>
              </div>
            </div>

            <div className="p-3.5 rounded-lg bg-[#07090D] border border-neutral-800/80 text-xs font-mono space-y-1">
              <div className={isReallyGood ? "text-emerald-400 font-bold flex items-center gap-1.5" : "text-amber-400 font-bold flex items-center gap-1.5"}>
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                {isReallyGood
                  ? `Really Good Focus! (${distractions} distraction${distractions === 1 ? "" : "s"} < 7)`
                  : `Sprint Complete (${distractions} distractions logged)`}
              </div>
              <div className="text-neutral-400">
                {isReallyGood
                  ? "Outstanding cognitive discipline. You stayed locked on target throughout the sprint!"
                  : "Distraction threshold was exceeded. Consider placing your phone out of reach for the next round."}
              </div>
            </div>

            <button
              onClick={() => {
                setShowSummaryModal(false);
                resetTimer();
              }}
              className="w-full py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-bold text-xs transition-colors cursor-pointer"
            >
              NEXT STUDY INTERVAL
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
