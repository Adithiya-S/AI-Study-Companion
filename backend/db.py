import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from .config import DATABASE_URL

# Engine & Session
is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    focus_streak = Column(String(64), default="0 Days")
    total_hours = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("StudyDocument", back_populates="user", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete-orphan")


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    mode = Column(String(32), default="pomodoro")  # pomodoro, deepwork, break
    duration_minutes = Column(Integer, default=25)
    focus_score = Column(Float, default=95.0)
    distractions_count = Column(Integer, default=0)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    distractions = relationship("DistractionLog", back_populates="session", cascade="all, delete-orphan")


class DistractionLog(Base):
    __tablename__ = "distraction_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("study_sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    distraction_type = Column(String(64), default="looking_away")
    ear_value = Column(Float, default=0.18)

    session = relationship("StudySession", back_populates="distractions")


class StudyDocument(Base):
    __tablename__ = "study_documents"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(String(32), default="1.2 MB")
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="documents")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(64), default="General")
    mastered = Column(Boolean, default=False)
    review_count = Column(Integer, default=0)

    user = relationship("User", back_populates="flashcards")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
