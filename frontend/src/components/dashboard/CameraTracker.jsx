import React, { useRef, useState, useEffect, useCallback } from "react";
import { Camera as CameraIcon, CameraOff, Eye } from "lucide-react";
import { GlowBadge } from "../ui/GlowBadge";
import { sounds } from "../../lib/audio";
import { apiUrl } from "../../lib/api";

export const CameraTracker = ({ onDistractionUpdate, onFocusUpdate, sensitivity = "medium" }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const faceMeshRef = useRef(null);
  const animationFrameRef = useRef(null);
  const distractionCountRef = useRef(0);
  const lastDistractionTimeRef = useRef(0);
  const detectedPhoneBoxRef = useRef(null);

  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [phoneModelReady, setPhoneModelReady] = useState(false);
  const [showMesh, setShowMesh] = useState(true);

  // Performance & Concurrency Refs
  const lastStateUpdateRef = useRef(0);
  const lastReportedStatusRef = useRef("");
  const isDetectingPhoneRef = useRef(false);
  const isProcessingMeshRef = useRef(false);
  const eyesClosedStartTimeRef = useRef(0);
  const localStreamRef = useRef(null);
  const backgroundIntervalRef = useRef(null);

  // Store callbacks and props in refs to prevent camera re-triggering on state updates
  const onDistractionUpdateRef = useRef(onDistractionUpdate);
  const onFocusUpdateRef = useRef(onFocusUpdate);
  const showMeshRef = useRef(true);
  const sensitivityRef = useRef(sensitivity);

  useEffect(() => {
    onDistractionUpdateRef.current = onDistractionUpdate;
  }, [onDistractionUpdate]);

  useEffect(() => {
    onFocusUpdateRef.current = onFocusUpdate;
  }, [onFocusUpdate]);

  useEffect(() => {
    showMeshRef.current = showMesh;
  }, [showMesh]);

  useEffect(() => {
    sensitivityRef.current = sensitivity;
  }, [sensitivity]);

  const [telemetry, setTelemetry] = useState({
    ear: 0.28,
    focusScore: 98,
    status: "STANDBY", // "STANDBY" | "FOCUSED" | "LOOKING_AWAY" | "EYES_CLOSED" | "PHONE_DETECTED" | "NO_FACE"
    fps: 30,
    gaze: "FORWARD",
  });

  const toggleCamera = () => {
    if (cameraEnabled) {
      // Turn camera off
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach((t) => t.stop());
        localStreamRef.current = null;
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
      if (backgroundIntervalRef.current) {
        clearInterval(backgroundIntervalRef.current);
        backgroundIntervalRef.current = null;
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      const canvas = canvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
      setCameraActive(false);
      setCameraEnabled(false);
      setTelemetry((prev) => ({ ...prev, status: "STANDBY" }));
    } else {
      // Turn camera on
      setCameraEnabled(true);
    }
  };

  // Euclidean distance between two 2D points
  const dist = (p1, p2) => {
    const dx = p1.x - p2.x;
    const dy = p1.y - p2.y;
    return Math.sqrt(dx * dx + dy * dy);
  };

  // Process Real Face Mesh Landmarks & Phone Detections
  const onResults = useCallback((results) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    const now = Date.now();
    const phoneBox = detectedPhoneBoxRef.current;
    const isPhoneVisible = phoneBox !== null;

    // Dynamic Sensitivity (from src/focus_tracker.py: Low, Medium, High)
    const sens = sensitivityRef.current || "medium";
    const yawLow = sens === "low" ? 0.22 : sens === "high" ? 0.38 : 0.31;
    const yawHigh = sens === "low" ? 0.78 : sens === "high" ? 0.62 : 0.69;
    const alertTimeout = sens === "low" ? 5000 : sens === "high" ? 2000 : 3500;

    // 1. Check if face was detected
    if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
      if (now - lastDistractionTimeRef.current > alertTimeout) {
        lastDistractionTimeRef.current = now;
        distractionCountRef.current += 1;
        sounds.playDistractionWarning();
        onDistractionUpdateRef.current && onDistractionUpdateRef.current(distractionCountRef.current);
      }

      const noFaceStatus = isPhoneVisible ? "PHONE_DETECTED" : "NO_FACE";
      if (noFaceStatus !== lastReportedStatusRef.current || now - lastStateUpdateRef.current > 400) {
        lastStateUpdateRef.current = now;
        lastReportedStatusRef.current = noFaceStatus;
        setTelemetry((prev) => ({
          ...prev,
          status: noFaceStatus,
          focusScore: Math.max(40, prev.focusScore - 1),
          gaze: isPhoneVisible ? "LOOKING AT PHONE" : "AWAY",
        }));
        onFocusUpdateRef.current && onFocusUpdateRef.current(50);
      }
      return;
    }

    const landmarks = results.multiFaceLandmarks[0];

    // 2. Real Eye Aspect Ratio (EAR) - uses 3 vertical landmark pairs including the center
    const p33 = landmarks[33];   // Left eye outer corner
    const p133 = landmarks[133]; // Left eye inner corner
    const p159 = landmarks[159]; // Left eye upper center
    const p145 = landmarks[145]; // Left eye lower center
    const p160 = landmarks[160];
    const p144 = landmarks[144];
    const p158 = landmarks[158];
    const p153 = landmarks[153];

    const leftH = dist(p33, p133);
    const leftV = (dist(p160, p144) + dist(p159, p145) * 2.0 + dist(p158, p153)) / 4.0;
    const leftEar = leftH > 0 ? leftV / leftH : 0.3;

    const p263 = landmarks[263]; // Right eye outer corner
    const p362 = landmarks[362]; // Right eye inner corner
    const p386 = landmarks[386]; // Right eye upper center
    const p374 = landmarks[374]; // Right eye lower center
    const p385 = landmarks[385];
    const p380 = landmarks[380];
    const p387 = landmarks[387];
    const p373 = landmarks[373];

    const rightH = dist(p263, p362);
    const rightV = (dist(p385, p380) + dist(p386, p374) * 2.0 + dist(p387, p373)) / 4.0;
    const rightEar = rightH > 0 ? rightV / rightH : 0.3;

    const avgEar = +((leftEar + rightEar) / 2.0).toFixed(2);

    // Track eye closed duration:
    // Blinking: < 0.22 for brief interval (< 2s) is normal and NOT a distraction.
    // Prolonged closure / drowsy: counts as a distraction ONLY when closed for > 2.0 seconds (2000ms).
    if (avgEar < 0.22) {
      if (!eyesClosedStartTimeRef.current) {
        eyesClosedStartTimeRef.current = now;
      }
    } else {
      eyesClosedStartTimeRef.current = 0;
    }
    const eyeClosedDurationMs = eyesClosedStartTimeRef.current > 0 ? now - eyesClosedStartTimeRef.current : 0;
    const isEyesClosed = eyeClosedDurationMs >= 2000;

    // 3. Head Yaw (Turning head left vs right)
    const nose = landmarks[1];
    const leftCheek = landmarks[234];
    const rightCheek = landmarks[454];
    const cheekSpan = Math.abs(rightCheek.x - leftCheek.x);
    const yawRatio = cheekSpan > 0 ? (nose.x - leftCheek.x) / cheekSpan : 0.5;

    // Classification Rules:
    let status = "FOCUSED";
    let gazeDir = "FORWARD";

    if (isPhoneVisible) {
      status = "PHONE_DETECTED";
      gazeDir = "LOOKING AT PHONE";
    } else if (isEyesClosed) {
      status = "EYES_CLOSED";
      gazeDir = "EYES CLOSED (>2s)";
    } else if (yawRatio < yawLow) {
      status = "LOOKING_AWAY";
      gazeDir = "LEFT";
    } else if (yawRatio > yawHigh) {
      status = "LOOKING_AWAY";
      gazeDir = "RIGHT";
    }

    // Distraction Alert Trigger
    if (status !== "FOCUSED") {
      if (now - lastDistractionTimeRef.current > alertTimeout) {
        lastDistractionTimeRef.current = now;
        distractionCountRef.current += 1;
        sounds.playDistractionWarning();
        onDistractionUpdateRef.current && onDistractionUpdateRef.current(distractionCountRef.current);
      }
    }

    // Dynamic Focus Score Calculation:
    // Under 7 distractions is evaluated as really good & highly focused (90-98%)
    const currentDistractions = distractionCountRef.current;
    const baseScore = currentDistractions < 7
      ? Math.max(90, Math.round(98 - currentDistractions * 1.2))
      : Math.max(45, Math.round(90 - (currentDistractions - 6) * 4));

    const score = status === "FOCUSED"
      ? baseScore
      : status === "PHONE_DETECTED"
      ? Math.max(40, baseScore - 20)
      : Math.max(50, baseScore - 15);

    const shouldUpdate =
      status !== lastReportedStatusRef.current ||
      now - lastStateUpdateRef.current > 350;

    if (shouldUpdate) {
      lastStateUpdateRef.current = now;
      lastReportedStatusRef.current = status;
      setTelemetry({
        ear: avgEar,
        focusScore: score,
        status,
        fps: 30,
        gaze: gazeDir,
      });
      onFocusUpdateRef.current && onFocusUpdateRef.current(score);
    }

    // 4. Draw Real Face Landmarks
    if (showMeshRef.current) {
      const isBad = status !== "FOCUSED";

      // Face Oval
      const faceOvalIndices = [
        10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365,
        379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93,
        234, 127, 162, 21, 54, 103, 67, 109, 10,
      ];

      ctx.strokeStyle = isBad ? "rgba(239, 68, 68, 0.8)" : "rgba(0, 242, 254, 0.45)";
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      faceOvalIndices.forEach((idx, i) => {
        const pt = landmarks[idx];
        if (pt) {
          const x = (1 - pt.x) * width; // Mirrored
          const y = pt.y * height;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
      });
      ctx.closePath();
      ctx.stroke();

      // Eye Outlines
      const leftEyeIndices = [33, 160, 158, 133, 153, 144, 33];
      const rightEyeIndices = [362, 385, 387, 263, 373, 380, 362];

      [leftEyeIndices, rightEyeIndices].forEach((indices) => {
        ctx.strokeStyle = isBad ? "#EF4444" : "#00F2FE";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        indices.forEach((idx, i) => {
          const pt = landmarks[idx];
          if (pt) {
            const x = (1 - pt.x) * width;
            const y = pt.y * height;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }
        });
        ctx.stroke();
      });

      // Iris Crosshairs (landmarks 468 & 473)
      const leftIris = landmarks[468] || landmarks[159];
      const rightIris = landmarks[473] || landmarks[386];

      [leftIris, rightIris].forEach((iris) => {
        if (iris) {
          const ix = (1 - iris.x) * width;
          const iy = iris.y * height;
          ctx.fillStyle = isBad ? "#EF4444" : "#10B981";
          ctx.beginPath();
          ctx.arc(ix, iy, 2.5, 0, Math.PI * 2);
          ctx.fill();

          ctx.strokeStyle = isBad ? "#EF4444" : "#00F2FE";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(ix - 6, iy);
          ctx.lineTo(ix + 6, iy);
          ctx.moveTo(ix, iy - 6);
          ctx.lineTo(ix, iy + 6);
          ctx.stroke();
        }
      });

      // 5. Draw Target Bounding Box around Real Detected Phone
      if (phoneBox) {
        const [bx, by, bw, bh] = phoneBox.bbox;
        const conf = Math.round(phoneBox.score * 100);
        const mirroredX = width - (bx + bw);

        ctx.strokeStyle = "#F59E0B";
        ctx.lineWidth = 2.5;
        ctx.strokeRect(mirroredX, by, bw, bh);

        ctx.fillStyle = "rgba(245, 158, 11, 0.9)";
        ctx.fillRect(mirroredX, Math.max(0, by - 24), Math.min(180, bw), 22);
        ctx.fillStyle = "#000000";
        ctx.font = "bold 11px JetBrains Mono, monospace";
        ctx.fillText(`📱 CELL PHONE (${conf}%)`, mirroredX + 6, Math.max(0, by - 24) + 15);
      }

      // HUD Corner Brackets
      ctx.strokeStyle = isBad ? "#EF4444" : "#00F2FE";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(12, 24);
      ctx.lineTo(12, 12);
      ctx.lineTo(24, 12);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(width - 24, 12);
      ctx.lineTo(width - 12, 12);
      ctx.lineTo(width - 12, 24);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(12, height - 24);
      ctx.lineTo(12, height - 12);
      ctx.lineTo(24, height - 12);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(width - 24, height - 12);
      ctx.lineTo(width - 12, height - 12);
      ctx.lineTo(width - 12, height - 24);
      ctx.stroke();
    }
  }, []);

  // Initialize MediaPipe FaceMesh & Camera Stream when cameraEnabled is true
  useEffect(() => {
    if (!cameraEnabled) return;

    let isMounted = true;
    let localStream = null;
    let phoneScanInterval = null;

    const waitForScripts = () => {
      return new Promise((resolve) => {
        const check = setInterval(() => {
          if (window.FaceMesh) {
            clearInterval(check);
            resolve(true);
          }
        }, 100);
        setTimeout(() => {
          clearInterval(check);
          resolve(!!window.FaceMesh);
        }, 10000);
      });
    };

    const setup = async () => {
      try {
        await waitForScripts();
        if (!window.FaceMesh) {
          console.warn("MediaPipe script not loaded.");
          return;
        }

        // 1. Initialize FaceMesh
        const faceMesh = new window.FaceMesh({
          locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`,
        });

        faceMesh.setOptions({
          maxNumFaces: 1,
          refineLandmarks: true,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        faceMesh.onResults(onResults);
        faceMeshRef.current = faceMesh;
        if (isMounted) setModelReady(true);
        if (isMounted) setPhoneModelReady(true);

        // 2. Request User Webcam
        localStream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 360, frameRate: { ideal: 30, max: 30 }, facingMode: "user" },
        });
        localStreamRef.current = localStream;

        if (videoRef.current && isMounted) {
          videoRef.current.srcObject = localStream;
          await videoRef.current.play();
          setCameraActive(true);

          // 3. 30 FPS Face Tracking Loop
          let lastProcessTime = 0;

          const process = async (timestamp) => {
            if (!isMounted) return;

            if (timestamp - lastProcessTime >= 33) {
              lastProcessTime = timestamp;

              if (
                videoRef.current &&
                videoRef.current.readyState >= 2 &&
                faceMeshRef.current &&
                !isProcessingMeshRef.current
              ) {
                isProcessingMeshRef.current = true;
                try {
                  await faceMeshRef.current.send({ image: videoRef.current });
                } catch (e) {
                  // Silently ignore frame drops
                } finally {
                  isProcessingMeshRef.current = false;
                }
              }
            }

            if (isMounted) {
              animationFrameRef.current = requestAnimationFrame(process);
            }
          };

          animationFrameRef.current = requestAnimationFrame(process);

          // 4. Background Tab Visibility Handler
          // When student switches browser tabs, browsers throttle requestAnimationFrame.
          // We run a background setInterval so face tracking & phone detection persist continuously!
          const handleVisibilityChange = () => {
            if (document.hidden) {
              if (!backgroundIntervalRef.current && faceMeshRef.current) {
                backgroundIntervalRef.current = setInterval(async () => {
                  if (
                    videoRef.current &&
                    videoRef.current.readyState >= 2 &&
                    faceMeshRef.current &&
                    !isProcessingMeshRef.current
                  ) {
                    isProcessingMeshRef.current = true;
                    try {
                      await faceMeshRef.current.send({ image: videoRef.current });
                    } catch (e) {
                      // Silently ignore
                    } finally {
                      isProcessingMeshRef.current = false;
                    }
                  }
                }, 250);
              }
            } else {
              if (backgroundIntervalRef.current) {
                clearInterval(backgroundIntervalRef.current);
                backgroundIntervalRef.current = null;
              }
            }
          };

          document.addEventListener("visibilitychange", handleVisibilityChange);

          // 5. Backend YOLO Phone Detector (Captures a small frame every 900ms)
          const offscreenCanvas = document.createElement("canvas");
          offscreenCanvas.width = 320;
          offscreenCanvas.height = 180;
          const offscreenCtx = offscreenCanvas.getContext("2d");

          phoneScanInterval = setInterval(async () => {
            if (
              !isMounted ||
              isDetectingPhoneRef.current ||
              !videoRef.current ||
              videoRef.current.readyState < 2
            ) {
              return;
            }

            isDetectingPhoneRef.current = true;
            try {
              offscreenCtx.drawImage(videoRef.current, 0, 0, 320, 180);
              const dataUrl = offscreenCanvas.toDataURL("image/jpeg", 0.6);

              const res = await fetch(apiUrl("/api/telemetry/detect-phone"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image_base64: dataUrl }),
              });

              if (res.ok) {
                const data = await res.json();
                if (data.phone_detected && data.boxes && data.boxes.length > 0) {
                  const b = data.boxes[0];
                  detectedPhoneBoxRef.current = {
                    bbox: [b.x1 * 2, b.y1 * 2, (b.x2 - b.x1) * 2, (b.y2 - b.y1) * 2],
                    score: data.confidence,
                  };
                } else {
                  detectedPhoneBoxRef.current = null;
                }
              }
            } catch (err) {
              // Ignore background scan error if backend busy
            } finally {
              isDetectingPhoneRef.current = false;
            }
          }, 900);
        }
      } catch (err) {
        console.warn("Webcam or model setup error:", err);
      }
    };

    setup();

    return () => {
      isMounted = false;
      if (phoneScanInterval) clearInterval(phoneScanInterval);
      if (backgroundIntervalRef.current) {
        clearInterval(backgroundIntervalRef.current);
        backgroundIntervalRef.current = null;
      }
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      if (localStream) {
        localStream.getTracks().forEach((t) => t.stop());
      }
    };
  }, [cameraEnabled, onResults]);

  const getStatusBadge = () => {
    if (!cameraEnabled) {
      return <GlowBadge status="idle">CAMERA OFF (STANDBY)</GlowBadge>;
    }
    switch (telemetry.status) {
      case "FOCUSED":
        return <GlowBadge status="active">REAL EYE TRACKING: FOCUSED</GlowBadge>;
      case "PHONE_DETECTED":
        return <GlowBadge status="warning">📱 LOOKING AT PHONE</GlowBadge>;
      case "LOOKING_AWAY":
        return <GlowBadge status="warning">LOOKING AWAY</GlowBadge>;
      case "EYES_CLOSED":
        return <GlowBadge status="danger">EYES CLOSED / DROWSY</GlowBadge>;
      case "NO_FACE":
        return <GlowBadge status="danger">NO FACE DETECTED</GlowBadge>;
      default:
        return <GlowBadge status="idle">INITIALIZING MEDIAPIPE...</GlowBadge>;
    }
  };

  return (
    <div className="rounded-xl border border-neutral-800 bg-[#0B0E14] p-5 flex flex-col justify-between relative overflow-hidden">
      {/* HUD Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-cyan-400" />
          <span className="font-mono text-xs font-bold text-white tracking-wider">
            MEDIAPIPE EYE TRACKING // 30 FPS
          </span>
        </div>

        <div className="flex items-center gap-2">
          {getStatusBadge()}
          <button
            onClick={toggleCamera}
            title={cameraEnabled ? "Turn camera OFF" : "Turn camera ON"}
            className={`text-[10px] font-mono px-2 py-1 rounded border transition-colors flex items-center gap-1 cursor-pointer ${
              cameraEnabled
                ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/40 font-bold"
                : "bg-neutral-800 text-neutral-400 border-neutral-700 hover:text-white"
            }`}
          >
            {cameraEnabled ? <CameraIcon className="w-3 h-3 text-emerald-400" /> : <CameraOff className="w-3 h-3 text-neutral-400" />}
            CAMERA {cameraEnabled ? "ON" : "OFF"}
          </button>
          <button
            onClick={() => setShowMesh(!showMesh)}
            title="Toggle Face Mesh Overlay"
            className={`text-[10px] font-mono px-2 py-1 rounded border transition-colors cursor-pointer ${
              showMesh
                ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/30 font-bold"
                : "bg-neutral-800 text-neutral-400 border-neutral-700"
            }`}
          >
            HUD {showMesh ? "ON" : "OFF"}
          </button>
        </div>
      </div>

      {/* Video & Canvas container */}
      <div className="relative w-full aspect-video bg-[#05060A] rounded-lg border border-neutral-800/80 overflow-hidden flex items-center justify-center">
        {/* Real Live Webcam Video */}
        <video
          ref={videoRef}
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover transform -scale-x-100"
        />

        {/* Real-time MediaPipe Landmark & Phone Detection Overlay */}
        <canvas
          ref={canvasRef}
          width={640}
          height={360}
          className="absolute inset-0 w-full h-full pointer-events-none z-10"
        />

        {!cameraEnabled ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-[#07090E]/95 z-20">
            <div className="w-12 h-12 rounded-full bg-[#10141F] border border-neutral-800 flex items-center justify-center mb-3 text-neutral-400 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
              <CameraOff className="w-6 h-6" />
            </div>
            <div className="text-xs font-mono text-white font-bold mb-1">
              CAMERA STANDBY // SENSORS OFF
            </div>
            <p className="text-[11px] text-neutral-400 max-w-xs mb-4 leading-relaxed font-sans">
              Camera is OFF by default. Turn on below or in the top right to start live Eye Aspect Ratio (EAR) & phone distraction detection.
            </p>
            <button
              onClick={toggleCamera}
              className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-bold text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <CameraIcon className="w-3.5 h-3.5" /> TURN CAMERA ON
            </button>
          </div>
        ) : !cameraActive ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-[#07090E]/95 z-20">
            <div className="w-7 h-7 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mb-3" />
            <div className="text-xs font-mono text-neutral-300 font-semibold mb-1">
              CONNECTING CAMERA & INITIALIZING AI...
            </div>
            <p className="text-[11px] text-neutral-500 max-w-xs">
              Please allow webcam access if prompted by your browser.
            </p>
          </div>
        ) : null}
      </div>

      {/* Readout Telemetry Footer */}
      <div className="grid grid-cols-4 gap-2 mt-3 pt-3 border-t border-neutral-800/80 font-mono text-xs text-center">
        <div className="p-2 rounded bg-[#07090D] border border-neutral-800/60">
          <div className="text-[10px] text-neutral-500">REAL EAR</div>
          <div className="text-cyan-400 font-bold mt-0.5">{telemetry.ear}</div>
        </div>
        <div className="p-2 rounded bg-[#07090D] border border-neutral-800/60">
          <div className="text-[10px] text-neutral-500">GAZE ORIENTATION</div>
          <div className="text-white font-bold mt-0.5 text-[11px]">{telemetry.gaze}</div>
        </div>
        <div className="p-2 rounded bg-[#07090D] border border-neutral-800/60">
          <div className="text-[10px] text-neutral-500">FOCUS SCORE</div>
          <div className="text-emerald-400 font-bold mt-0.5">{telemetry.focusScore}%</div>
        </div>
        <div className="p-2 rounded bg-[#07090D] border border-neutral-800/60">
          <div className="text-[10px] text-neutral-500">STREAM RATE</div>
          <div className="text-cyan-400 font-bold mt-0.5 text-[11px]">
            {cameraActive ? "30 FPS // ACTIVE" : "STANDBY (30 FPS)"}
          </div>
        </div>
      </div>
    </div>
  );
};
