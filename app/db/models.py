from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, VARCHAR
import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base


Base = declarative_base()
class ReviewRequest():
    __tablename__ = "review_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    code_text  = Column(Text,nullable=False)
    code_hash  = Column(String(64), index= True, nullable= False)
    language   = Column(String(50), nullable=True)
    status   = Column(String(20), default="pending", nullable=False)
    created_at   = Column(DateTime, default= datetime.now(timezone.utc))

    
class AgentOutputs():
    __tablename__ = "agent_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    review_id  = Column(UUID(as_uuid=True), ForeignKey("review_requests.id"))
    agent_name  = Column(VARCHAR(50))
    output   = Column(JSONB)
    status   = Column(VARCHAR(20), default="success", nullable=False)
    error_message   = Column(Text(20), nullable=True)
    created_at   = Column(DateTime, default= datetime.now(timezone.utc))

class FinalReports():
    __tablename__ = "final_reports"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    review_id  = Column(UUID(as_uuid=True), ForeignKey("review_requests.id"))
    overall_score  = Column(Integer, nullable=False)
    summary   = Column(Text)
    critical_issues   = Column(Integer, nullable=False)
    warnings   = Column(Integer, nullable=False)
    report_json   =Column(JSONB)
    created_at   = Column(DateTime, default= datetime.now(timezone.utc))

    

class ErrorLogs():
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    review_id  = Column(UUID(as_uuid=True), ForeignKey("review_requests.id"))
    agent_name  =  Column(VARCHAR(50))
    error_type   = Column(VARCHAR(100))
    error_message   = Column(Text)
    created_at   = Column(DateTime, default= datetime.now(timezone.utc))

