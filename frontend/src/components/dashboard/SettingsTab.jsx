import React, { useState } from "react";
import { Sliders, Volume2, Shield, Key, Check, Eye } from "lucide-react";
import { GlowBadge } from "../ui/GlowBadge";

export const SettingsTab = () => {
  const [sensitivity, setSensitivity] = useState("medium"); // "low" | "medium" | "high"
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [outlineEnabled, setOutlineEnabled] = useState(true);
  const [apiKey, setApiKey] = useState("");
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div className="border-b border-neutral-800 pb-4 flex items-center justify-between">
        <div>
          <h3 className="text-base font-mono font-bold text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" /> SYSTEM CONFIGURATION
          </h3>
          <p className="text-xs font-mono text-neutral-500">
            Tune computer vision parameters, audio alerts, and API authentication
          </p>
        </div>
        <GlowBadge status="active">NODE: CONFIG_SYNCED</GlowBadge>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Card 1: Eye Tracking Sensitivity */}
        <div className="p-5 rounded-xl bg-[#0B0E14] border border-neutral-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-mono font-bold text-white">TRACKING SENSITIVITY</div>
              <div className="text-xs text-neutral-500 font-mono">
                Threshold for registering eye closure and gaze deviation
              </div>
            </div>
            <span className="text-xs font-mono text-cyan-400 font-bold uppercase">{sensitivity}</span>
          </div>

          <div className="grid grid-cols-3 gap-3 font-mono text-xs">
            {["low", "medium", "high"].map((level) => (
              <button
                key={level}
                type="button"
                onClick={() => setSensitivity(level)}
                className={`py-2.5 rounded-lg border uppercase transition-colors ${
                  sensitivity === level
                    ? "bg-cyan-500/10 border-cyan-500/40 text-cyan-400 font-bold"
                    : "border-neutral-800 text-neutral-400 hover:border-neutral-700"
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Card 2: Audio & HUD Toggles */}
        <div className="p-5 rounded-xl bg-[#0B0E14] border border-neutral-800 space-y-4">
          <div className="text-sm font-mono font-bold text-white mb-2">TELEMETRY & FEEDBACK</div>

          <div className="flex items-center justify-between py-2 border-b border-neutral-800/60">
            <div>
              <div className="text-xs font-mono text-neutral-200">SYNTHESIZED AUDIO CHIMES</div>
              <div className="text-[11px] text-neutral-500">Play harmonic bell alerts on session milestones</div>
            </div>
            <button
              type="button"
              onClick={() => setSoundEnabled(!soundEnabled)}
              className={`w-11 h-6 rounded-full transition-colors relative ${
                soundEnabled ? "bg-cyan-500" : "bg-neutral-800"
              }`}
            >
              <span
                className={`block w-4 h-4 rounded-full bg-white transition-transform ${
                  soundEnabled ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between py-2">
            <div>
              <div className="text-xs font-mono text-neutral-200">SHOW FACE MESH CONTOURS</div>
              <div className="text-[11px] text-neutral-500">Draw facial wireframe and iris vector markers on camera HUD</div>
            </div>
            <button
              type="button"
              onClick={() => setOutlineEnabled(!outlineEnabled)}
              className={`w-11 h-6 rounded-full transition-colors relative ${
                outlineEnabled ? "bg-cyan-500" : "bg-neutral-800"
              }`}
            >
              <span
                className={`block w-4 h-4 rounded-full bg-white transition-transform ${
                  outlineEnabled ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </div>

        {/* Card 3: Gemini API Key */}
        <div className="p-5 rounded-xl bg-[#0B0E14] border border-neutral-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="text-sm font-mono font-bold text-white flex items-center gap-2">
              <Key className="w-4 h-4 text-purple-400" /> GOOGLE GEMINI API KEY
            </div>
            <span className="text-[11px] font-mono text-neutral-500">FREE PERSONAL TIER (60 RPM)</span>
          </div>
          <p className="text-xs text-neutral-400 font-mono">
            Provide a custom Gemini API key for uncapped document QA and lecture synthesis. If blank, the app uses built-in smart responses.
          </p>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="AIzaSy..."
            className="w-full px-3.5 py-2.5 rounded-lg bg-[#07090D] border border-neutral-800 text-sm text-white font-mono focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        {/* Save button */}
        <div className="flex items-center justify-between pt-2">
          <button
            type="submit"
            className="px-6 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-mono text-xs font-bold transition-colors shadow-[0_0_15px_rgba(0,242,254,0.25)] flex items-center gap-2"
          >
            {saved ? (
              <>
                <Check className="w-4 h-4" /> PREFERENCES SAVED
              </>
            ) : (
              "COMMIT CONFIGURATION"
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
