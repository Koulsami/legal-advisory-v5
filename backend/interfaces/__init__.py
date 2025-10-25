"""
Interfaces Module
Legal Advisory System v5.0

All interface definitions (Abstract Base Classes)
"""

from .ai_service import IAIService
from .analysis import IAnalysisEngine
from .calculator import ICalculator

# Data Structures
from .data_structures import (
    AIProvider,
    AIRequest,
    AIResponse,
    AIServiceType,
    ConversationSession,
    FieldRequirement,
    LogicTreeNode,
    MatchResult,
    ModuleMetadata,
    ModuleStatus,
    QuestionTemplate,
    ValidationError,
)

# Interfaces
from .legal_module import ILegalModule
from .matching import IMatchingEngine
from .tree import ITreeFramework
from .validation import IValidator

__all__ = [
    # Data Structures
    "LogicTreeNode",
    "MatchResult",
    "ValidationError",
    "ConversationSession",
    "ModuleMetadata",
    "FieldRequirement",
    "QuestionTemplate",
    "AIRequest",
    "AIResponse",
    "ModuleStatus",
    "AIProvider",
    "AIServiceType",
    # Interfaces
    "ILegalModule",
    "IAIService",
    "IMatchingEngine",
    "IValidator",
    "ITreeFramework",
    "IAnalysisEngine",
    "ICalculator",
]
