"""
Deductive Questioning Engine
Legal Advisory System v5.0

Generates intelligent questions to fill information gaps.
"""

from typing import Any, Dict, List, Optional

from backend.interfaces import (
    ConversationSession,
    FieldRequirement,
    InfoGap,
    QuestionTemplate,
)


class QuestioningStrategy:
    """Base class for questioning strategies"""

    def prioritize_gaps(self, gaps: List[InfoGap]) -> List[InfoGap]:
        """
        Prioritize information gaps.

        Args:
            gaps: List of information gaps

        Returns:
            Sorted list of gaps by priority
        """
        return sorted(gaps, key=lambda g: (-g.priority, -int(g.required)))


class HighImpactStrategy(QuestioningStrategy):
    """Focus on high-impact required fields first"""

    def prioritize_gaps(self, gaps: List[InfoGap]) -> List[InfoGap]:
        """Prioritize by required fields, then by impact"""
        required = [g for g in gaps if g.required]
        optional = [g for g in gaps if not g.required]

        # Sort required by priority
        required_sorted = sorted(required, key=lambda g: -g.priority)
        optional_sorted = sorted(optional, key=lambda g: -g.priority)

        return required_sorted + optional_sorted


class UserFriendlyStrategy(QuestioningStrategy):
    """Ask simple questions first, building complexity gradually"""

    def prioritize_gaps(self, gaps: List[InfoGap]) -> List[InfoGap]:
        """Prioritize by simplicity (field type complexity)"""
        complexity_order = {"enum": 1, "string": 2, "number": 3, "date": 4}

        return sorted(
            gaps,
            key=lambda g: (
                -int(g.required),  # Required first
                complexity_order.get(g.field_type, 5),  # Simple types first
                -g.priority,  # Then by priority
            ),
        )


class RapidCompletionStrategy(QuestioningStrategy):
    """Ask for all required fields quickly"""

    def prioritize_gaps(self, gaps: List[InfoGap]) -> List[InfoGap]:
        """Get required fields as fast as possible"""
        required = [g for g in gaps if g.required]
        optional = [g for g in gaps if not g.required]

        return required + optional


class DeductiveQuestioningEngine:
    """
    Generates intelligent questions to fill information gaps.

    Uses different strategies to determine which questions to ask
    and in what order.
    """

    def __init__(self):
        """Initialize the questioning engine"""
        self.strategies = {
            "high_impact": HighImpactStrategy(),
            "user_friendly": UserFriendlyStrategy(),
            "rapid": RapidCompletionStrategy(),
        }
        self.default_strategy = "user_friendly"

        # Statistics
        self._stats = {
            "total_questions_generated": 0,
            "strategy_usage": {name: 0 for name in self.strategies.keys()},
        }

    def analyze_gaps(
        self,
        filled_fields: Dict[str, Any],
        field_requirements: List[FieldRequirement],
    ) -> List[InfoGap]:
        """
        Analyze what information is missing.

        Args:
            filled_fields: Currently filled fields
            field_requirements: Required fields from module

        Returns:
            List of InfoGap objects representing missing information
        """
        gaps = []

        for req in field_requirements:
            field_value = filled_fields.get(req.field_name)

            # Check if field is missing or None
            if field_value is None:
                gap = InfoGap(
                    field_name=req.field_name,
                    field_type=req.field_type,
                    description=req.description,
                    priority=1 if req.required else 0,
                    required=req.required,
                    current_value=None,
                    validation_rules=req.validation_rules or {},
                )
                gaps.append(gap)

        return gaps

    def generate_question(
        self,
        session: ConversationSession,
        field_requirements: List[FieldRequirement],
        question_templates: List[QuestionTemplate],
        strategy_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate next question to ask user.

        Args:
            session: Current conversation session
            field_requirements: Field requirements from module
            question_templates: Question templates from module
            strategy_name: Strategy to use (default: user_friendly)

        Returns:
            Question string, or None if no more questions needed
        """
        # Analyze gaps
        gaps = self.analyze_gaps(session.filled_fields, field_requirements)

        if not gaps:
            return None  # No gaps, no questions needed

        # Select strategy
        strategy_name = strategy_name or self.default_strategy
        strategy = self.strategies.get(strategy_name, self.strategies[self.default_strategy])

        # Prioritize gaps
        prioritized_gaps = strategy.prioritize_gaps(gaps)

        if not prioritized_gaps:
            return None

        # Get first gap
        first_gap = prioritized_gaps[0]

        # Find matching template
        template = next(
            (qt for qt in question_templates if qt.field_name == first_gap.field_name),
            None,
        )

        if template:
            question = template.template
        else:
            # Generate fallback question
            question = self._generate_fallback_question(first_gap)

        # Update statistics
        self._stats["total_questions_generated"] += 1
        actual_strategy_used = strategy_name if strategy_name in self.strategies else self.default_strategy
        self._stats["strategy_usage"][actual_strategy_used] += 1

        return question

    def generate_multiple_questions(
        self,
        session: ConversationSession,
        field_requirements: List[FieldRequirement],
        question_templates: List[QuestionTemplate],
        max_questions: int = 3,
        strategy_name: Optional[str] = None,
    ) -> List[str]:
        """
        Generate multiple questions at once.

        Args:
            session: Current conversation session
            field_requirements: Field requirements from module
            question_templates: Question templates from module
            max_questions: Maximum number of questions to return
            strategy_name: Strategy to use

        Returns:
            List of question strings
        """
        # Analyze gaps
        gaps = self.analyze_gaps(session.filled_fields, field_requirements)

        if not gaps:
            return []

        # Select strategy
        strategy_name = strategy_name or self.default_strategy
        strategy = self.strategies.get(strategy_name, self.strategies[self.default_strategy])

        # Prioritize gaps
        prioritized_gaps = strategy.prioritize_gaps(gaps)

        # Generate questions for top gaps
        questions = []
        for gap in prioritized_gaps[:max_questions]:
            # Find matching template
            template = next(
                (qt for qt in question_templates if qt.field_name == gap.field_name),
                None,
            )

            if template:
                question = template.template
            else:
                question = self._generate_fallback_question(gap)

            questions.append(question)

            # Update statistics
            self._stats["total_questions_generated"] += 1

        if questions:
            actual_strategy_used = strategy_name if strategy_name in self.strategies else self.default_strategy
            self._stats["strategy_usage"][actual_strategy_used] += 1

        return questions

    def _generate_fallback_question(self, gap: InfoGap) -> str:
        """
        Generate a fallback question when no template exists.

        Args:
            gap: Information gap

        Returns:
            Generated question string
        """
        field_name_formatted = gap.field_name.replace("_", " ").title()

        if gap.field_type == "enum":
            return f"What is the {field_name_formatted.lower()}?"
        elif gap.field_type == "number":
            return f"Please provide the {field_name_formatted.lower()}."
        elif gap.field_type == "string":
            return f"Could you specify the {field_name_formatted.lower()}?"
        elif gap.field_type == "date":
            return f"What is the {field_name_formatted.lower()}?"
        else:
            return f"Please provide information about {field_name_formatted.lower()}."

    def set_default_strategy(self, strategy_name: str) -> bool:
        """
        Set the default questioning strategy.

        Args:
            strategy_name: Name of strategy to use as default

        Returns:
            True if strategy exists and was set, False otherwise
        """
        if strategy_name in self.strategies:
            self.default_strategy = strategy_name
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get questioning engine statistics"""
        return {
            **self._stats,
            "available_strategies": list(self.strategies.keys()),
            "default_strategy": self.default_strategy,
        }
