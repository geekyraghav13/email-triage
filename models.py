from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class EmailPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EmailCategory(str, Enum):
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    BILLING = "billing"
    GENERAL_INQUIRY = "general_inquiry"
    SPAM = "spam"
    ESCALATION = "escalation"
    FEEDBACK = "feedback"


class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str
    has_attachment: bool = False
    thread_id: Optional[str] = None
    reply_to: Optional[str] = None


class Observation(BaseModel):
    """What the agent sees at each step."""
    current_email: Email
    inbox_size: int
    processed_count: int
    time_remaining: int  # steps remaining
    context: Optional[str] = None  # thread context for hard task
    task_id: str
    step_number: int


class Action(BaseModel):
    """What the agent can do."""
    action_type: Literal["classify", "prioritize", "reply", "escalate", "archive", "skip"]
    category: Optional[EmailCategory] = None
    priority: Optional[EmailPriority] = None
    reply_text: Optional[str] = None
    escalate_to: Optional[str] = None
    reasoning: Optional[str] = None  # agent explains its decision


class Reward(BaseModel):
    """Reward signal returned to the agent."""
    score: float = Field(ge=0.0, le=1.0)
    breakdown: dict  # component scores
    feedback: str  # human-readable explanation


class EnvironmentState(BaseModel):
    """Full internal state for state() endpoint."""
    task_id: str
    emails: List[Email]
    current_index: int
    actions_taken: List[dict]
    scores: List[float]
    done: bool
    total_reward: float
