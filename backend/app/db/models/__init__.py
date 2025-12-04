"""Database models package."""
from app.db.models.user import User, UserRole
from app.db.models.contract import Contract, ContractStatus
from app.db.models.template import Template
from app.db.models.upload import Upload, FileType, ExtractionStatus
from app.db.models.proposal import Proposal, ValidationStatus, RiskLevel
from app.db.models.job import Job, JobStatus, JobType
from app.db.models.audit import AuditLog, AuditAction
from app.db.models.conversation import (
    Conversation, ConversationMessage, AIInteractionLog,
    ConversationStatus, MessageRole
)

__all__ = [
    "User",
    "UserRole",
    "Contract",
    "ContractStatus",
    "Template",
    "Upload",
    "FileType",
    "ExtractionStatus",
    "Proposal",
    "ValidationStatus",
    "RiskLevel",
    "Job",
    "JobStatus",
    "JobType",
    "AuditLog",
    "AuditAction",
    "Conversation",
    "ConversationMessage",
    "AIInteractionLog",
    "ConversationStatus",
    "MessageRole",
]
