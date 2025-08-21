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
        
        # Camera
        self.camera = None
        self.camera_index = 0
        
        # Eye tracking parameters
        self.EAR_THRESHOLD = 0.25  # Eye Aspect Ratio threshold
        self.FOCUS_THRESHOLD = 0.7  # Overall focus threshold
        self.DISTRACTION_TIME_LIMIT = 3.0  # Seconds
        
        # State tracking
        self.is_tracking = False
        self.last_focus_time = time.time()
        self.current_focus_score = 0.0
        self.distraction_start_time = None
        
        # Eye landmarks (MediaPipe face mesh indices)
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        # Gaze direction landmarks
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
        # Session data
        self.session_start_time = None
        self.focus_events = []
        self.distraction_count = 0
        
        # Callbacks
        self.distraction_callback = None
        
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
            # Vertical distances
            A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[1])
            B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[3])
            
            # Horizontal distance  
            C = np.linalg.norm(eye_landmarks - eye_landmarks[4])
            
            # EAR calculation
            ear = (A + B) / (2.0 * C)
            return ear
            
        except (IndexError, ZeroDivisionError):
            return 0.0
            
    def extract_eye_landmarks(self, landmarks, eye_indices) -> np.ndarray:
        """Extract eye landmarks from face mesh."""
        eye_points = []
        for idx in eye_indices[:6]:  # Use first 6 points for EAR calculation
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
            left_corner = np.array([landmarks.landmark[33].x, landmarks.landmark[5].y])
            right_corner = np.array([landmarks.landmark.x, landmarks.landmark.y])
            
            # Calculate relative positions
            left_ratio = (left_iris_center[0] - left_corner) / 0.05  # Normalize
            right_ratio = (right_iris_center - right_corner) / 0.05
            
            avg_ratio = (left_ratio + right_ratio) / 2
            
            if avg_ratio < -0.3:
                return "left"
            elif avg_ratio > 0.3:
                return "right"
            else:
                return "center"
                
        except (IndexError, AttributeError):
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
            
            # 2D image points
            image_points = np.array([
                (landmarks.landmark[1].x * w, landmarks.landmark[6].y * h),     # Nose tip
                (landmarks.landmark[7].x * w, landmarks.landmark[7].y * h),   # Chin
                (landmarks.landmark[5].x * w, landmarks.landmark[5].y * h),   # Left eye corner
                (landmarks.landmark.x * w, landmarks.landmark.y * h), # Right eye corner
                (landmarks.landmark[8].x * w, landmarks.landmark[8].y * h),   # Left mouth corner
                (landmarks.landmark.x * w, landmarks.landmark.y * h)  # Right mouth corner
            ], dtype=np.float32)
            
            # Camera matrix
            focal_length = w
            center = (w/2, h/2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[6]],
                [0, 0, 1]
            ], dtype=np.float32)
            
            # Distortion coefficients
            dist_coeffs = np.zeros((4,1))
            
            # Solve PnP
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs
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
                    roll = np.arctan2(-rotation_matrix[1,0], rotation_matrix[0,0])
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
        
    def analyze_focus_level(self, frame) -> Dict:
        """Analyze focus level from camera frame."""
        if frame is None:
            return {"focus_score": 0.0, "is_focused": False, "details": "No frame"}
            
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return {"focus_score": 0.0, "is_focused": False, "details": "No face detected"}
            
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
        
        # Focus scoring algorithm
        # 1. Eye openness (40% weight)
        eye_score = min(avg_ear / self.EAR_THRESHOLD, 1.0) * 0.4
        
        # 2. Gaze direction (35% weight)
        gaze_score = 0.35 if gaze_direction == "center" else 0.1
        
        # 3. Head pose (25% weight)
        head_score = max(0, 1 - (abs(pitch) + abs(yaw)) / 60) * 0.25
        
        focus_score = eye_score + gaze_score + head_score
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
                "head_pose": {"pitch": pitch, "yaw": yaw, "roll": roll}
            }
            self.focus_events.append(event)
        
        return {
            "focus_score": focus_score,
            "is_focused": is_focused,
            "ear": avg_ear,
            "gaze": gaze_direction,
            "head_pose": {"pitch": pitch, "yaw": yaw, "roll": roll},
            "details": f"EAR: {avg_ear:.2f}, Gaze: {gaze_direction}, Pose: {pitch:.1f}°/{yaw:.1f}°/{roll:.1f}°"
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
        
        # Draw annotations
        if focus_data["focus_score"] > 0:
            # Draw face mesh
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
        
        cv2.rectangle(frame, (10, 10), (250, 80), color, -1)
        cv2.putText(frame, status_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Score: {focus_data['focus_score']:.2f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
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
        self.stop_tracking()
        print("Focus tracker cleaned up")
