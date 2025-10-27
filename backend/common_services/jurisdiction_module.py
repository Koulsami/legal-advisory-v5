"""
Jurisdiction Module System
Legal Advisory System v6.0

Provides modular jurisdiction architecture for multi-jurisdiction support.
Inspired by proven RAG patterns while maintaining simplicity.

This architecture allows adding new jurisdictions (UK, India, etc.) without
core system changes.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from backend.common_services.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DocumentSource:
    """Metadata for a legal document source"""
    name: str
    type: str  # e.g., "procedural_rules", "practice_directions", "statutes"
    path: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[str] = None


@dataclass
class CitationFormat:
    """Citation format rules for a jurisdiction"""
    rule_pattern: str  # Regex pattern for rules
    case_pattern: Optional[str] = None  # Regex pattern for cases
    display_format: str = "{citation}"  # How to display citations


@dataclass
class RetrievalConfig:
    """Retrieval and ranking configuration for a jurisdiction"""
    boost_courts: Dict[str, float] = None  # Court level boosts
    boost_recent: Dict[str, float] = None  # Recency boosts
    mandatory_filters: Dict[str, Any] = None  # Required filters


class JurisdictionModule(ABC):
    """
    Base class for jurisdiction-specific implementations.

    Each jurisdiction implements this interface to provide:
    - Legal module calculators
    - Document sources
    - Citation formats
    - Retrieval configurations

    This enables plug-and-play multi-jurisdiction support.
    """

    @abstractmethod
    def get_id(self) -> str:
        """Unique identifier (e.g., 'SG', 'UK', 'IN')"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Display name (e.g., 'Singapore', 'United Kingdom', 'India')"""
        pass

    @abstractmethod
    def get_document_sources(self) -> List[DocumentSource]:
        """
        Legal document sources for this jurisdiction.

        Returns:
            List of DocumentSource objects
        """
        pass

    @abstractmethod
    def get_citation_format(self) -> CitationFormat:
        """
        Citation format rules for this jurisdiction.

        Returns:
            CitationFormat object with regex patterns
        """
        pass

    @abstractmethod
    def get_retrieval_config(self) -> RetrievalConfig:
        """
        Retrieval and ranking configuration.

        Returns:
            RetrievalConfig object with boost factors
        """
        pass

    @abstractmethod
    def get_calculators(self) -> Dict[str, Any]:
        """
        Available calculator modules for this jurisdiction.

        Returns:
            Dict mapping module_id to calculator instance
        """
        pass


class SingaporeJurisdiction(JurisdictionModule):
    """
    Singapore legal system implementation.

    Provides Singapore-specific:
    - Order 21 cost calculator
    - Rules of Court 2021 documents
    - Singapore citation formats
    - Court hierarchy boosts
    """

    def __init__(self, module_registry=None):
        """
        Initialize Singapore jurisdiction.

        Args:
            module_registry: Optional module registry for accessing calculators
        """
        self.module_registry = module_registry

    def get_id(self) -> str:
        return "SG"

    def get_name(self) -> str:
        return "Singapore"

    def get_document_sources(self) -> List[DocumentSource]:
        return [
            DocumentSource(
                name="Rules of Court 2021",
                type="procedural_rules",
                path="docs/Rules_of_Court_202113.pdf",
                version="2021",
                effective_date="2021-04-01"
            ),
            DocumentSource(
                name="Supreme Court Practice Directions",
                type="practice_directions",
                path=None,  # Future
                version="2021"
            ),
            DocumentSource(
                name="Legal Profession Act",
                type="statute",
                path=None,  # Future
                version="2023"
            )
        ]

    def get_citation_format(self) -> CitationFormat:
        return CitationFormat(
            rule_pattern=r"Order\s+(\d+)(?:,\s*Rule\s+(\d+)(?:\((\d+|[a-z])\))?)?",
            case_pattern=r"\[(\d{4})\]\s+SGHC\s+(\d+)",
            display_format="Order {order}, Rule {rule}({para})"
        )

    def get_retrieval_config(self) -> RetrievalConfig:
        return RetrievalConfig(
            boost_courts={
                'Court of Appeal': 1.5,
                'High Court': 1.2,
                'District Court': 1.0,
                'Magistrates Court': 0.9
            },
            boost_recent={
                'within_1_year': 1.3,
                'within_5_years': 1.1,
                'older_than_5_years': 1.0
            },
            mandatory_filters={
                'jurisdiction': 'Singapore',
                'status': 'active'
            }
        )

    def get_calculators(self) -> Dict[str, Any]:
        """
        Get available calculators for Singapore.

        Returns:
            Dict of calculator instances
        """
        calculators = {}

        if self.module_registry:
            # Get Order 21 module from registry
            order21 = self.module_registry.get_module('ORDER_21')
            if order21:
                calculators['ORDER_21'] = order21

            # Future calculators can be added here
            # order5 = self.module_registry.get_module('ORDER_5')
            # if order5:
            #     calculators['ORDER_5'] = order5

        return calculators

    def get_statistics(self) -> Dict[str, Any]:
        """Get jurisdiction-specific statistics"""
        return {
            "jurisdiction_id": self.get_id(),
            "jurisdiction_name": self.get_name(),
            "available_modules": list(self.get_calculators().keys()),
            "document_sources": len(self.get_document_sources()),
        }


class JurisdictionRegistry:
    """
    Registry of all available jurisdictions.

    Maintains a central registry of jurisdiction modules for
    easy lookup and management.
    """

    _modules: Dict[str, JurisdictionModule] = {}

    @classmethod
    def register(cls, module: JurisdictionModule):
        """
        Register a jurisdiction module.

        Args:
            module: JurisdictionModule instance to register
        """
        jurisdiction_id = module.get_id()
        cls._modules[jurisdiction_id] = module
        logger.info(f"Registered jurisdiction: {module.get_name()} ({jurisdiction_id})")

    @classmethod
    def get(cls, jurisdiction_id: str) -> Optional[JurisdictionModule]:
        """
        Get jurisdiction module by ID.

        Args:
            jurisdiction_id: Jurisdiction identifier (e.g., 'SG')

        Returns:
            JurisdictionModule instance or None if not found
        """
        return cls._modules.get(jurisdiction_id)

    @classmethod
    def list_all(cls) -> List[str]:
        """
        List all registered jurisdiction IDs.

        Returns:
            List of jurisdiction IDs
        """
        return list(cls._modules.keys())

    @classmethod
    def list_all_details(cls) -> List[Dict[str, str]]:
        """
        List all registered jurisdictions with details.

        Returns:
            List of dicts with jurisdiction metadata
        """
        return [
            {
                "id": jur_id,
                "name": module.get_name(),
                "calculators": list(module.get_calculators().keys())
            }
            for jur_id, module in cls._modules.items()
        ]

    @classmethod
    def clear(cls):
        """Clear all registered jurisdictions (for testing)"""
        cls._modules = {}
