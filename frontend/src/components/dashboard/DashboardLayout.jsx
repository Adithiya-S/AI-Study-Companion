import React, { useState, useEffect, useCallback } from "react";
import { Eye, Clock, Bot, BookOpen, BarChart2, Sliders, LogOut, Flame, Shield, User } from "lucide-react";
import { StatCards } from "./StatCards";
import { SessionTimer } from "./SessionTimer";
import { CameraTracker } from "./CameraTracker";
import { AIChatTab } from "./AIChatTab";
import { MaterialsTab } from "./MaterialsTab";
import { AnalyticsTab } from "./AnalyticsTab";
import { SettingsTab } from "./SettingsTab";
import { GlowBadge } from "../ui/GlowBadge";
import { apiUrl } from "../../lib/api";

export const DashboardLayout = ({ user, onSignOut }) => {
  const [activeTab, setActiveTab] = useState("hub"); // "hub" | "ai" | "materials" | "analytics" | "settings"
  const [distractionCount, setDistractionCount] = useState(0);
  const [liveFocusScore, setLiveFocusScore] = useState(96);
  const [sensitivity, setSensitivity] = useState(() => localStorage.getItem("aura_sensitivity") || "medium");
  const [userStats, setUserStats] = useState({
    totalHours: user?.totalHours ?? 0.0,
    sessions: 0,
    avgScore: 100.0,
    focusStreak: user?.focusStreak || "0 Days",
  });

  const fetchUserStats = useCallback(async () => {
    if (!user?.id) return;
    try {
      const res = await fetch(apiUrl(`/api/auth/user/${user.id}/stats`));
      if (res.ok) {
        const data = await res.json();
        setUserStats({
          totalHours: data.totalHours ?? 0.0,
          sessions: data.sessions ?? 0,
          avgScore: data.avgScore ?? 100.0,
          focusStreak: data.focusStreak || "0 Days",
        });
      }
    } catch (err) {
      console.warn("Could not load user stats:", err);
    }
  }, [user?.id]);

  useEffect(() => {
    fetchUserStats();
  }, [fetchUserStats]);

  const handleSensitivityChange = (newSens) => {
    setSensitivity(newSens);
    localStorage.setItem("aura_sensitivity", newSens);
  };

  const navItems = [
    { id: "hub", label: "01 // LIVE STUDY HUB", icon: Clock },
    { id: "ai", label: "02 // GEMINI AI STUDIO", icon: Bot },
    { id: "materials", label: "03 // MATERIALS & CARDS", icon: BookOpen },
    { id: "analytics", label: "04 // SESSION RECAP", icon: BarChart2 },
    { id: "settings", label: "05 // CONFIGURATION", icon: Sliders },
  ];

  return (
    <div className="min-h-screen bg-[#08090D] text-neutral-200 flex flex-col engineering-grid">
      {/* Top Header */}
      <header className="sticky top-0 z-50 border-b border-neutral-800/90 bg-[#08090D]/95 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#0F131C] border border-cyan-500/40 flex items-center justify-center shadow-[0_0_12px_rgba(0,242,254,0.2)] p-1.5">
              <img src="/favicon.svg" alt="AURA" className="w-full h-full object-contain" />
            </div>
            <div>
              <div className="font-mono text-sm font-bold tracking-wider text-white flex items-center gap-2">
                AURA <span className="text-cyan-400">//</span> AI STUDY COMPANION
              </div>
              <div className="text-[10px] font-mono text-neutral-500">STUDENT OPERATOR NODE</div>
            </div>
          </div>

          {/* Center quick status */}
          <div className="hidden md:flex items-center gap-4">
            <GlowBadge status="active">FOCUS ENGINE: ONLINE</GlowBadge>
            {activeTab !== "hub" && (
              <span className="text-xs font-mono text-cyan-400 font-bold px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30">
                LIVE FOCUS: {liveFocusScore}%
              </span>
            )}
            <span className="text-neutral-700">|</span>
            <div className="flex items-center gap-1.5 text-xs font-mono text-amber-400">
              <Flame className="w-3.5 h-3.5" /> STREAK: {userStats.focusStreak}
            </div>
          </div>

          {/* User profile & Logout */}
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-xs font-mono font-bold text-white">{user?.name || "Student Operator"}</div>
              <div className="text-[10px] font-mono text-neutral-500">{user?.email || ""}</div>
            </div>

            <button
              onClick={onSignOut}
              title="Sign Out"
              className="p-2 rounded-lg border border-neutral-800 bg-[#0D1017] text-neutral-400 hover:text-red-400 hover:border-red-500/30 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tab Strip */}
        <div className="border-t border-neutral-800/60 bg-[#06080C]">
          <div className="max-w-7xl mx-auto px-6 flex items-center gap-1 overflow-x-auto no-scrollbar font-mono text-xs">
            {navItems.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-3 px-4 border-b-2 transition-colors flex items-center gap-2 flex-shrink-0 ${
                    isActive
                      ? "border-cyan-400 text-cyan-400 font-bold bg-[#0D111A]"
                      : "border-transparent text-neutral-400 hover:text-white hover:bg-[#0A0D14]"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        {/* Metric Cards Row (visible across all tabs) */}
        <StatCards
          hours={userStats.totalHours.toString()}
          sessions={userStats.sessions.toString()}
          avgScore={`${userStats.avgScore}%`}
          streak={userStats.focusStreak}
        />

        {/* TAB 1: Live Study Hub (Kept mounted in DOM so camera, face recognition, and timer persist across tab switches) */}
        <div
          className={
            activeTab === "hub"
              ? "grid grid-cols-1 lg:grid-cols-12 gap-8 items-start"
              : "fixed -left-[9999px] top-0 w-[1200px] pointer-events-none opacity-0 overflow-hidden"
          }
        >
          <div className="lg:col-span-6">
            <SessionTimer
              user={user}
              distractions={distractionCount}
              focusScore={liveFocusScore}
              onSessionFinished={fetchUserStats}
              onSessionStateChange={(state) => {
                console.log("Session state:", state);
              }}
            />
          </div>
          <div className="lg:col-span-6">
            <CameraTracker
              sensitivity={sensitivity}
              onDistractionUpdate={(count) => setDistractionCount(count)}
              onFocusUpdate={(score) => setLiveFocusScore(score)}
            />
          </div>
        </div>

        {/* TAB 2: AI Study Studio */}
        {activeTab === "ai" && <AIChatTab />}

        {/* TAB 3: Study Materials & Flashcards */}
        {activeTab === "materials" && <MaterialsTab user={user} />}

        {/* TAB 4: Analytics */}
        {activeTab === "analytics" && (
          <AnalyticsTab user={user} refreshKey={userStats.sessions} />
        )}

        {/* TAB 5: Settings */}
        {activeTab === "settings" && (
          <SettingsTab
            sensitivity={sensitivity}
            onSensitivityChange={handleSensitivityChange}
          />
        )}
      </main>
    </div>
  );
};
