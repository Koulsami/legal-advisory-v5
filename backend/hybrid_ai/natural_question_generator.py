"""
Natural Gap Question Generator
Legal Advisory System v5.0

Converts logic tree gaps into natural, conversational questions.
Part of the Hybrid AI + Logic Tree architecture.
"""

from typing import Dict, List, Any, Optional
from backend.common_services.gap_detector import Gap, ValidationResult
from backend.common_services.logging_config import get_logger

logger = get_logger(__name__)


class NaturalQuestionGenerator:
    """
    Generates natural questions about gaps identified by logic tree.

    This bridges the ACCURACY layer (logic tree gaps) with the
    NATURAL layer (conversational AI).
    """

    def __init__(self, ai_service):
        """
        Initialize question generator.

        Args:
            ai_service: ClaudeAIService instance for natural language generation
        """
        self.ai_service = ai_service

    async def generate_gap_questions(
        self,
        validation_result: ValidationResult,
        filled_fields: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
    ) -> str:
        """
        Generate natural questions about gaps.

        Args:
            validation_result: Result from gap detection
            filled_fields: Fields filled so far
            conversation_history: Previous messages

        Returns:
            Natural language question(s) about gaps
        """
        gaps = validation_result.gaps

        if not gaps:
            return "I have all the information I need. Let me calculate..."

        logger.info(f"Generating natural questions for {len(gaps)} gap(s)")

        # Use AI to generate natural questions
        if self.ai_service and hasattr(self.ai_service, "client") and self.ai_service.client:
            return await self._ai_generate_questions(
                gaps, filled_fields, conversation_history
            )
        else:
            # Fallback to template-based generation
            return self._template_generate_questions(gaps, filled_fields)

    async def _ai_generate_questions(
        self,
        gaps: List[Gap],
        filled_fields: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
    ) -> str:
        """
        Use AI to generate natural questions.

        This creates questions that:
        - Acknowledge what user already provided
        - Ask about gaps conversationally
        - Sound professional and natural
        """
        # Build context summary
        context_summary = self._build_context_summary(filled_fields)

        # Build gap summary
        gap_summary = self._build_gap_summary(gaps)

        # Create prompt for AI
        prompt = f"""You are a professional legal cost calculator assistant helping calculate costs under the Singapore Rules of Court, Order 21.

The user has provided the following information:
{context_summary}

To calculate the appropriate costs accurately, you need to know:
{gap_summary}

Your task: Generate a natural, professional response that:
1. Briefly acknowledges what the user has told you (1 sentence)
2. Asks about the missing information in a conversational way
3. Explains WHY you need this information (relates to cost calculation)
4. Keeps it concise and friendly

DO NOT:
- Repeat information the user already provided
- Sound like a form or questionnaire
- Use bullet points for the questions themselves (narrative is fine)
- Ask for information we already have

Example good response:
"Thank you for that information about your High Court case. To ensure I calculate the costs correctly under Order 21, I need to understand a bit more about how the proceedings went. Was this a contested trial, or was it resolved through default or summary judgment? This affects which cost schedule applies."

Example bad response:
"Please provide:
1. Case type
2. Trial duration
Thank you."

Generate the response now (just the response text, no preamble):"""

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                conversation_history=[],  # Don't include history in this call
                max_tokens=300,
            )

            logger.info(f"AI generated question: {response[:100]}...")
            return response

        except Exception as e:
            logger.error(f"AI question generation failed: {e}")
            return self._template_generate_questions(gaps, filled_fields)

    def _template_generate_questions(
        self, gaps: List[Gap], filled_fields: Dict[str, Any]
    ) -> str:
        """
        Fallback template-based question generation.

        Used when AI is not available or fails.
        """
        # Build acknowledgment
        if filled_fields:
            acknowledgment = self._build_acknowledgment(filled_fields)
        else:
            acknowledgment = "I'd be happy to help you calculate legal costs under Order 21."

        # Build questions
        questions = []
        for gap in gaps:
            question = self._gap_to_question(gap)
            questions.append(question)

        if len(questions) == 1:
            return f"{acknowledgment}\n\n{questions[0]}"
        else:
            questions_text = "\n\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
            return f"{acknowledgment}\n\nTo calculate the appropriate costs, I need to know:\n\n{questions_text}"

    def _build_context_summary(self, filled_fields: Dict[str, Any]) -> str:
        """Build a natural summary of what we know."""
        if not filled_fields:
            return "Nothing yet - this is the start of our conversation."

        parts = []
        for field, value in filled_fields.items():
            parts.append(f"• {self._field_to_natural(field)}: {value}")

        return "\n".join(parts)

    def _build_gap_summary(self, gaps: List[Gap]) -> str:
        """Build a summary of gaps."""
        parts = []
        for gap in gaps:
            parts.append(f"• {gap.field_name} ({gap.description})")

        return "\n".join(parts)

    def _build_acknowledgment(self, filled_fields: Dict[str, Any]) -> str:
        """Build natural acknowledgment of what user provided."""
        # Get most significant fields
        significant = []

        if "court_level" in filled_fields:
            significant.append(f"{filled_fields['court_level']}")

        if "case_type" in filled_fields:
            case_type = filled_fields['case_type'].replace('_', ' ')
            significant.append(f"{case_type}")

        if "claim_amount" in filled_fields:
            amount = filled_fields['claim_amount']
            significant.append(f"${amount:,.0f} claim")

        if significant:
            summary = " ".join(significant)
            return f"Thank you for providing information about your {summary}."
        else:
            return "Thank you for that information."

    def _gap_to_question(self, gap: Gap) -> str:
        """Convert a gap to a natural question."""
        field_questions = {
            "court_level": "Which court is handling this case - High Court, District Court, or Magistrates Court?",
            "case_type": "How was the case resolved? For example, was it a contested trial, default judgment, or summary judgment?",
            "claim_amount": "What is the total claim amount in Singapore dollars?",
            "trial_days": "How many days did the trial last?",
            "claim_nature": "Was the claim for a liquidated sum (a specific amount owed) or unliquidated damages (assessed by the court)?",
            "represented_status": "Were the defendants represented by lawyers?",
            "defendant_count": "How many defendants were involved in the case?",
        }

        if gap.field_name in field_questions:
            return field_questions[gap.field_name]
        else:
            # Generic question
            return f"Could you please provide information about {gap.field_name.replace('_', ' ')}?"

    def _field_to_natural(self, field_name: str) -> str:
        """Convert field name to natural language."""
        natural_names = {
            "court_level": "Court",
            "case_type": "Case type",
            "claim_amount": "Claim amount",
            "trial_days": "Trial duration",
            "claim_nature": "Claim nature",
            "represented_status": "Representation",
            "defendant_count": "Number of defendants",
        }

        return natural_names.get(field_name, field_name.replace('_', ' ').title())

    def generate_summary_message(self, filled_fields: Dict[str, Any]) -> str:
        """
        Generate a summary of what we understand so far.

        Useful for confirming with the user before calculating.
        """
        if not filled_fields:
            return "I don't have any information yet."

        parts = ["Based on our conversation, I understand:"]

        # Order fields logically
        field_order = [
            "court_level",
            "case_type",
            "claim_amount",
            "claim_nature",
            "trial_days",
            "defendant_count",
            "represented_status",
        ]

        for field in field_order:
            if field in filled_fields:
                natural_name = self._field_to_natural(field)
                value = filled_fields[field]

                # Format value nicely
                if field == "claim_amount":
                    value_str = f"${value:,.0f}"
                elif field == "trial_days":
                    value_str = f"{value} day{'s' if value != 1 else ''}"
                else:
                    value_str = str(value).replace('_', ' ')

                parts.append(f"• {natural_name}: {value_str}")

        return "\n".join(parts)
