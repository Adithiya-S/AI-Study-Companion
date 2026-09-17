import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Eye, Shield, Lock, Mail, ArrowRight, ArrowLeft, CheckCircle2, Terminal, ExternalLink, AlertCircle } from "lucide-react";
import { BorderBeam } from "../ui/BorderBeam";
import { MagneticButton } from "../ui/MagneticButton";
import { GlowBadge } from "../ui/GlowBadge";

const GOOGLE_CLIENT_ID = "262576481074-0qemddi96lt1d3buupbreoump4oj4f2e.apps.googleusercontent.com";

export const LoginPage = ({ onLoginSuccess, onBackToLanding, onOpenTerms, onOpenPrivacy }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [googleLoaded, setGoogleLoaded] = useState(false);

  // Initialize Google Identity Services (GIS)
  useEffect(() => {
    const setupGoogleGSI = () => {
      if (window.google?.accounts?.id) {
        try {
          window.google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleCredentialResponse,
            auto_select: false,
          });

          const container = document.getElementById("google-signin-target");
          if (container) {
            container.innerHTML = "";
            window.google.accounts.id.renderButton(container, {
              theme: "filled_black",
              size: "large",
              text: "continue_with",
              shape: "rectangular",
              width: container.offsetWidth || 340,
            });
            setGoogleLoaded(true);
          }
        } catch (e) {
          console.warn("Google GSI setup error:", e);
        }
      }
    };

    if (window.google?.accounts?.id) {
      setupGoogleGSI();
    } else {
      const timer = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(timer);
          setupGoogleGSI();
        }
      }, 300);
      return () => clearInterval(timer);
    }
  }, [isSignUp]);

  const handleGoogleCredentialResponse = async (response) => {
    if (!response?.credential) return;
    setIsLoading(true);
    setErrorMessage("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential: response.credential }),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.token) {
          localStorage.setItem("aura_auth_token", data.token);
        }
        setIsLoading(false);
        onLoginSuccess(data.user);
        return;
      } else {
        const err = await res.json().catch(() => ({}));
        setErrorMessage(err.detail || "Google authentication failed on server.");
        setIsLoading(false);
        return;
      }
    } catch (err) {
      console.warn("Error communicating with /api/auth/google:", err);
      setErrorMessage("Could not connect to Google authentication service.");
      setIsLoading(false);
    }
  };

  const handleManualGoogleClick = () => {
    if (window.google?.accounts?.id) {
      window.google.accounts.id.prompt();
    } else {
      setErrorMessage("Google Sign-In SDK is loading, please try again in a moment.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");

    if (isSignUp && !agreedToTerms) {
      setErrorMessage("You must accept the Terms & Conditions and Privacy Policy to register.");
      return;
    }

    setIsLoading(true);

    try {
      const endpoint = isSignUp ? "http://127.0.0.1:8000/api/auth/register" : "http://127.0.0.1:8000/api/auth/login";
      const payload = isSignUp ? { name, email, password } : { email, password };

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.token) {
          localStorage.setItem("aura_auth_token", data.token);
        }
        setIsLoading(false);
        onLoginSuccess(data.user);
        return;
      } else {
        const errData = await res.json().catch(() => ({}));
        setErrorMessage(errData.detail || (isSignUp ? "Registration failed. Email may already be in use." : "Invalid email or password."));
        setIsLoading(false);
        return;
      }
    } catch (err) {
      console.error("Backend authentication API unreachable:", err);
      setErrorMessage("Unable to connect to the authentication server. Please ensure the backend is running.");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6 relative bg-[#08090D] engineering-grid">
      {/* Top back button */}
      <div className="absolute top-6 left-6">
        <button
          onClick={onBackToLanding}
          className="flex items-center gap-2 text-xs font-mono text-neutral-400 hover:text-white px-3 py-1.5 rounded-lg border border-neutral-800 bg-[#0C0E14] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> RETURN TO LANDING
        </button>
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md my-8"
      >
        <div className="relative rounded-2xl bg-[#0D1017] border border-[#1E2433] p-8 shadow-2xl">
          <BorderBeam size={220} duration={8} colorFrom="#00F2FE" colorTo="#10B981" />

          {/* Header */}
          <div className="text-center space-y-2 mb-6">
            <div className="inline-flex w-10 h-10 rounded-xl bg-[#131824] border border-cyan-500/40 items-center justify-center mb-1 shadow-[0_0_15px_rgba(0,242,254,0.2)]">
              <Eye className="w-5 h-5 text-cyan-400" />
            </div>
            <h2 className="text-2xl font-bold text-white font-sans tracking-tight">
              {isSignUp ? "INITIALIZE OPERATOR ID" : "AUTHENTICATE TELEMETRY"}
            </h2>
            <p className="text-xs font-mono text-neutral-400">
              {isSignUp
                ? "Register a verified study node with legal compliance"
                : "Sign in with Google or your email credentials"}
            </p>
          </div>

          {errorMessage && (
            <div className="mb-5 p-3 rounded-lg bg-red-950/40 border border-red-500/40 flex items-center gap-2 text-red-400 text-xs font-mono">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Single Unified Google OAuth Button */}
          <div className="space-y-3 mb-6">
            <div
              id="google-signin-target"
              className={`w-full flex justify-center min-h-[40px] overflow-hidden rounded-lg ${
                !googleLoaded ? "hidden" : ""
              }`}
            ></div>

            {!googleLoaded && (
              <button
                type="button"
                onClick={handleManualGoogleClick}
                disabled={isLoading}
                className="w-full py-2.5 px-4 rounded-lg bg-[#121622] hover:bg-[#1A2030] text-neutral-200 border border-neutral-700 hover:border-neutral-500 font-mono text-xs tracking-wider flex items-center justify-center gap-2.5 transition-colors cursor-pointer"
              >
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
                <span>CONTINUE WITH GOOGLE</span>
              </button>
            )}
          </div>

          <div className="relative my-5 text-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-neutral-800"></div>
            </div>
            <span className="relative px-3 bg-[#0D1017] text-[10px] font-mono text-neutral-500 tracking-wider">
              OR WITH EMAIL CREDENTIALS
            </span>
          </div>

          {/* Manual Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignUp && (
              <div>
                <label className="block text-xs font-mono text-neutral-400 mb-1.5">OPERATOR NAME</label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Alex Chen"
                    className="w-full px-3.5 py-2.5 rounded-lg bg-[#080A0F] border border-neutral-800 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono transition-colors"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-mono text-neutral-400 mb-1.5">EMAIL ADDRESS</label>
              <div className="relative">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="student@university.edu"
                  className="w-full px-3.5 py-2.5 rounded-lg bg-[#080A0F] border border-neutral-800 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-neutral-400 mb-1.5">SECURITY KEY / PASSWORD</label>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3.5 py-2.5 rounded-lg bg-[#080A0F] border border-neutral-800 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono transition-colors"
                />
              </div>
            </div>

            {/* Terms & Conditions Checkbox (when creating account) */}
            {isSignUp && (
              <div className="pt-2 pb-1">
                <label className="flex items-start gap-2.5 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    id="terms-checkbox"
                    checked={agreedToTerms}
                    onChange={(e) => setAgreedToTerms(e.target.checked)}
                    className="mt-1 w-4 h-4 rounded border-neutral-700 bg-[#080A0F] text-cyan-500 focus:ring-0 focus:ring-offset-0 cursor-pointer accent-cyan-400"
                  />
                  <span className="text-xs text-neutral-400 leading-relaxed font-sans">
                    I have read and agree to the{" "}
                    <button
                      type="button"
                      onClick={onOpenTerms}
                      className="text-cyan-400 hover:underline font-mono inline-flex items-center gap-0.5 cursor-pointer"
                    >
                      Terms & Conditions <ExternalLink className="w-2.5 h-2.5 inline" />
                    </button>{" "}
                    and acknowledge the{" "}
                    <button
                      type="button"
                      onClick={onOpenPrivacy}
                      className="text-cyan-400 hover:underline font-mono inline-flex items-center gap-0.5 cursor-pointer"
                    >
                      Privacy Policy <ExternalLink className="w-2.5 h-2.5 inline" />
                    </button>.
                  </span>
                </label>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || (isSignUp && !agreedToTerms)}
              className={`w-full mt-2 py-3 rounded-lg font-mono text-xs tracking-wider font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                isSignUp && !agreedToTerms
                  ? "bg-neutral-800 text-neutral-500 border border-neutral-800 cursor-not-allowed"
                  : "bg-[#141A26] hover:bg-[#1A2233] text-white border border-neutral-700 hover:border-cyan-500/50"
              }`}
            >
              {isLoading ? (
                <span>INITIALIZING NODE...</span>
              ) : isSignUp ? (
                <span>CREATE WORKSPACE</span>
              ) : (
                <span>SIGN IN TO WORKSPACE</span>
              )}
            </button>
          </form>

          {/* Toggle between login and sign up */}
          <div className="mt-6 pt-4 border-t border-neutral-800/80 text-center">
            <button
              onClick={() => {
                setIsSignUp(!isSignUp);
                setErrorMessage("");
              }}
              className="text-xs font-mono text-neutral-400 hover:text-cyan-400 transition-colors cursor-pointer"
            >
              {isSignUp
                ? "Already have an operator node? Sign In"
                : "New student or developer? Register Workspace"}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
