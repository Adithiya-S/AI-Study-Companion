import uuid
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db, StudySession, DistractionLog, User

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class StartSessionRequest(BaseModel):
    user_id: str
    mode: str = "pomodoro"
    duration_minutes: int = 25


class LogDistractionRequest(BaseModel):
    session_id: str
    distraction_type: str = "looking_away"
    ear_value: float = 0.18


class EndSessionRequest(BaseModel):
    session_id: str
    focus_score: float = 95.0
    actual_duration_minutes: Optional[int] = None


@router.post("/start")
def start_session(req: StartSessionRequest, db: Session = Depends(get_db)):
    if not req.user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    session_id = f"ses_{uuid.uuid4().hex[:8]}"
    new_session = StudySession(
        id=session_id,
        user_id=req.user_id,
        mode=req.mode,
        duration_minutes=req.duration_minutes,
        focus_score=100.0,
        distractions_count=0,
        start_time=datetime.datetime.utcnow(),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.id, "status": "started", "mode": new_session.mode}


@router.post("/log-distraction")
def log_distraction(req: LogDistractionRequest, db: Session = Depends(get_db)):
    session = db.query(StudySession).filter(StudySession.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.distractions_count += 1
    session.focus_score = max(50.0, round(session.focus_score - 3.5, 1))

    distraction = DistractionLog(
        session_id=session.id,
        distraction_type=req.distraction_type,
        ear_value=req.ear_value,
        timestamp=datetime.datetime.utcnow(),
    )
    db.add(distraction)
    db.commit()

    return {
        "status": "logged",
        "distractions_count": session.distractions_count,
        "current_focus_score": session.focus_score,
    }


@router.post("/end")
def end_session(req: EndSessionRequest, db: Session = Depends(get_db)):
    session = db.query(StudySession).filter(StudySession.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    now = datetime.datetime.utcnow()
    session.end_time = now
    session.focus_score = round(req.focus_score, 1)

    # Determine duration
    if req.actual_duration_minutes is not None and req.actual_duration_minutes > 0:
        session.duration_minutes = req.actual_duration_minutes
    elif session.start_time:
        elapsed = max(1, round((now - session.start_time).total_seconds() / 60))
        session.duration_minutes = min(session.duration_minutes, elapsed)

    # Update user total hours & streak
    user = db.query(User).filter(User.id == session.user_id).first()
    if user:
        added_hours = session.duration_minutes / 60.0
        user.total_hours = round((user.total_hours or 0.0) + added_hours, 2)
        if not user.focus_streak or user.focus_streak == "0 Days":
            user.focus_streak = "1 Day"

    db.commit()
    return {
        "status": "completed",
        "focus_score": session.focus_score,
        "duration_minutes": session.duration_minutes,
        "total_hours": user.total_hours if user else 0.0,
        "focus_streak": user.focus_streak if user else "1 Day",
    }


@router.get("/history")
def get_session_history(user_id: str = Query(...), db: Session = Depends(get_db)):
    sessions = (
        db.query(StudySession)
        .filter(StudySession.user_id == user_id)
        .order_by(StudySession.start_time.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": s.id,
            "mode": s.mode.title() if s.mode else "Study",
            "duration": f"{s.duration_minutes}m",
            "score": s.focus_score,
            "distractions": s.distractions_count,
            "date": s.start_time.strftime("%b %d, %H:%M") if s.start_time else "",
        }
        for s in sessions
    ]


@router.get("/analytics")
def get_session_analytics(
    user_id: str = Query(...),
    period: int = Query(7),
    db: Session = Depends(get_db),
):
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(days=period)

    # Sessions in selected period
    period_sessions = (
        db.query(StudySession)
        .filter(StudySession.user_id == user_id, StudySession.start_time >= cutoff)
        .order_by(StudySession.start_time.asc())
        .all()
    )

    # All sessions for history table
    all_sessions = (
        db.query(StudySession)
        .filter(StudySession.user_id == user_id)
        .order_by(StudySession.start_time.desc())
        .limit(30)
        .all()
    )

    total_sessions = len(period_sessions)
    total_minutes = sum(s.duration_minutes for s in period_sessions)
    total_hours = round(total_minutes / 60.0, 1)
    avg_duration = round(total_minutes / total_sessions) if total_sessions > 0 else 0
    overall_focus = (
        round(sum(s.focus_score for s in period_sessions) / total_sessions, 1)
        if total_sessions > 0
        else 0.0
    )
    total_distractions = sum(s.distractions_count for s in period_sessions)
    efficiency = (
        max(50.0, round(overall_focus - (total_distractions * 1.5), 1))
        if total_sessions > 0
        else 0.0
    )

    # Build Bar Data (Study hours distribution)
    if period == 1:
        # Breakdown by morning, afternoon, evening, night
        slot_hours = {"Morning": 0.0, "Afternoon": 0.0, "Evening": 0.0, "Night": 0.0}
        for s in period_sessions:
            if s.start_time:
                hour = s.start_time.hour
                hrs = s.duration_minutes / 60.0
                if 6 <= hour < 12:
                    slot_hours["Morning"] += hrs
                elif 12 <= hour < 17:
                    slot_hours["Afternoon"] += hrs
                elif 17 <= hour < 21:
                    slot_hours["Evening"] += hrs
                else:
                    slot_hours["Night"] += hrs
        bar_labels = ["Morning", "Afternoon", "Evening", "Night"]
        bar_values = [round(slot_hours[k], 2) for k in bar_labels]
    else:
        # Daily distribution for the period
        num_days = min(period, 14)
        days = [(now - datetime.timedelta(days=i)).date() for i in range(num_days - 1, -1, -1)]
        day_map = {d: 0.0 for d in days}
        for s in period_sessions:
            if s.start_time:
                s_date = s.start_time.date()
                if s_date in day_map:
                    day_map[s_date] += s.duration_minutes / 60.0
        bar_labels = [d.strftime("%a") if period == 7 else d.strftime("%m/%d") for d in days]
        bar_values = [round(day_map[d], 2) for d in days]

    # Build Line Data (Focus trend across period sessions)
    if period_sessions:
        line_labels = [
            s.start_time.strftime("%H:%M" if period == 1 else "%b %d %H:%M")
            if s.start_time
            else ""
            for s in period_sessions
        ]
        line_values = [s.focus_score for s in period_sessions]
    else:
        line_labels = []
        line_values = []

    history = [
        {
            "id": s.id,
            "date": s.start_time.strftime("%b %d, %H:%M") if s.start_time else "",
            "type": s.mode.title() if s.mode else "Study",
            "duration": f"{s.duration_minutes}m",
            "score": s.focus_score,
            "distractions": s.distractions_count,
        }
        for s in all_sessions
    ]

    return {
        "summary": {
            "total_sessions": total_sessions,
            "total_hours": total_hours,
            "avg_duration": avg_duration,
            "overall_focus": overall_focus,
            "efficiency": efficiency,
            "total_distractions": total_distractions,
        },
        "bar_data": {
            "labels": bar_labels,
            "values": bar_values,
        },
        "line_data": {
            "labels": line_labels,
            "values": line_values,
        },
        "history": history,
    }
