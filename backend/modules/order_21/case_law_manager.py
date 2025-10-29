"""
Case Law Manager for Order 21
Intelligent search, matching, and retrieval of case law
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import re
from backend.modules.order_21.case_law_data import (
    CaseLaw,
    CASE_LAW_DATABASE,
    get_all_cases,
    get_cases_by_provision,
    get_cases_by_keyword,
    get_cases_by_relevance_tag,
    get_database_statistics
)


@dataclass
class CaseLawMatch:
    """Represents a case law match with relevance score"""
    case: CaseLaw
    relevance_score: float  # 0.0 to 1.0
    match_reasons: List[str]  # Why this case was matched

    def __lt__(self, other):
        """For sorting by relevance"""
        return self.relevance_score > other.relevance_score  # Descending order


class CaseLawManager:
    """
    Manages case law database with intelligent search and matching capabilities.

    Features:
    - Search by keywords, provisions, principles
    - Match case law to cost scenarios
    - Relevance scoring
    - Formatted output for AI and user display
    """

    def __init__(self):
        """Initialize the case law manager"""
        self.database = CASE_LAW_DATABASE
        self.all_cases = get_all_cases()

    # ================================================================================
    # SEARCH METHODS
    # ================================================================================

    def search(self, query: str, max_results: int = 5) -> List[CaseLawMatch]:
        """
        Universal search across all case law fields.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of CaseLawMatch objects sorted by relevance
        """
        query_lower = query.lower()
        matches = []

        for case in self.all_cases:
            score, reasons = self._calculate_search_score(case, query_lower)
            if score > 0:
                matches.append(CaseLawMatch(
                    case=case,
                    relevance_score=score,
                    match_reasons=reasons
                ))

        # Sort by relevance and return top N
        matches.sort()
        return matches[:max_results]

    def search_by_provision(self, provision: str) -> List[CaseLaw]:
        """
        Search for cases interpreting a specific Order 21 provision.

        Args:
            provision: e.g., "Order 21 r 2(1)" or just "2(1)" or "r 2"

        Returns:
            List of matching CaseLaw objects
        """
        return get_cases_by_provision(provision)

    def search_by_scenario(self, scenario_type: str,
                          filled_fields: Optional[Dict[str, any]] = None,
                          max_results: int = 3) -> List[CaseLawMatch]:
        """
        Find case law relevant to a specific cost scenario.

        Args:
            scenario_type: Type of scenario (e.g., "default_judgment", "trial", "indemnity")
            filled_fields: Fields extracted from user query
            max_results: Maximum results to return

        Returns:
            List of CaseLawMatch objects sorted by relevance
        """
        matches = []

        # Determine relevant tags based on scenario
        relevant_tags = self._get_tags_for_scenario(scenario_type, filled_fields)

        # Search by tags
        for tag in relevant_tags:
            cases = get_cases_by_relevance_tag(tag)
            for case in cases:
                # Check if already added
                if not any(m.case.case_id == case.case_id for m in matches):
                    score, reasons = self._calculate_scenario_relevance(
                        case, scenario_type, filled_fields, relevant_tags
                    )
                    if score > 0:
                        matches.append(CaseLawMatch(
                            case=case,
                            relevance_score=score,
                            match_reasons=reasons
                        ))

        # Sort and return top N
        matches.sort()
        return matches[:max_results]

    def search_by_keywords(self, keywords: List[str]) -> List[CaseLaw]:
        """
        Search for cases by multiple keywords.

        Args:
            keywords: List of keywords to search for

        Returns:
            List of CaseLaw objects matching any keyword
        """
        matching_cases = set()
        for keyword in keywords:
            cases = get_cases_by_keyword(keyword)
            matching_cases.update(cases)
        return list(matching_cases)

    # ================================================================================
    # CONTEXT GENERATION FOR AI
    # ================================================================================

    def get_ai_context(self, scenario_type: str,
                       filled_fields: Optional[Dict[str, any]] = None,
                       max_cases: int = 2) -> str:
        """
        Generate formatted case law context for inclusion in AI prompts.

        Args:
            scenario_type: Type of scenario
            filled_fields: Fields from user query
            max_cases: Maximum cases to include

        Returns:
            Formatted string suitable for AI prompt
        """
        matches = self.search_by_scenario(scenario_type, filled_fields, max_cases)

        if not matches:
            return ""

        context_parts = ["**Relevant Case Law:**\n"]

        for i, match in enumerate(matches, 1):
            case = match.case
            context_parts.append(f"{i}. **{case.short_name}** {case.citation}")
            context_parts.append(f"   - *Principle:* {case.principle}")
            context_parts.append(f"   - *Quote:* \"{case.verbatim_quote[:200]}...\" (at {case.paragraph_ref})")
            context_parts.append("")

        return "\n".join(context_parts)

    def get_citation_text(self, case_ids: List[str]) -> str:
        """
        Generate formatted citation text for specific cases.

        Args:
            case_ids: List of case IDs

        Returns:
            Formatted citation text
        """
        citations = []
        for case_id in case_ids:
            case = self._get_case_by_id(case_id)
            if case:
                citations.append(f"- {case.get_formatted_citation()} at {case.paragraph_ref}")

        return "\n".join(citations)

    # ================================================================================
    # USER DISPLAY FORMATTING
    # ================================================================================

    def format_case_for_display(self, case: CaseLaw, include_quote: bool = True) -> Dict[str, any]:
        """
        Format a case for user display.

        Args:
            case: CaseLaw object
            include_quote: Whether to include verbatim quote

        Returns:
            Dictionary with formatted case information
        """
        formatted = {
            "citation": case.citation,
            "short_name": case.short_name,
            "year": case.year,
            "court": case._get_court_name(),
            "provision": case.provision,
            "principle": case.principle,
            "interpretation": case.interpretation,
            "paragraph_ref": case.paragraph_ref,
            "authority_statement": case.get_authority_statement()
        }

        if include_quote:
            formatted["verbatim_quote"] = case.verbatim_quote

        return formatted

    def format_matches_for_display(self, matches: List[CaseLawMatch]) -> List[Dict[str, any]]:
        """Format multiple case matches for display"""
        return [
            {
                **self.format_case_for_display(match.case, include_quote=False),
                "relevance_score": match.relevance_score,
                "match_reasons": match.match_reasons
            }
            for match in matches
        ]

    # ================================================================================
    # HELPER METHODS
    # ================================================================================

    def _calculate_search_score(self, case: CaseLaw, query: str) -> tuple[float, List[str]]:
        """
        Calculate relevance score for general search.

        Returns:
            Tuple of (score, reasons)
        """
        score = 0.0
        reasons = []

        # Check principle (highest weight)
        if query in case.principle.lower():
            score += 0.4
            reasons.append("Matches principle")

        # Check interpretation
        if query in case.interpretation.lower():
            score += 0.2
            reasons.append("Matches interpretation")

        # Check keywords
        for keyword in case.keywords:
            if query in keyword.lower():
                score += 0.15
                reasons.append(f"Matches keyword: {keyword}")

        # Check provision
        if query in case.provision.lower():
            score += 0.15
            reasons.append("Matches provision")

        # Check case name
        if query in case.short_name.lower():
            score += 0.1
            reasons.append("Matches case name")

        return (score, reasons)

    def _calculate_scenario_relevance(self, case: CaseLaw, scenario_type: str,
                                     filled_fields: Optional[Dict[str, any]],
                                     relevant_tags: List[str]) -> tuple[float, List[str]]:
        """Calculate relevance score for scenario matching"""
        score = 0.0
        reasons = []

        # Base score for matching tags
        matching_tags = set(case.relevance_tags) & set(relevant_tags)
        if matching_tags:
            score += 0.5 * (len(matching_tags) / len(relevant_tags))
            reasons.append(f"Matches tags: {', '.join(matching_tags)}")

        # Bonus for indemnity basis
        if filled_fields and filled_fields.get("costs_basis") == "indemnity":
            if "indemnity" in case.keywords:
                score += 0.3
                reasons.append("Relevant to indemnity basis")

        # Bonus for litigant-in-person
        if filled_fields and filled_fields.get("litigant_in_person"):
            if "litigant_in_person" in case.relevance_tags:
                score += 0.3
                reasons.append("Relevant to litigant-in-person")

        # Bonus for recent cases
        if case.year >= 2024:
            score += 0.1
            reasons.append("Recent case")

        # Bonus for Court of Appeal cases (higher authority)
        if case.court == "SGCA":
            score += 0.1
            reasons.append("Court of Appeal authority")

        return (score, reasons)

    def _get_tags_for_scenario(self, scenario_type: str,
                               filled_fields: Optional[Dict[str, any]]) -> List[str]:
        """Determine relevant tags based on scenario type"""
        tags = ["general_principles"]  # Always include

        # Map scenario types to tags
        scenario_tag_map = {
            "default_judgment": ["successful_party", "costs_follow_event"],
            "contested_trial": ["conduct", "complexity", "proportionality"],
            "interlocutory": ["discretion", "assessment_factors"],
            "appeal": ["appeal", "stay_application"],
            "assessment": ["assessment", "taxation", "proportionality"],
        }

        # Add scenario-specific tags
        for scenario_key, scenario_tags in scenario_tag_map.items():
            if scenario_key in scenario_type.lower():
                tags.extend(scenario_tags)

        # Add tags based on filled fields
        if filled_fields:
            if filled_fields.get("costs_basis") == "indemnity":
                tags.extend(["indemnity_basis", "exceptional_circumstances"])

            if filled_fields.get("litigant_in_person"):
                tags.append("litigant_in_person")

            if filled_fields.get("non_party"):
                tags.append("non_party_costs")

            if filled_fields.get("solicitor_costs"):
                tags.append("solicitor_costs")

        return list(set(tags))  # Remove duplicates

    def _get_case_by_id(self, case_id: str) -> Optional[CaseLaw]:
        """Get a case by its ID"""
        for case in self.all_cases:
            if case.case_id == case_id:
                return case
        return None

    # ================================================================================
    # STATISTICS AND INFO
    # ================================================================================

    def get_statistics(self) -> Dict[str, any]:
        """Get database statistics"""
        return get_database_statistics()

    def get_all_provisions(self) -> List[str]:
        """Get list of all provisions covered"""
        provisions = set()
        for case in self.all_cases:
            provisions.add(case.provision)
        return sorted(list(provisions))

    def get_all_keywords(self) -> List[str]:
        """Get list of all keywords"""
        keywords = set()
        for case in self.all_cases:
            keywords.update(case.keywords)
        return sorted(list(keywords))

    def get_cases_by_category(self, category: str) -> List[CaseLaw]:
        """Get all cases in a specific category"""
        return self.database.get(category, [])

    def get_all_categories(self) -> List[str]:
        """Get list of all categories"""
        return list(self.database.keys())


# ====================================================================================
# CONVENIENCE FUNCTIONS
# ====================================================================================

# Global instance for easy access
_case_law_manager = None


def get_case_law_manager() -> CaseLawManager:
    """Get the global CaseLawManager instance"""
    global _case_law_manager
    if _case_law_manager is None:
        _case_law_manager = CaseLawManager()
    return _case_law_manager


def search_case_law(query: str, max_results: int = 5) -> List[CaseLawMatch]:
    """Convenience function for searching case law"""
    manager = get_case_law_manager()
    return manager.search(query, max_results)


def get_case_law_for_scenario(scenario_type: str,
                               filled_fields: Optional[Dict[str, any]] = None,
                               max_results: int = 3) -> List[CaseLawMatch]:
    """Convenience function for scenario-based case law retrieval"""
    manager = get_case_law_manager()
    return manager.search_by_scenario(scenario_type, filled_fields, max_results)


def get_case_law_ai_context(scenario_type: str,
                            filled_fields: Optional[Dict[str, any]] = None) -> str:
    """Convenience function for generating AI context"""
    manager = get_case_law_manager()
    return manager.get_ai_context(scenario_type, filled_fields)
