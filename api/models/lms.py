# api/models/lms.py
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship

from api.config.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False, index=True)

    participants = relationship("Participant", back_populates="company")
    courses = relationship("Course", back_populates="company")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    level = Column(String, nullable=True)
    duration_hours = Column(Float, nullable=True)
    status = Column(String, default="BORRADOR")

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="courses")

    editions = relationship("CourseEdition", back_populates="course")
    lessons = relationship("Lesson", back_populates="course")


class CourseEdition(Base):
    __tablename__ = "course_editions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, default="EN_PROGRESO")

    course = relationship("Course", back_populates="editions")
    enrollments = relationship("Enrollment", back_populates="edition")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    type = Column(String, default="TEORICA")

    course = relationship("Course", back_populates="lessons")
    progresses = relationship("LessonProgress", back_populates="lesson")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True)

    company = relationship("Company", back_populates="participants")
    enrollments = relationship("Enrollment", back_populates="participant")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    edition_id = Column(Integer, ForeignKey("course_editions.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="ASIGNADO")

    participant = relationship("Participant", back_populates="enrollments")
    edition = relationship("CourseEdition", back_populates="enrollments")
    progresses = relationship("LessonProgress", back_populates="enrollment")
    certificate = relationship("Certificate", back_populates="enrollment", uselist=False)


class LessonProgress(Base):
    __tablename__ = "lesson_progresses"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    status = Column(String, default="NO_INICIADA")
    last_event_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Float, nullable=True)

    enrollment = relationship("Enrollment", back_populates="progresses")
    lesson = relationship("Lesson", back_populates="progresses")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    code = Column(String, unique=True, index=True)
    url = Column(String, nullable=True)
    grade = Column(Float, nullable=True)

    enrollment = relationship("Enrollment", back_populates="certificate")


class NotificationEvent(Base):
    __tablename__ = "notification_events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    payload = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="ENVIADO")
