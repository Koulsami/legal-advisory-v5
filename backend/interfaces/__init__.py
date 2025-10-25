"""
Interfaces Module
Legal Advisory System v5.0

All interface definitions (Abstract Base Classes)
"""

# Data Structures
from .data_structures import (
    LogicTreeNode,
    MatchResult,
    ValidationError,
    ConversationSession,
    ModuleMetadata,
    FieldRequirement,
    QuestionTemplate,
    AIRequest,
    AIResponse,
    ModuleStatus,
    AIProvider,
    AIServiceType,
)

# Interfaces
from .legal_module import ILegalModule
from .ai_service import IAIService
from .matching import IMatchingEngine
from .validation import IValidator
from .tree import ITreeFramework
from .analysis import IAnalysisEngine
from .calculator import ICalculator

__all__ = [
    # Data Structures
    'LogicTreeNode',
    'MatchResult',
    'ValidationError',
    'ConversationSession',
    'ModuleMetadata',
    'FieldRequirement',
    'QuestionTemplate',
    'AIRequest',
    'AIResponse',
    'ModuleStatus',
    'AIProvider',
    'AIServiceType',
    # Interfaces
    'ILegalModule',
    'IAIService',
    'IMatchingEngine',
    'IValidator',
    'ITreeFramework',
    'IAnalysisEngine',
    'ICalculator',
]
