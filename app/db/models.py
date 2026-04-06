from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
import enum
from sqlalchemy import Enum


class ReviewStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
class AgentStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"

    
Base = declarative_base()
class ReviewRequest(Base):
    __tablename__ = "review_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    code_text  = Column(Text,nullable=False)
    code_hash  = Column(String(64), index= True, nullable= False)
    language   = Column(String(50), nullable=True)
    status   = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False)
    created_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable= False)

    
class AgentOutputs(Base):
    __tablename__ = "agent_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    review_id  = Column(UUID(as_uuid=True), ForeignKey("review_requests.id"))
    agent_name  = Column(String(50), nullable= False)
    output   = Column(JSONB)
    status = Column(Enum(AgentStatus), default=AgentStatus.SUCCESS, nullable=False)
    error_message   = Column(Text, nullable=True)
    created_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable= False)

class FinalReports(Base):
    __tablename__ = "final_reports"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    review_id  = Column(UUID(as_uuid=True), ForeignKey("review_requests.id"))
    overall_score  = Column(Integer, nullable=False)
    summary   = Column(Text)
    critical_issues   = Column(Integer, nullable=False)
    warnings   = Column(Integer, nullable=False)
    report_json   =Column(JSONB)
    created_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable= False)

    

class ErrorLogs(Base):
    __tablename__ = "error_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    review_id  = Column(UUID(as_uuid=True), ForeignKey("review_requests.id"), nullable=True)
    agent_name  =  Column(String(50))
    error_type   = Column(String(100))
    error_message   = Column(Text)
    created_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable= False)

