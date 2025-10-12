"""
Focus Tracker Module - Eye tracking using MediaPipe and OpenCV
Compatible with Python 3.8-3.12
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable

# Try to import YOLO for phone detection
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics not installed. Phone detection will be disabled.")

class FocusTracker:
    """Advanced focus tracking using MediaPipe face mesh and eye detection."""
    
    def __init__(self):
        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Face mesh model
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Hand detection setup (for detecting phone usage)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hand_detection_enabled = True
        
        # YOLO phone detection setup
        self.phone_detection_enabled = False
        self.yolo_model = None
        if YOLO_AVAILABLE:
            try:
                # Load YOLOv8 nano model (lightweight and fast)
                self.yolo_model = YOLO('yolov8n.pt')
                self.phone_detection_enabled = True
                print("Phone detection enabled (YOLOv8)")
            except Exception as e:
                print(f"Warning: Could not load YOLO model: {e}")
                self.phone_detection_enabled = False
        
        # Phone detection parameters
        self.PHONE_CLASS_ID = 67  # COCO dataset class ID for cell phone
        self.PHONE_CONFIDENCE_THRESHOLD = 0.25  # Lowered threshold for partial visibility
        self.PHONE_PENALTY = 0.3  # Reduce focus score by 30% when phone detected
        
        # Hand detection to infer phone usage (people often hold phones near face)
        # Detecting hands in specific positions can indicate phone usage
        self.HAND_NEAR_FACE_PENALTY = 0.15  # Additional penalty if hands detected near face area
        
        # Camera
        self.camera = None
        self.camera_index = 0
        
        # Eye tracking parameters - SIMPLIFIED: Focus on head pose only
        self.FOCUS_THRESHOLD = 0.5  # Overall focus threshold
        self.DISTRACTION_TIME_LIMIT = 3.0  # Seconds before alerting
        
        # Head pose thresholds (degrees) - Main focus detection method
        self.HEAD_PITCH_THRESHOLD = 30  # Up/down head tilt limit (increased)
        self.HEAD_YAW_THRESHOLD = 45    # Left/right head turn limit (increased for natural movement)
        
        # Eye aspect ratio thresholds (calibrated to your camera)
        self.EYE_OPEN_THRESHOLD = 3.5    # Eyes clearly open if EAR < 3.5
        self.EYE_SQUINT_THRESHOLD = 5.0  # Eyes squinting if EAR < 5.0
        self.EYE_CLOSED_THRESHOLD = 6.0  # Eyes closed if EAR >= 6.0
        
        # State tracking
        self.is_tracking = False
        self.last_focus_time = time.time()
        self.current_focus_score = 0.0
        self.distraction_start_time = None
        
        # Eye landmarks (MediaPipe face mesh indices) - 6 key points for EAR calculation
        # Format: [outer_corner, top1, top2, inner_corner, bottom2, bottom1]
        self.LEFT_EYE = [33, 160, 159, 133, 145, 144]   # Left eye 6-point contour
        self.RIGHT_EYE = [362, 387, 386, 263, 374, 373]  # Right eye 6-point contour
        
        # Gaze direction landmarks
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
        # Session data
        self.session_start_time = None
        self.focus_events = []
        self.distraction_count = 0
        
        # Display settings
        self.show_outline = True  # Show face/eye tracking outline by default
        
        # Callbacks
        self.distraction_callback = None
        
    def set_sensitivity(self, sensitivity: str):
        """
        Adjust focus detection sensitivity based on head pose angles.
        
        Args:
            sensitivity: "low", "medium", or "high"
        """
        if sensitivity == "low":
            # More lenient - allows more head movement
            self.HEAD_PITCH_THRESHOLD = 40  # Very relaxed up/down movement
            self.HEAD_YAW_THRESHOLD = 55    # Very relaxed left/right movement
            self.DISTRACTION_TIME_LIMIT = 5.0
        elif sensitivity == "medium":
            # Balanced - natural studying posture with comfortable movement
            self.HEAD_PITCH_THRESHOLD = 30  # Comfortable up/down tilt
            self.HEAD_YAW_THRESHOLD = 45    # Comfortable left/right turn
            self.DISTRACTION_TIME_LIMIT = 3.0
        elif sensitivity == "high":
            # Strict - requires more direct attention
            self.HEAD_PITCH_THRESHOLD = 20  # Limited up/down movement
            self.HEAD_YAW_THRESHOLD = 30    # Limited left/right turn
            self.DISTRACTION_TIME_LIMIT = 2.0
        
        print(f"Focus sensitivity set to: {sensitivity}")
        print(f"  Pitch threshold: ±{self.HEAD_PITCH_THRESHOLD}°")
        print(f"  Yaw threshold: ±{self.HEAD_YAW_THRESHOLD}°")
        print(f"  Distraction time limit: {self.DISTRACTION_TIME_LIMIT}s")
        
    def set_show_outline(self, show: bool):
        """
        Enable or disable the face/eye tracking outline visualization.
        
        Args:
            show: True to show outline, False to hide
        """
        self.show_outline = show
        print(f"Face tracking outline: {'enabled' if show else 'disabled'}")
        
    def set_callbacks(self, distraction_callback: Optional[Callable] = None):
        """Set callback functions for events."""
        self.distraction_callback = distraction_callback
        
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """Initialize camera for face tracking."""
        try:
            if self.camera is not None:
                self.camera.release()
                
            self.camera = cv2.VideoCapture(camera_index)
            self.camera_index = camera_index
            
            if not self.camera.isOpened():
                print(f"Error: Could not open camera {camera_index}")
                return False
                
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"Camera {camera_index} initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
            
    def start_tracking(self):
        """Start focus tracking session."""
        self.is_tracking = True
        self.session_start_time = time.time()
        self.focus_events.clear()
        self.distraction_count = 0
        self.last_focus_time = time.time()
        print("Focus tracking started")
        
    def stop_tracking(self):
        """Stop focus tracking session."""
        self.is_tracking = False
        print("Focus tracking stopped")
        
    def calculate_ear(self, eye_landmarks) -> float:
        """Calculate Eye Aspect Ratio."""
        try:
            if len(eye_landmarks) < 6:
                return 0.0
                
            # Vertical distances
            A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
            B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
            
            # Horizontal distance  
            C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
            
            # Prevent division by zero
            if A + B == 0:
                return 0.0
            
            # EAR calculation - CORRECTED FORMULA
            # EAR = horizontal / vertical (higher when eyes open, lower when closed)
            ear = (2.0 * C) / (A + B)
            return ear
            
        except (IndexError, ZeroDivisionError, Exception) as e:
            return 0.0
            
    def extract_eye_landmarks(self, landmarks, eye_indices) -> np.ndarray:
        """Extract eye landmarks from face mesh (all 6 points for EAR)."""
        eye_points = []
        for idx in eye_indices:  # Use all 6 points
            point = landmarks.landmark[idx]
            eye_points.append([point.x, point.y])
        return np.array(eye_points)
        
    def estimate_gaze_direction(self, landmarks, frame_shape) -> str:
        """Estimate gaze direction (left, center, right)."""
        try:
            # Get iris centers
            left_iris_center = np.mean([[landmarks.landmark[i].x, landmarks.landmark[i].y] 
                                       for i in self.LEFT_IRIS], axis=0)
            right_iris_center = np.mean([[landmarks.landmark[i].x, landmarks.landmark[i].y] 
                                        for i in self.RIGHT_IRIS], axis=0)
            
            # Get eye corners for reference
            left_corner = np.array([landmarks.landmark[33].x, landmarks.landmark[33].y])
            right_corner = np.array([landmarks.landmark[263].x, landmarks.landmark[263].y])
            
            # Get eye outer corners
            left_outer = np.array([landmarks.landmark[133].x, landmarks.landmark[133].y])
            right_outer = np.array([landmarks.landmark[362].x, landmarks.landmark[362].y])
            
            # Calculate eye widths
            left_eye_width = np.linalg.norm(left_corner - left_outer)
            right_eye_width = np.linalg.norm(right_corner - right_outer)
            
            # Prevent division by zero
            if left_eye_width == 0 or right_eye_width == 0:
                return "center"
            
            # Calculate relative positions
            left_ratio = (left_iris_center[0] - left_outer[0]) / left_eye_width
            right_ratio = (right_iris_center[0] - right_outer[0]) / right_eye_width
            
            avg_ratio = (left_ratio + right_ratio) / 2
            
            if avg_ratio < 0.35:
                return "left"
            elif avg_ratio > 0.65:
                return "right"
            else:
                return "center"
                
        except (IndexError, AttributeError, ZeroDivisionError, Exception) as e:
            return "center"
            
    def estimate_head_pose(self, landmarks, frame_shape) -> Tuple[float, float, float]:
        """Estimate head pose (pitch, yaw, roll)."""
        try:
            h, w = frame_shape[:2]
            
            # 3D model points
            model_points = np.array([
                (0.0, 0.0, 0.0),             # Nose tip
                (0.0, -330.0, -65.0),        # Chin
                (-225.0, 170.0, -135.0),     # Left eye left corner
                (225.0, 170.0, -135.0),      # Right eye right corner
                (-150.0, -150.0, -125.0),    # Left mouth corner
                (150.0, -150.0, -125.0)      # Right mouth corner
            ])
            
            # 2D image points (using correct face mesh indices)
            image_points = np.array([
                (landmarks.landmark[1].x * w, landmarks.landmark[1].y * h),     # Nose tip
                (landmarks.landmark[152].x * w, landmarks.landmark[152].y * h), # Chin
                (landmarks.landmark[33].x * w, landmarks.landmark[33].y * h),   # Left eye corner
                (landmarks.landmark[263].x * w, landmarks.landmark[263].y * h), # Right eye corner
                (landmarks.landmark[61].x * w, landmarks.landmark[61].y * h),   # Left mouth corner
                (landmarks.landmark[291].x * w, landmarks.landmark[291].y * h)  # Right mouth corner
            ], dtype=np.float32)
            
            # Camera matrix
            focal_length = w
            center = (w/2, h/2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype=np.float32)
            
            # Distortion coefficients
            dist_coeffs = np.zeros((4,1))
            
            # Solve PnP
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if success:
                # Convert rotation vector to rotation matrix
                rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
                
                # Extract angles
                sy = np.sqrt(rotation_matrix[0,0] * rotation_matrix[0,0] +  rotation_matrix[1,0] * rotation_matrix[1,0])
                singular = sy < 1e-6
                
                if not singular:
                    pitch = np.arctan2(-rotation_matrix[2,1], rotation_matrix[2,2])
                    yaw = np.arctan2(-rotation_matrix[2,0], sy)
                    roll = np.arctan2(rotation_matrix[1,0], rotation_matrix[0,0])
                else:
                    pitch = np.arctan2(-rotation_matrix[2,1], rotation_matrix[2,2])
                    yaw = np.arctan2(-rotation_matrix[2,0], sy)
                    roll = 0
                    
                # Convert to degrees
                pitch = np.degrees(pitch)
                yaw = np.degrees(yaw)
                roll = np.degrees(roll)
                
                return pitch, yaw, roll
            
        except Exception as e:
            print(f"Head pose estimation error: {e}")
            
        return 0.0, 0.0, 0.0
    
    def detect_phone(self, frame) -> Tuple[bool, float, Optional[List]]:
        """
        Detect if a phone is present in the frame using YOLO.
        Also detects hands near the face area which may indicate phone usage.
        
        Returns:
            Tuple of (phone_detected, confidence, bounding_boxes)
            - phone_detected: True if phone is detected with sufficient confidence OR hands near face
            - confidence: Highest confidence score for phone detection
            - bounding_boxes: List of bounding boxes for detected phones and hands [(x1, y1, x2, y2, conf, type), ...]
        """
        if not self.phone_detection_enabled or self.yolo_model is None:
            return False, 0.0, None
        
        try:
            # Run YOLO inference
            results = self.yolo_model(frame, verbose=False)
            
            phone_detected = False
            max_confidence = 0.0
            detection_boxes = []
            
            frame_height, frame_width = frame.shape[:2]
            face_area_top = int(frame_height * 0.1)  # Top 10% to 60% is typical face area
            face_area_bottom = int(frame_height * 0.6)
            
            # Process detections
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Detect cell phones (class 67)
                    if class_id == self.PHONE_CLASS_ID and confidence >= self.PHONE_CONFIDENCE_THRESHOLD:
                        phone_detected = True
                        max_confidence = max(max_confidence, confidence)
                        
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        detection_boxes.append((int(x1), int(y1), int(x2), int(y2), confidence, 'phone'))
                    
                    # Detect hands near face (class 0 is person, but we'll look for specific hand gestures)
                    # Note: COCO doesn't have a dedicated "hand" class, but we can use heuristics
                    # If we detect objects in the upper portion of frame with medium confidence,
                    # it might indicate phone usage
                    
            # Additional heuristic: Check for small objects in face area that might be partially visible phones
            # This helps catch phones that are partially obscured
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Look for objects in the face/upper body area with lower confidence
                    # These could be partially visible phones
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    box_center_y = (y1 + y2) / 2
                    
                    # Check if object is in face area
                    if face_area_top < box_center_y < face_area_bottom:
                        # Check for cell phone with even lower confidence (partially visible)
                        if class_id == self.PHONE_CLASS_ID and confidence >= 0.15:
                            if not phone_detected:  # Only add if not already detected with higher confidence
                                phone_detected = True
                                max_confidence = max(max_confidence, confidence)
                                detection_boxes.append((int(x1), int(y1), int(x2), int(y2), confidence, 'phone_partial'))
            
            return phone_detected, max_confidence, detection_boxes if detection_boxes else None
            
        except Exception as e:
            print(f"Phone detection error: {e}")
            return False, 0.0, None
    
    def detect_hands_near_face(self, frame, face_landmarks=None) -> Tuple[bool, int, Optional[List]]:
        """
        Detect hands near the face area using MediaPipe hands.
        This can indicate phone usage even when phone is partially obscured.
        
        Returns:
            Tuple of (hands_near_face, hand_count, hand_boxes)
        """
        if not self.hand_detection_enabled:
            return False, 0, None
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_results = self.hands.process(rgb_frame)
            
            if not hand_results.multi_hand_landmarks:
                return False, 0, None
            
            h, w = frame.shape[:2]
            hands_near_face = False
            hand_count = len(hand_results.multi_hand_landmarks)
            hand_boxes = []
            
            # Define face area (upper 60% of frame typically contains face)
            face_area_top = int(h * 0.1)
            face_area_bottom = int(h * 0.6)
            
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Get hand bounding box
                x_coords = [lm.x * w for lm in hand_landmarks.landmark]
                y_coords = [lm.y * h for lm in hand_landmarks.landmark]
                
                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))
                
                hand_center_y = (y_min + y_max) / 2
                
                # Check if hand is in face area
                if face_area_top < hand_center_y < face_area_bottom:
                    hands_near_face = True
                    hand_boxes.append((x_min, y_min, x_max, y_max, 1.0, 'hand_near_face'))
                else:
                    hand_boxes.append((x_min, y_min, x_max, y_max, 1.0, 'hand'))
            
            return hands_near_face, hand_count, hand_boxes if hand_boxes else None
            
        except Exception as e:
            print(f"Hand detection error: {e}")
            return False, 0, None
        
    def analyze_focus_level(self, frame) -> Dict:
        """Analyze focus level from camera frame."""
        if frame is None:
            return {
                "focus_score": 0.0, 
                "is_focused": False, 
                "ear": 0.0,
                "gaze": "unknown",
                "head_pose": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
                "phone_detected": False,
                "phone_confidence": 0.0,
                "hands_near_face": False,
                "details": "No frame"
            }
        
        # Detect phone first (if enabled)
        phone_detected, phone_confidence, phone_boxes = self.detect_phone(frame)
        
        # Detect hands near face (additional signal for phone usage)
        hands_near_face, hand_count, hand_boxes = self.detect_hands_near_face(frame)
        
        # Combine detection boxes for visualization
        all_detection_boxes = []
        if phone_boxes:
            all_detection_boxes.extend(phone_boxes)
        if hand_boxes:
            all_detection_boxes.extend(hand_boxes)
            
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return {
                "focus_score": 0.0, 
                "is_focused": False, 
                "ear": 0.0,
                "gaze": "unknown",
                "head_pose": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
                "phone_detected": phone_detected,
                "phone_confidence": phone_confidence,
                "phone_boxes": all_detection_boxes,
                "hands_near_face": hands_near_face,
                "hand_count": hand_count,
                "details": "No face detected"
            }
            
        landmarks = results.multi_face_landmarks[0]
        h, w = frame.shape[:2]
        
        # Calculate metrics
        left_eye = self.extract_eye_landmarks(landmarks, self.LEFT_EYE)
        right_eye = self.extract_eye_landmarks(landmarks, self.RIGHT_EYE)
        
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        gaze_direction = self.estimate_gaze_direction(landmarks, frame.shape)
        pitch, yaw, roll = self.estimate_head_pose(landmarks, frame.shape)
        
        # SIMPLIFIED FOCUS ALGORITHM - Based primarily on head pose
        # User is focused if head is facing generally toward the screen
        
        # 1. Eyes open check (20% weight) - Give full points if eyes are reasonably open
        # Your calibrated EAR values: open ~2, closed ~8
        # Lower EAR = more open, Higher EAR = more closed
        if avg_ear < self.EYE_OPEN_THRESHOLD:  # Eyes clearly open (EAR < 3.5)
            eye_score = 0.2
        elif avg_ear < self.EYE_SQUINT_THRESHOLD:  # Eyes squinting (EAR 3.5-5.0)
            eye_score = 0.1
        elif avg_ear < self.EYE_CLOSED_THRESHOLD:  # Eyes partially closed (EAR 5.0-6.0)
            eye_score = 0.05
        else:
            eye_score = 0.0  # Eyes closed (EAR >= 6.0)
        
        # 2. Head Pitch - Up/Down angle (40% weight)
        # Give FULL points within a comfortable range, then gradually decrease
        abs_pitch = abs(pitch)
        if abs_pitch <= 15:  # Within 15° - full points (natural range)
            pitch_score = 0.4
        elif abs_pitch <= self.HEAD_PITCH_THRESHOLD:
            # Gradually decrease from 15° to threshold
            remaining = self.HEAD_PITCH_THRESHOLD - 15
            pitch_score = 0.4 * (1.0 - (abs_pitch - 15) / remaining) if remaining > 0 else 0.0
        else:
            pitch_score = 0.0
        
        # 3. Head Yaw - Left/Right angle (40% weight)
        # Give FULL points within a comfortable range, then gradually decrease
        abs_yaw = abs(yaw)
        if abs_yaw <= 20:  # Within 20° - full points (natural range)
            yaw_score = 0.4
        elif abs_yaw <= self.HEAD_YAW_THRESHOLD:
            # Gradually decrease from 20° to threshold
            remaining = self.HEAD_YAW_THRESHOLD - 20
            yaw_score = 0.4 * (1.0 - (abs_yaw - 20) / remaining) if remaining > 0 else 0.0
        else:
            yaw_score = 0.0
        
        # Total focus score (before phone penalty)
        base_focus_score = eye_score + pitch_score + yaw_score
        
        # 4. Phone detection penalty
        # If a phone is detected, reduce the focus score significantly
        phone_penalty_amount = 0.0
        if phone_detected:
            phone_penalty_amount = base_focus_score * self.PHONE_PENALTY
        
        # 5. Hand near face penalty (additional indicator of phone usage)
        # If hands are detected near face area, apply additional penalty
        hand_penalty_amount = 0.0
        if hands_near_face:
            hand_penalty_amount = base_focus_score * self.HAND_NEAR_FACE_PENALTY
        
        # Apply penalties
        focus_score = max(0.0, base_focus_score - phone_penalty_amount - hand_penalty_amount)
        
        is_focused = focus_score >= self.FOCUS_THRESHOLD
        
        # Update tracking state
        current_time = time.time()
        if is_focused:
            self.last_focus_time = current_time
            self.distraction_start_time = None
        else:
            if self.distraction_start_time is None:
                self.distraction_start_time = current_time
            elif current_time - self.distraction_start_time >= self.DISTRACTION_TIME_LIMIT:
                if self.distraction_callback and self.is_tracking:
                    self.distraction_callback()
                self.distraction_count += 1
                self.distraction_start_time = current_time  # Reset to avoid repeated calls
        
        self.current_focus_score = focus_score
        
        # Log event if tracking
        if self.is_tracking:
            event = {
                "timestamp": current_time,
                "focus_score": focus_score,
                "is_focused": is_focused,
                "ear": avg_ear,
                "gaze": gaze_direction,
                "head_pose": {"pitch": pitch, "yaw": yaw, "roll": roll},
                "phone_detected": phone_detected,
                "phone_confidence": phone_confidence,
                "hands_near_face": hands_near_face,
                "hand_count": hand_count
            }
            self.focus_events.append(event)
        
        details = f"EAR: {avg_ear:.2f}, Gaze: {gaze_direction}, Pose: {pitch:.1f}°/{yaw:.1f}°/{roll:.1f}°"
        if phone_detected:
            details += f", PHONE ({phone_confidence:.2f})"
        if hands_near_face:
            details += f", HANDS@FACE ({hand_count})"
        
        return {
            "focus_score": focus_score,
            "is_focused": is_focused,
            "ear": avg_ear,
            "gaze": gaze_direction,
            "head_pose": {"pitch": pitch, "yaw": yaw, "roll": roll},
            "phone_detected": phone_detected,
            "phone_confidence": phone_confidence,
            "phone_boxes": all_detection_boxes,
            "hands_near_face": hands_near_face,
            "hand_count": hand_count,
            "details": details
        }
        
    def process_frame(self):
        """Process current camera frame and return annotated frame."""
        if not self.camera or not self.camera.isOpened():
            return None
            
        ret, frame = self.camera.read()
        if not ret:
            return None
            
        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Analyze focus
        focus_data = self.analyze_focus_level(frame)
        
        # Draw phone detection bounding boxes first (so they appear behind other annotations)
        if focus_data.get("phone_detected", False) and focus_data.get("phone_boxes"):
            for box in focus_data["phone_boxes"]:
                if len(box) == 6:  # New format with type
                    x1, y1, x2, y2, conf, detection_type = box
                else:  # Old format (backwards compatibility)
                    x1, y1, x2, y2, conf = box
                    detection_type = 'phone'
                
                # Choose color based on detection type
                if detection_type == 'phone':
                    color = (0, 0, 255)  # Red for full phone detection
                    label = f"PHONE {conf:.2f}"
                elif detection_type == 'phone_partial':
                    color = (0, 165, 255)  # Orange for partial detection
                    label = f"PHONE? {conf:.2f}"
                else:
                    color = (255, 255, 0)  # Yellow for other
                    label = f"{detection_type.upper()} {conf:.2f}"
                
                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                # Add label with background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), color, -1)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw annotations
        if focus_data["focus_score"] > 0 and self.show_outline:
            # Draw face mesh only if outline is enabled
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Draw eye contours
                    self.mp_drawing.draw_landmarks(
                        frame, face_landmarks,
                        self.mp_face_mesh.FACEMESH_CONTOURS,
                        None,
                        self.mp_drawing_styles.get_default_face_mesh_contours_style()
                    )
        
        # Draw focus status
        color = (0, 255, 0) if focus_data["is_focused"] else (0, 0, 255)
        status_text = "FOCUSED" if focus_data["is_focused"] else "DISTRACTED"
        
        # Calculate box height dynamically based on content
        base_box_height = 165
        if focus_data.get("phone_detected", False):
            base_box_height += 25
        if focus_data.get("hands_near_face", False):
            base_box_height += 25
        
        # Main status box (dynamic size)
        cv2.rectangle(frame, (10, 10), (300, base_box_height), color, -1)
        cv2.putText(frame, status_text, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(frame, f"Score: {focus_data['focus_score']:.2f}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Eye status - using calibrated thresholds (lower = more open, higher = more closed)
        ear = focus_data.get('ear', 0.0)
        eye_status = "OPEN" if ear < self.EYE_OPEN_THRESHOLD else "SQUINT" if ear < self.EYE_CLOSED_THRESHOLD else "CLOSED"
        cv2.putText(frame, f"Eyes: {eye_status} ({ear:.3f})", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Head pose angles (most important info)
        pose = focus_data['head_pose']
        cv2.putText(frame, f"Pitch: {pose['pitch']:+.1f} deg", (20, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"Yaw: {pose['yaw']:+.1f} deg", (20, 158), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Phone detection status
        y_offset = 183
        if focus_data.get("phone_detected", False):
            phone_conf = focus_data.get("phone_confidence", 0.0)
            cv2.putText(frame, f"PHONE! ({phone_conf:.2f})", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            y_offset += 25
        
        if focus_data.get("hands_near_face", False):
            hand_count = focus_data.get("hand_count", 0)
            cv2.putText(frame, f"HANDS@FACE ({hand_count})", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Threshold indicators (bottom left)
        cv2.putText(frame, f"Thresholds: P±{self.HEAD_PITCH_THRESHOLD} Y±{self.HEAD_YAW_THRESHOLD}", 
                   (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
        
    def get_session_stats(self) -> Dict:
        """Get statistics for current tracking session."""
        if not self.focus_events:
            return {
                "total_time": 0,
                "focus_time": 0,
                "distraction_time": 0,
                "focus_percentage": 0.0,
                "average_focus_score": 0.0,
                "distraction_count": self.distraction_count
            }
        
        current_time = time.time()
        total_time = current_time - self.session_start_time if self.session_start_time else 0
        
        # Calculate focus statistics
        focused_events = [e for e in self.focus_events if e["is_focused"]]
        focus_time = len(focused_events)
        total_events = len(self.focus_events)
        
        focus_percentage = (focus_time / total_events * 100) if total_events > 0 else 0
        
        focus_scores = [e["focus_score"] for e in self.focus_events]
        avg_focus_score = sum(focus_scores) / len(focus_scores) if focus_scores else 0
        
        return {
            "total_time": total_time,
            "focus_time": focus_time,
            "distraction_time": total_events - focus_time,
            "focus_percentage": focus_percentage,
            "average_focus_score": avg_focus_score,
            "distraction_count": self.distraction_count,
            "total_events": total_events
        }
        
    def cleanup(self):
        """Clean up resources."""
        if self.camera:
            self.camera.release()
        if hasattr(self, 'hands'):
            self.hands.close()
        self.stop_tracking()
        print("Focus tracker cleaned up")
