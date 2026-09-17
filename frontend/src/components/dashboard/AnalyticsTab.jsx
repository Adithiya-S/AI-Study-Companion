import React, { useState, useEffect } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";
import { Download, Calendar, BarChart2, TrendingUp, CheckCircle, Clock, Zap, Target, AlertCircle } from "lucide-react";
import { GlowBadge } from "../ui/GlowBadge";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export const AnalyticsTab = ({ user, refreshKey }) => {
  const [period, setPeriod] = useState(7); // 1 | 7 | 14 | 30 days
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) return;
    setLoading(true);
    fetch(`http://127.0.0.1:8000/api/sessions/analytics?user_id=${user.id}&period=${period}`)
      .then((r) => r.json())
      .then((data) => {
        setAnalytics(data);
        setLoading(false);
      })
      .catch((err) => {
        console.warn("Analytics fetch failed:", err);
        setLoading(false);
      });
  }, [user?.id, period, refreshKey]);

  const summary = analytics?.summary || {
    total_sessions: 0,
    total_hours: 0.0,
    avg_duration: 0,
    overall_focus: 0.0,
    efficiency: 0.0,
    total_distractions: 0,
  };

  const hasSessions = summary.total_sessions > 0;

  // Real or initial bar data
  const barData = {
    labels:
      analytics?.bar_data?.labels && analytics.bar_data.labels.length > 0
        ? analytics.bar_data.labels
        : period === 1
        ? ["Morning", "Afternoon", "Evening", "Night"]
        : ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    datasets: [
      {
        label: "Study Hours",
        data:
          analytics?.bar_data?.values && analytics.bar_data.values.length > 0
            ? analytics.bar_data.values
            : [0, 0, 0, 0],
        backgroundColor: "rgba(0, 242, 254, 0.6)",
        hoverBackgroundColor: "rgba(0, 242, 254, 0.9)",
        borderColor: "#00F2FE",
        borderWidth: 1,
        borderRadius: 6,
      },
    ],
  };

  // Real or initial focus trend line data
  const lineLabels =
    analytics?.line_data?.labels && analytics.line_data.labels.length > 0
      ? analytics.line_data.labels
      : ["Standby"];
  const lineValues =
    analytics?.line_data?.values && analytics.line_data.values.length > 0
      ? analytics.line_data.values
      : [100];

  const lineData = {
    labels: lineLabels,
    datasets: [
      {
        label: "Focus Score %",
        data: lineValues,
        fill: true,
        backgroundColor: "rgba(16, 185, 129, 0.1)",
        borderColor: "#10B981",
        pointBackgroundColor: "#10B981",
        tension: 0.35,
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: "#94A3B8",
          font: { family: "JetBrains Mono", size: 11 },
        },
      },
      tooltip: {
        backgroundColor: "#0D1117",
        titleColor: "#FFFFFF",
        bodyColor: "#00F2FE",
        borderColor: "#1E2433",
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: { color: "rgba(255,255,255,0.04)" },
        ticks: { color: "#64748B", font: { family: "JetBrains Mono", size: 10 } },
      },
      y: {
        grid: { color: "rgba(255,255,255,0.04)" },
        ticks: { color: "#64748B", font: { family: "JetBrains Mono", size: 10 } },
      },
    },
  };

  const sessionsHistory = analytics?.history || [];

  const exportCSV = () => {
    if (sessionsHistory.length === 0) {
      alert("No study sessions logged yet to export.");
      return;
    }
    const headers = "Session ID,Date,Type,Duration,Focus Score,Distractions\n";
    const rows = sessionsHistory
      .map((s) => `${s.id},${s.date},${s.type},${s.duration},${s.score}%,${s.distractions}`)
      .join("\n");
    const blob = new Blob([headers + rows], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `aura_study_recap_${user?.id || "user"}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Header and export */}
      <div className="flex flex-wrap items-center justify-between border-b border-neutral-800 pb-4 gap-3">
        <div>
          <h3 className="text-base font-mono font-bold text-white flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-cyan-400" /> STUDY SESSION RECAP
          </h3>
          <p className="text-xs font-mono text-neutral-500">
            Live biometric focus analytics logged from your real study sprints
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Period Selector (1, 7, 14, 30 days) */}
          <div className="flex items-center bg-[#07090D] p-1 rounded-lg border border-neutral-800 text-xs font-mono">
            {[1, 7, 14, 30].map((d) => (
              <button
                key={d}
                onClick={() => setPeriod(d)}
                className={`px-3 py-1 rounded transition-colors cursor-pointer ${
                  period === d
                    ? "bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30"
                    : "text-neutral-400 hover:text-white"
                }`}
              >
                {d}D
              </button>
            ))}
          </div>

          <button
            onClick={exportCSV}
            className="text-xs font-mono px-3.5 py-1.5 rounded-lg border border-neutral-800 bg-[#0E121A] text-neutral-300 hover:text-cyan-400 hover:border-cyan-500/40 transition-colors flex items-center gap-2 cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" /> CSV EXPORT
          </button>
        </div>
      </div>

      {/* Real Productivity Report Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono text-xs">
        <div className="p-3.5 rounded-xl bg-[#0B0E14] border border-neutral-800 text-center">
          <div className="text-[10px] text-neutral-500">TOTAL SESSIONS</div>
          <div className="text-lg font-bold text-white mt-1">{summary.total_sessions}</div>
        </div>
        <div className="p-3.5 rounded-xl bg-[#0B0E14] border border-neutral-800 text-center">
          <div className="text-[10px] text-neutral-500">TOTAL STUDY TIME</div>
          <div className="text-lg font-bold text-cyan-400 mt-1">{summary.total_hours}h</div>
        </div>
        <div className="p-3.5 rounded-xl bg-[#0B0E14] border border-neutral-800 text-center">
          <div className="text-[10px] text-neutral-500">AVG SESSION</div>
          <div className="text-lg font-bold text-neutral-200 mt-1">{summary.avg_duration}m</div>
        </div>
        <div className="p-3.5 rounded-xl bg-[#0B0E14] border border-neutral-800 text-center">
          <div className="text-[10px] text-neutral-500">OVERALL FOCUS</div>
          <div className="text-lg font-bold text-emerald-400 mt-1">
            {hasSessions ? `${summary.overall_focus}%` : "--"}
          </div>
        </div>
        <div className="p-3.5 rounded-xl bg-[#0B0E14] border border-neutral-800 text-center">
          <div className="text-[10px] text-neutral-500">EFFICIENCY</div>
          <div className="text-lg font-bold text-purple-400 mt-1">
            {hasSessions ? `${summary.efficiency}%` : "--"}
          </div>
        </div>
        <div className="p-3.5 rounded-xl bg-[#0B0E14] border border-neutral-800 text-center">
          <div className="text-[10px] text-neutral-500">DISTRACTIONS</div>
          <div className="text-lg font-bold text-amber-400 mt-1">{summary.total_distractions}</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1 */}
        <div className="p-5 rounded-xl bg-[#0B0E14] border border-neutral-800">
          <div className="text-xs font-mono text-neutral-400 mb-4 flex items-center justify-between">
            <span>PERIOD STUDY DURATION ({period} DAYS)</span>
            <GlowBadge status="cyan">TOTAL: {summary.total_hours}H</GlowBadge>
          </div>
          <div className="h-64">
            <Bar data={barData} options={chartOptions} />
          </div>
        </div>

        {/* Chart 2 */}
        <div className="p-5 rounded-xl bg-[#0B0E14] border border-neutral-800">
          <div className="text-xs font-mono text-neutral-400 mb-4 flex items-center justify-between">
            <span>DIURNAL FOCUS EFFICIENCY (%)</span>
            <GlowBadge status="active">
              {hasSessions ? `MEAN: ${summary.overall_focus}%` : "AWAITING SPRINTS"}
            </GlowBadge>
          </div>
          <div className="h-64">
            <Line data={lineData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Session History Table */}
      <div className="p-5 rounded-xl bg-[#0B0E14] border border-neutral-800">
        <div className="text-xs font-mono text-neutral-400 mb-4 uppercase tracking-wider flex items-center justify-between">
          <span>HISTORICAL STUDY SESSIONS & RECAP LOGS</span>
          <span className="text-[10px] text-neutral-500 font-normal">
            {sessionsHistory.length} Recorded
          </span>
        </div>

        {sessionsHistory.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-neutral-800 rounded-lg">
            <Clock className="w-8 h-8 text-neutral-600 mx-auto mb-2" />
            <div className="text-sm font-mono text-neutral-300 font-semibold">
              No Study Sprints Recorded Yet
            </div>
            <p className="text-xs font-mono text-neutral-500 max-w-sm mx-auto mt-1">
              Start your first session from the "Live Study Hub" tab. Your biometric focus scores and distraction logs will automatically be tracked here.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-neutral-800 text-neutral-500">
                  <th className="pb-3 font-normal">SESSION ID</th>
                  <th className="pb-3 font-normal">TIMESTAMP</th>
                  <th className="pb-3 font-normal">MODE</th>
                  <th className="pb-3 font-normal">DURATION</th>
                  <th className="pb-3 font-normal">FOCUS SCORE</th>
                  <th className="pb-3 font-normal">DISTRACTIONS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-800/60">
                {sessionsHistory.map((s) => (
                  <tr key={s.id} className="hover:bg-[#10141F] transition-colors">
                    <td className="py-3 text-cyan-400">{s.id}</td>
                    <td className="py-3 text-neutral-300">{s.date}</td>
                    <td className="py-3 text-neutral-400">{s.type}</td>
                    <td className="py-3 text-white font-bold">{s.duration}</td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                        {s.score}%
                      </span>
                    </td>
                    <td className="py-3 text-neutral-400">
                      {s.distractions === 0 ? (
                        <span className="text-emerald-400">0 (Clean)</span>
                      ) : (
                        <span className="text-amber-400">{s.distractions} alerts</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
