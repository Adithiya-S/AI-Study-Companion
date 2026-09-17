import React from "react";
import { Clock, CheckCircle2, TrendingUp, ShieldAlert } from "lucide-react";

export const StatCards = ({
  hours = "0.0",
  sessions = "0",
  avgScore = "100%",
  streak = "1 Day",
}) => {
  const isNew = parseInt(sessions, 10) === 0;

  const stats = [
    {
      label: "TOTAL FOCUS HOURS",
      val: `${hours}h`,
      sub: isNew ? "Start your first sprint" : "Logged study time",
      icon: Clock,
      color: "text-cyan-400",
      border: "hover:border-cyan-500/40",
    },
    {
      label: "COMPLETED SPRINTS",
      val: sessions,
      sub: isNew ? "No sessions recorded yet" : "Completed telemetry sprints",
      icon: CheckCircle2,
      color: "text-emerald-400",
      border: "hover:border-emerald-500/40",
    },
    {
      label: "AVG FOCUS EFFICIENCY",
      val: avgScore,
      sub: isNew ? "Awaiting session data" : "Biometric focus average",
      icon: TrendingUp,
      color: "text-purple-400",
      border: "hover:border-purple-500/40",
    },
    {
      label: "DEEP WORK STREAK",
      val: streak,
      sub: isNew ? "No streak yet – start studying!" : "Consistent study days",
      icon: ShieldAlert,
      color: "text-amber-400",
      border: "hover:border-amber-500/40",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {stats.map((s, i) => {
        const Icon = s.icon;
        return (
          <div
            key={i}
            className={`p-4 rounded-xl bg-[#0B0E14] border border-neutral-800 transition-colors ${s.border}`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-wider">
                {s.label}
              </span>
              <Icon className={`w-4 h-4 ${s.color}`} />
            </div>
            <div className="text-2xl font-mono font-bold text-white tracking-tight">
              {s.val}
            </div>
            <div className="text-[11px] font-mono text-neutral-400 mt-1">
              {s.sub}
            </div>
          </div>
        );
      })}
    </div>
  );
};
