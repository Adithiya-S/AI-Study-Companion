import React, { useState, useEffect, Suspense, lazy } from "react";
import { BackgroundGrid } from "./components/ui/BackgroundGrid";
import { Navbar } from "./components/landing/Navbar";
import { Hero } from "./components/landing/Hero";
import { FeaturesBento } from "./components/landing/FeaturesBento";
import { Footer } from "./components/landing/Footer";
import { LoginPage } from "./components/auth/LoginPage";
import { CookieConsentBanner } from "./components/ui/CookieConsentBanner";

// Lazy-load heavy dashboard and secondary legal pages to maximize initial page load speed
const DashboardLayout = lazy(() =>
  import("./components/dashboard/DashboardLayout").then((m) => ({ default: m.DashboardLayout }))
);
const PrivacyPolicy = lazy(() =>
  import("./components/legal/PrivacyPolicy").then((m) => ({ default: m.PrivacyPolicy }))
);
const TermsOfService = lazy(() =>
  import("./components/legal/TermsOfService").then((m) => ({ default: m.TermsOfService }))
);
const NotFoundPage = lazy(() =>
  import("./components/ui/NotFoundPage").then((m) => ({ default: m.NotFoundPage }))
);

// Cyber-engineering loading fallback for code-split components
const LoadingFallback = () => (
  <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#08090D] font-mono text-cyan-400 space-y-4">
    <div className="relative w-12 h-12 flex items-center justify-center">
      <div className="w-12 h-12 rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin" />
      <div className="absolute w-6 h-6 rounded-full border-2 border-emerald-500/20 border-b-emerald-400 animate-spin" style={{ animationDirection: "reverse", animationDuration: "1.2s" }} />
    </div>
    <div className="text-xs tracking-widest text-neutral-400 animate-pulse">
      INITIALIZING TELEMETRY PIPELINE...
    </div>
  </div>
);

export default function App() {
  const [currentView, setCurrentView] = useState("landing"); // "landing" | "auth" | "dashboard" | "privacy" | "terms" | "404"
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem("aura_user");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // Synchronize router state with browser URL Hash & PopState
  useEffect(() => {
    const handleHash = () => {
      const rawHash = window.location.hash.replace(/^#\/?/, "").toLowerCase();
      if (!rawHash || rawHash === "landing" || rawHash === "home") {
        setCurrentView("landing");
      } else if (rawHash === "auth" || rawHash === "login" || rawHash === "register") {
        setCurrentView("auth");
      } else if (rawHash === "dashboard" || rawHash === "workspace") {
        const saved = localStorage.getItem("aura_user");
        if (saved) {
          setCurrentView("dashboard");
        } else {
          setCurrentView("auth");
        }
      } else if (rawHash === "privacy") {
        setCurrentView("privacy");
      } else if (rawHash === "terms") {
        setCurrentView("terms");
      } else if (rawHash === "404") {
        setCurrentView("404");
      } else {
        // Unknown hash route triggers 404 page
        setCurrentView("404");
      }
    };

    handleHash();
    window.addEventListener("hashchange", handleHash);
    return () => window.removeEventListener("hashchange", handleHash);
  }, []);

  const navigateTo = (view) => {
    setCurrentView(view);
    const hash = view === "landing" ? "" : `#${view}`;
    if (window.location.hash !== hash) {
      window.history.pushState(null, "", hash || window.location.pathname);
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleOpenDashboard = () => {
    if (currentUser) {
      navigateTo("dashboard");
    } else {
      navigateTo("auth");
    }
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    try {
      localStorage.setItem("aura_user", JSON.stringify(user));
    } catch (e) {
      console.warn("Failed saving aura_user", e);
    }
    navigateTo("dashboard");
  };

  const handleSignOut = () => {
    localStorage.removeItem("aura_auth_token");
    localStorage.removeItem("aura_user");
    setCurrentUser(null);
    navigateTo("landing");
  };

  return (
    <div className="min-h-screen bg-[#08090D] text-neutral-200">
      <Suspense fallback={<LoadingFallback />}>
        {/* 1. LANDING PAGE VIEW */}
        {currentView === "landing" && (
          <BackgroundGrid variant="dots">
            <Navbar
              onOpenAuth={() => navigateTo("auth")}
              onOpenDashboard={handleOpenDashboard}
            />
            <main>
              <Hero
                onOpenAuth={() => navigateTo("auth")}
                onOpenDashboard={handleOpenDashboard}
              />
              <FeaturesBento onOpenDashboard={handleOpenDashboard} />
            </main>
            <Footer
              onOpenAuth={() => navigateTo("auth")}
              onOpenDashboard={handleOpenDashboard}
              onOpenPrivacy={() => navigateTo("privacy")}
              onOpenTerms={() => navigateTo("terms")}
            />
          </BackgroundGrid>
        )}

        {/* 2. AUTHENTICATION / LOGIN VIEW */}
        {currentView === "auth" && (
          <LoginPage
            onLoginSuccess={handleLoginSuccess}
            onBackToLanding={() => navigateTo("landing")}
            onOpenTerms={() => navigateTo("terms")}
            onOpenPrivacy={() => navigateTo("privacy")}
          />
        )}

        {/* 3. PERSONAL STUDY DASHBOARD VIEW */}
        {currentView === "dashboard" && (
          <DashboardLayout user={currentUser} onSignOut={handleSignOut} />
        )}

        {/* 4. PRIVACY POLICY VIEW */}
        {currentView === "privacy" && (
          <PrivacyPolicy onBack={() => navigateTo("landing")} />
        )}

        {/* 5. TERMS OF SERVICE VIEW */}
        {currentView === "terms" && (
          <TermsOfService onBack={() => navigateTo("landing")} />
        )}

        {/* 6. CUSTOM 404 NOT FOUND VIEW */}
        {currentView === "404" && (
          <NotFoundPage
            onBackToLanding={() => navigateTo("landing")}
            onOpenDashboard={() => navigateTo("dashboard")}
          />
        )}
      </Suspense>

      {/* Global Cookie Consent Banner */}
      <CookieConsentBanner onOpenPrivacy={() => navigateTo("privacy")} />
    </div>
  );
}
