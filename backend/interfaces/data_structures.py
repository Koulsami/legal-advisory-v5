"""
Shared Data Structures
Legal Advisory System v5.0

These are used across all interfaces and modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# ============================================
# ENUMS
# ============================================


class ModuleStatus(Enum):
    """Module lifecycle status"""

    REGISTERED = "registered"
    ACTIVE = "active"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class AIProvider(Enum):
    """AI service providers"""

    ANTHROPIC_CLAUDE = "anthropic_claude"
    OPENAI_GPT = "openai_gpt"
    EMULATOR = "emulator"


class AIServiceType(Enum):
    """Types of AI services"""

    CONVERSATION = "conversation"
    ANALYSIS = "analysis"
    ENHANCEMENT = "enhancement"


# ============================================
# CORE DATA STRUCTURES
# ============================================


@dataclass
class LogicTreeNode:
    """
    Universal tree node structure.

    Six logical dimensions based on legal reasoning:
    - WHAT: Definitions and concepts
    - WHICH: Categorizations and types
    - IF-THEN: Conditional rules
    - MODALITY: Requirements (must/may/shall)
    - GIVEN: Contextual conditions
    - WHY: Rationale and purpose
    """

    # Identity
    node_id: str
    citation: str
    module_id: str

    # Six logical dimensions
    what: List[Dict[str, Any]] = field(default_factory=list)
    which: List[Dict[str, Any]] = field(default_factory=list)
    if_then: List[Dict[str, Any]] = field(default_factory=list)
    modality: List[Dict[str, Any]] = field(default_factory=list)
    given: List[Dict[str, Any]] = field(default_factory=list)
    why: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    confidence: float = 1.0
    source_type: str = "rule"
    effective_date: Optional[str] = None

    # Case Law References
    case_law_references: List[str] = field(default_factory=list)

    # Relationships
    parent_nodes: List[str] = field(default_factory=list)
    child_nodes: List[str] = field(default_factory=list)
    related_nodes: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate node after creation"""
        if not self.node_id:
            raise ValueError("node_id is required")
        if not self.citation:
            raise ValueError("citation is required")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class MatchResult:
    """Result of matching user input to tree nodes"""

    node_id: str
    node: LogicTreeNode
    match_score: float
    matched_fields: Dict[str, Any]
    missing_fields: List[str]
    confidence: float
    reasoning: str

    def __post_init__(self):
        """Validate match result"""
        if not (0.0 <= self.match_score <= 1.0):
            raise ValueError("match_score must be between 0.0 and 1.0")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class ValidationError:
    """Validation error details"""

    field_name: str
    error_type: str
    message: str
    current_value: Any
    expected_format: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ConversationSession:
    """Conversation session state"""

    session_id: str
    user_id: str
    module_id: Optional[str]
    filled_fields: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    status: str  # "active", "analyzing", "complete"

    def __post_init__(self):
        """Validate session"""
        valid_statuses = ["active", "analyzing", "complete", "error"]
        if self.status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")


@dataclass
class ModuleMetadata:
    """Metadata for a legal module"""

    module_id: str
    module_name: str
    version: str
    status: ModuleStatus
    author: str
    description: str
    effective_date: str
    last_updated: str
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class FieldRequirement:
    """Specification for a required field"""

    field_name: str
    field_type: str
    description: str
    required: bool
    validation_rules: Dict[str, Any]
    enum_values: Optional[List[str]] = None
    example: Optional[str] = None


@dataclass
class QuestionTemplate:
    """Template for information gathering questions"""

    field_name: str
    template: str
    priority: int
    context_required: List[str] = field(default_factory=list)
    validation_pattern: Optional[str] = None


@dataclass
class AIRequest:
    """Request to AI service"""

    service_type: AIServiceType
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 4096
    temperature: float = 0.7
    model: Optional[str] = None


@dataclass
class AIResponse:
    """Response from AI service"""

    content: str
    service_type: AIServiceType
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================
# CONVERSATION DATA STRUCTURES
# ============================================


class ConversationStatus(Enum):
    """Conversation session status"""

    ACTIVE = "active"
    INFORMATION_GATHERING = "information_gathering"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    ERROR = "error"


class MessageRole(Enum):
    """Message role in conversation"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ConversationMessage:
    """Single message in conversation"""

    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationSession:
    """
    Session state for ongoing conversation.

    Tracks all information gathered during conversation,
    including filled fields, conversation history, and analysis results.
    """

    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: ConversationStatus = ConversationStatus.ACTIVE

    # Module selection
    module_id: Optional[str] = None
    module_confidence: float = 0.0

    # Information gathering
    filled_fields: Dict[str, Any] = field(default_factory=dict)
    completeness_score: float = 0.0
    missing_fields: List[str] = field(default_factory=list)

    # Conversation history
    messages: List[ConversationMessage] = field(default_factory=list)

    # Analysis results (when complete)
    analysis_result: Optional[Dict[str, Any]] = None
    calculation_result: Optional[Dict[str, Any]] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationResponse:
    """
    Response to user message in conversation.

    Contains the assistant's message, current session state,
    and any actions to take.
    """

    message: str
    session_id: str
    status: ConversationStatus

    # Progress indicators
    completeness_score: float = 0.0
    next_action: Optional[str] = None  # "ask_question", "analyze", "complete"

    # Questions (if asking for more information)
    questions: List[str] = field(default_factory=list)

    # Results (if analysis complete)
    result: Optional[Dict[str, Any]] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InfoGap:
    """Information gap that needs to be filled"""

    field_name: str
    field_type: str
    description: str
    priority: int
    required: bool
    current_value: Optional[Any] = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
