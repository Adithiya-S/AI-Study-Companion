"""
Vision & Phone Detection API Routes
Uses the original YOLOv8 phone detection from src/focus_tracker.py
"""

import base64
import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List

from src.focus_tracker import FocusTracker

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])

# Singleton instance of FocusTracker with YOLOv8 nano
_tracker_instance = None


def get_tracker() -> FocusTracker:
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = FocusTracker()
    return _tracker_instance


class FramePayload(BaseModel):
    image_base64: str  # Data URL or base64 string of camera frame


@router.get("/vision-status")
def get_vision_status():
    tracker = get_tracker()
    return {
        "yolo_available": tracker.phone_detection_enabled,
        "yolo_model": "yolov8n.pt" if tracker.phone_detection_enabled else None,
        "phone_class_id": tracker.PHONE_CLASS_ID,
        "confidence_threshold": tracker.PHONE_CONFIDENCE_THRESHOLD,
    }


@router.post("/detect-phone")
def detect_phone_frame(payload: FramePayload):
    """
    Direct YOLOv8 Phone Detection endpoint.
    Accepts base64 frame from webcam, decodes and passes to FocusTracker.detect_phone.
    Only triggers if an actual physical cell phone (COCO class 67) is present in the frame.
    """
    tracker = get_tracker()
    if not tracker.phone_detection_enabled:
        return {
            "phone_detected": False,
            "confidence": 0.0,
            "boxes": None,
            "note": "YOLO not loaded",
        }

    try:
        # Strip header if data URL format (e.g. data:image/jpeg;base64,...)
        b64_data = payload.image_base64
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]

        image_bytes = base64.b64decode(b64_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        phone_detected, confidence, boxes = tracker.detect_phone(frame)

        formatted_boxes = []
        if boxes:
            for b in boxes:
                formatted_boxes.append({
                    "x1": int(b[0]),
                    "y1": int(b[1]),
                    "x2": int(b[2]),
                    "y2": int(b[3]),
                    "conf": float(b[4]),
                    "type": str(b[5]),
                })

        if phone_detected:
            print(f"📱 [YOLO] Phone detected! Conf={confidence:.2f}, Boxes={len(formatted_boxes)}")

        return {
            "phone_detected": phone_detected,
            "confidence": round(confidence, 3),
            "boxes": formatted_boxes,
        }
    except Exception as e:
        print(f"❌ [VISION ERROR] Inference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")
