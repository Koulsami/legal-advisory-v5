"""
Analysis Engine - Orchestrates complete legal analysis workflow.

This engine coordinates all common services to perform comprehensive legal analysis:
- Module Registry: Selects appropriate legal modules
- Matching Engine: Finds relevant tree nodes
- Logic Tree Framework: Manages tree operations
- Legal Modules: Performs specialized calculations

CRITICAL PRINCIPLE: Orchestrates PRE-BUILT components.
NEVER constructs logic dynamically.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging
from datetime import datetime

from backend.interfaces.analysis import IAnalysisEngine
from backend.interfaces.legal_module import ILegalModule
from backend.interfaces.data_structures import ModuleStatus, MatchResult
from backend.common_services.module_registry import ModuleRegistry
from backend.common_services.matching_engine import UniversalMatchingEngine
from backend.common_services.logic_tree_framework import LogicTreeFramework

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    module_id: str
    module_name: str
    matched_nodes: List[MatchResult]
    calculation_result: Optional[Dict[str, Any]] = None
    recommendations: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    completeness_score: float = 0.0
    missing_fields: List[str] = field(default_factory=list)
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class MultiModuleAnalysisResult:
    """Result from analyzing multiple modules"""
    primary_result: Optional[AnalysisResult] = None
    alternative_results: List[AnalysisResult] = field(default_factory=list)
    total_modules_analyzed: int = 0
    analysis_summary: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AnalysisEngine(IAnalysisEngine):
    """
    Universal Analysis Engine.

    Orchestrates the complete analysis workflow by coordinating:
    - ModuleRegistry: Module selection and routing
    - UniversalMatchingEngine: Node matching
    - LogicTreeFramework: Tree operations
    - Legal Modules: Specialized calculations

    Key Features:
    - Intelligent module selection
    - Multi-module analysis support
    - Result aggregation and ranking
    - Completeness checking
    - Validation before calculation
    - Detailed analysis reporting

    Example:
        >>> engine = AnalysisEngine(registry, matcher, tree_framework)
        >>> # Analyze with specific module
        >>> result = await engine.analyze(order21_module, filled_fields)
        >>> # Auto-select and analyze
        >>> results = await engine.analyze_auto(filled_fields, top_k=3)
    """

    def __init__(
        self,
        module_registry: ModuleRegistry,
        matching_engine: UniversalMatchingEngine,
        tree_framework: LogicTreeFramework
    ):
        """
        Initialize the Analysis Engine.

        Args:
            module_registry: Registry of all legal modules
            matching_engine: Engine for matching nodes
            tree_framework: Framework for tree operations

        Raises:
            TypeError: If any argument is wrong type
        """
        if not isinstance(module_registry, ModuleRegistry):
            raise TypeError(
                f"module_registry must be ModuleRegistry, got {type(module_registry)}"
            )
        if not isinstance(matching_engine, UniversalMatchingEngine):
            raise TypeError(
                f"matching_engine must be UniversalMatchingEngine, got {type(matching_engine)}"
            )
        if not isinstance(tree_framework, LogicTreeFramework):
            raise TypeError(
                f"tree_framework must be LogicTreeFramework, got {type(tree_framework)}"
            )

        self.module_registry = module_registry
        self.matching_engine = matching_engine
        self.tree_framework = tree_framework

        # Statistics
        self._analysis_count = 0
        self._total_matches_found = 0

        logger.info("AnalysisEngine initialized")

    async def analyze(
        self,
        module: ILegalModule,
        filled_fields: Dict[str, Any],
        enhance_with_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Perform complete analysis with a specific module.

        This is the main analysis workflow:
        1. Validate input fields
        2. Check completeness
        3. Match relevant tree nodes
        4. Perform calculations (if complete)
        5. Generate recommendations
        6. Return comprehensive result

        Args:
            module: Legal module to use for analysis
            filled_fields: User-provided information
            enhance_with_ai: Whether to use AI enhancement (future)

        Returns:
            Dictionary with complete analysis results

        Example:
            >>> result = await engine.analyze(order21_module, {
            ...     "court_level": "High Court",
            ...     "party_type": "Plaintiff",
            ...     "amount_in_dispute": 100000
            ... })
            >>> print(f"Matched {len(result['matched_nodes'])} nodes")
        """
        self._analysis_count += 1

        if not isinstance(module, ILegalModule):
            raise TypeError(f"module must implement ILegalModule, got {type(module)}")

        metadata = module.metadata
        module_id = metadata.module_id

        logger.info(f"Starting analysis with module '{module_id}'")

        # Step 1: Validate fields
        is_valid, validation_errors = module.validate_fields(filled_fields)

        if not is_valid:
            logger.warning(
                f"Validation failed for module '{module_id}': {validation_errors}"
            )

        # Step 2: Check completeness
        completeness_score, missing_fields = module.check_completeness(filled_fields)

        logger.debug(
            f"Completeness: {completeness_score:.2%}, Missing: {missing_fields}"
        )

        # Step 3: Match relevant tree nodes
        tree_nodes = module.get_tree_nodes()
        matched_nodes = await self.matching_engine.match(
            tree_nodes=tree_nodes,
            filled_fields=filled_fields,
            threshold=0.3  # Lower threshold to find more possibilities
        )

        self._total_matches_found += len(matched_nodes)

        logger.info(
            f"Matched {len(matched_nodes)} nodes for module '{module_id}'"
        )

        # Step 4: Perform calculation if sufficiently complete
        calculation_result = None
        if completeness_score >= 0.7:  # 70% complete
            try:
                calculation_result = module.calculate(filled_fields)
                logger.info(f"Calculation completed for module '{module_id}'")
            except Exception as e:
                logger.error(f"Calculation failed for module '{module_id}': {e}")
                calculation_result = {"error": str(e)}
        else:
            logger.info(
                f"Skipping calculation - completeness {completeness_score:.2%} < 70%"
            )

        # Step 5: Generate recommendations
        recommendations = []
        if calculation_result and "error" not in calculation_result:
            try:
                recommendations = module.get_recommendations(calculation_result)
            except Exception as e:
                logger.error(f"Failed to generate recommendations: {e}")

        # Step 6: Calculate overall confidence
        confidence = self._calculate_analysis_confidence(
            completeness_score=completeness_score,
            validation_passed=is_valid,
            match_count=len(matched_nodes),
            calculation_succeeded=calculation_result is not None and "error" not in calculation_result
        )

        # Step 7: Build result
        result = {
            "module_id": module_id,
            "module_name": metadata.module_name,
            "matched_nodes": matched_nodes,
            "matched_node_count": len(matched_nodes),
            "calculation_result": calculation_result,
            "recommendations": recommendations,
            "validation_errors": validation_errors if not is_valid else [],
            "completeness_score": completeness_score,
            "missing_fields": missing_fields,
            "confidence": confidence,
            "is_valid": is_valid,
            "can_calculate": completeness_score >= 0.7,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(
            f"Analysis complete for module '{module_id}' "
            f"(confidence: {confidence:.2%})"
        )

        return result

    async def analyze_auto(
        self,
        filled_fields: Dict[str, Any],
        top_k: int = 3,
        require_active: bool = True
    ) -> MultiModuleAnalysisResult:
        """
        Auto-select modules and perform multi-module analysis.

        This method:
        1. Finds all suitable modules from registry
        2. Analyzes with each module
        3. Ranks results by confidence
        4. Returns top K results

        Args:
            filled_fields: User-provided information
            top_k: Number of top results to return (default: 3)
            require_active: Only use ACTIVE modules (default: True)

        Returns:
            MultiModuleAnalysisResult with ranked results

        Example:
            >>> results = await engine.analyze_auto({
            ...     "court": "High Court",
            ...     "costs": "dispute"
            ... }, top_k=3)
            >>> print(f"Best match: {results.primary_result.module_name}")
        """
        logger.info("Starting auto-analysis with module selection")

        # Get appropriate modules from registry
        status_filter = ModuleStatus.ACTIVE if require_active else None
        module_ids = self.module_registry.list_modules(status=status_filter)

        if not module_ids:
            logger.warning("No modules found for analysis")
            return MultiModuleAnalysisResult(
                total_modules_analyzed=0,
                analysis_summary="No modules available for analysis"
            )

        logger.info(f"Found {len(module_ids)} modules for analysis")

        # Analyze with each module
        results = []
        for module_id in module_ids:
            module = self.module_registry.get_module(module_id)
            if module:
                try:
                    result_dict = await self.analyze(module, filled_fields, enhance_with_ai=False)

                    # Convert to AnalysisResult
                    analysis_result = AnalysisResult(
                        module_id=result_dict["module_id"],
                        module_name=result_dict["module_name"],
                        matched_nodes=result_dict["matched_nodes"],
                        calculation_result=result_dict.get("calculation_result"),
                        recommendations=result_dict.get("recommendations", []),
                        validation_errors=result_dict.get("validation_errors", []),
                        completeness_score=result_dict["completeness_score"],
                        missing_fields=result_dict["missing_fields"],
                        confidence=result_dict["confidence"],
                        reasoning=self._generate_analysis_reasoning(result_dict)
                    )

                    results.append(analysis_result)

                except Exception as e:
                    logger.error(f"Analysis failed for module '{module_id}': {e}")

        # Rank results by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)

        # Select top K
        top_results = results[:top_k]

        # Build multi-module result
        multi_result = MultiModuleAnalysisResult(
            primary_result=top_results[0] if top_results else None,
            alternative_results=top_results[1:] if len(top_results) > 1 else [],
            total_modules_analyzed=len(results),
            analysis_summary=self._generate_multi_analysis_summary(results, top_k)
        )

        logger.info(
            f"Auto-analysis complete: analyzed {len(results)} modules, "
            f"returning top {len(top_results)}"
        )

        return multi_result

    async def analyze_with_module_id(
        self,
        module_id: str,
        filled_fields: Dict[str, Any],
        enhance_with_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Perform analysis with a specific module by ID.

        Convenience method that looks up module from registry.

        Args:
            module_id: ID of module to use
            filled_fields: User-provided information
            enhance_with_ai: Whether to use AI enhancement

        Returns:
            Analysis result dictionary

        Raises:
            ValueError: If module_id not found
        """
        module = self.module_registry.get_module(module_id)

        if module is None:
            raise ValueError(f"Module '{module_id}' not found in registry")

        return await self.analyze(module, filled_fields, enhance_with_ai)

    def get_analysis_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about analyses performed.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_analyses": self._analysis_count,
            "total_matches_found": self._total_matches_found,
            "average_matches_per_analysis": (
                self._total_matches_found / self._analysis_count
                if self._analysis_count > 0
                else 0
            ),
            "registered_modules": len(self.module_registry.list_modules()),
            "active_modules": len(
                self.module_registry.list_modules(status=ModuleStatus.ACTIVE)
            )
        }

    def _calculate_analysis_confidence(
        self,
        completeness_score: float,
        validation_passed: bool,
        match_count: int,
        calculation_succeeded: bool
    ) -> float:
        """
        Calculate overall confidence in the analysis result.

        Factors:
        - Completeness score (40%)
        - Validation passed (20%)
        - Number of matches (20%)
        - Calculation succeeded (20%)

        Returns:
            Confidence score 0.0-1.0
        """
        confidence = 0.0

        # Completeness contribution (40%)
        confidence += 0.4 * completeness_score

        # Validation contribution (20%)
        if validation_passed:
            confidence += 0.2

        # Match count contribution (20%)
        # More matches = higher confidence (up to a point)
        match_confidence = min(match_count / 5.0, 1.0)  # Cap at 5 matches
        confidence += 0.2 * match_confidence

        # Calculation contribution (20%)
        if calculation_succeeded:
            confidence += 0.2

        return round(min(confidence, 1.0), 4)

    def _generate_analysis_reasoning(self, result_dict: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for analysis result"""
        parts = []

        # Completeness
        completeness = result_dict["completeness_score"]
        parts.append(f"Information completeness: {completeness:.0%}")

        # Matches
        match_count = result_dict["matched_node_count"]
        if match_count > 0:
            parts.append(f"Found {match_count} relevant legal provisions")

        # Validation
        if result_dict["is_valid"]:
            parts.append("All fields validated successfully")
        else:
            error_count = len(result_dict.get("validation_errors", []))
            parts.append(f"{error_count} validation issues found")

        # Calculation
        if result_dict.get("calculation_result"):
            parts.append("Calculation completed")
        elif not result_dict["can_calculate"]:
            parts.append("Insufficient information for calculation")

        return "; ".join(parts)

    def _generate_multi_analysis_summary(
        self,
        results: List[AnalysisResult],
        top_k: int
    ) -> str:
        """Generate summary for multi-module analysis"""
        if not results:
            return "No modules produced results"

        best_confidence = results[0].confidence if results else 0

        summary_parts = [
            f"Analyzed {len(results)} module(s)",
            f"Best match confidence: {best_confidence:.0%}",
            f"Returning top {min(top_k, len(results))} result(s)"
        ]

        # Add info about best module
        if results:
            best = results[0]
            summary_parts.append(
                f"Recommended module: {best.module_name} "
                f"({best.matched_nodes.__len__()} matches)"
            )

        return "; ".join(summary_parts)
