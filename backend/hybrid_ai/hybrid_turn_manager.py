"""
Hybrid Turn Manager
Legal Advisory System v5.0

Orchestrates the hybrid AI + Logic Tree approach on every conversation turn.

THE HYBRID CYCLE:
1. User sends message
2. AI extracts entities naturally (Pattern + Claude)
3. Logic Tree validates completeness
4. If gaps → AI asks naturally
5. If complete → Logic Tree calculates → AI explains
"""

from typing import Dict, List, Any, Optional
from backend.common_services.gap_detector import GapDetector, ValidationResult
from backend.common_services.pattern_extractor import PatternExtractor
from backend.hybrid_ai.natural_question_generator import NaturalQuestionGenerator
from backend.hybrid_ai.claude_ai_service import ClaudeAIService
from backend.common_services.logging_config import (
    get_logger,
    log_extraction,
    log_conversation_flow,
)

logger = get_logger(__name__)


class HybridTurnManager:
    """
    Manages one turn of the hybrid conversation cycle.

    This is the CORE of the hybrid architecture - combines:
    - AI natural extraction (NATURAL)
    - Logic tree validation (ACCURACY)
    - Natural gap questioning (NATURAL)
    - Accurate calculation (ACCURACY)
    - Natural explanation (NATURAL)
    """

    def __init__(
        self,
        ai_service: ClaudeAIService,
        gap_detector: GapDetector,
        pattern_extractor: PatternExtractor,
        question_generator: NaturalQuestionGenerator,
    ):
        """
        Initialize hybrid turn manager.

        Args:
            ai_service: Claude AI for natural language
            gap_detector: Logic tree gap detection
            pattern_extractor: Fast pattern extraction
            question_generator: Natural question generation
        """
        self.ai_service = ai_service
        self.gap_detector = gap_detector
        self.pattern_extractor = pattern_extractor
        self.question_generator = question_generator

        logger.info("HybridTurnManager initialized")

    async def process_turn(
        self,
        user_message: str,
        module_id: str,
        filled_fields: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Process one turn of the hybrid cycle.

        This is where the magic happens - AI + Logic Tree working together.

        Args:
            user_message: User's natural language message
            module_id: Active module (e.g., "ORDER_21")
            filled_fields: Fields filled so far in session
            conversation_history: Previous messages

        Returns:
            Response dictionary with status, message, etc.
        """
        logger.info(f"🔄 Starting hybrid turn for module={module_id}")
        log_conversation_flow(logger, module_id, "hybrid_turn_start", {"message_length": len(user_message)})

        # ========================================
        # STEP 1: AI NATURAL EXTRACTION
        # ========================================
        extracted_info = await self._extract_naturally(
            user_message, filled_fields, conversation_history
        )

        logger.info(f"📊 Extracted: {extracted_info}")
        log_extraction(logger, user_message, extracted_info)

        # ========================================
        # STEP 2: MERGE WITH SESSION STATE
        # ========================================
        updated_fields = {**filled_fields, **extracted_info}

        logger.info(f"📝 Updated fields: {list(updated_fields.keys())}")

        # ========================================
        # STEP 3: LOGIC TREE VALIDATION
        # ========================================
        validation = self.gap_detector.validate_against_tree(module_id, updated_fields)

        logger.info(
            f"✅ Validation: complete={validation.complete}, "
            f"score={validation.completeness_score:.0%}, "
            f"gaps={len(validation.gaps)}"
        )

        # ========================================
        # STEP 4: DECISION POINT
        # ========================================
        if validation.complete and validation.can_calculate:
            # No gaps - we can calculate!
            return await self._handle_complete(
                validation, updated_fields, conversation_history, module_id
            )
        else:
            # Gaps found - ask naturally
            return await self._handle_gaps(
                validation, updated_fields, conversation_history, extracted_info
            )

    async def _extract_naturally(
        self,
        user_message: str,
        current_fields: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Extract information using AI + pattern matching.

        Combines:
        - Fast pattern extraction (reliable for numbers, courts, etc.)
        - AI extraction (intelligent, contextual, understands intent)

        Returns:
            Extracted field values
        """
        # FAST: Pattern extraction
        pattern_extracted = self.pattern_extractor.extract_all(
            user_message, context={"current_fields": current_fields}
        )

        logger.debug(f"Pattern extracted: {pattern_extracted}")

        # INTELLIGENT: AI extraction
        ai_extracted = await self._ai_extract(
            user_message, current_fields, conversation_history
        )

        logger.debug(f"AI extracted: {ai_extracted}")

        # MERGE: AI takes precedence if both extract same field
        # (AI is more intelligent, but patterns are more reliable for numbers)
        merged = {}

        # Start with pattern extraction (reliable for structured data)
        for field, value in pattern_extracted.items():
            merged[field] = value

        # Override/add with AI extraction (better context understanding)
        for field, value in ai_extracted.items():
            # AI can extract fields patterns can't
            if field not in merged:
                merged[field] = value
            # For amounts, prefer pattern extraction (more reliable)
            elif field == "claim_amount" and field in pattern_extracted:
                merged[field] = pattern_extracted[field]
            # For everything else, AI wins (better context)
            else:
                merged[field] = value

        return merged

    async def _ai_extract(
        self,
        user_message: str,
        current_fields: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Use AI to extract entities from message.

        AI is good at:
        - Understanding context
        - Recognizing intent
        - Handling variations
        - Connecting related information
        """
        # Build extraction prompt
        prompt = f"""You are analyzing a legal cost calculation conversation. Extract structured information from the user's message.

User message: "{user_message}"

Already known: {current_fields}

Extract any of these fields if mentioned:
- court_level: "High Court", "District Court", or "Magistrates Court"
- case_type: "default_judgment", "summary_judgment", "contested_trial", or "assessment_of_damages"
- claim_amount: numeric value in SGD
- claim_nature: "liquidated" or "unliquidated"
- trial_days: number of trial days
- represented_status: "represented" or "unrepresented"
- defendant_count: number of defendants

Return ONLY a JSON object with extracted fields. If nothing is extracted, return {{}}.
DO NOT extract fields we already know unless the user is correcting them.

Example:
User: "High Court contested trial for $50,000"
Response: {{"court_level": "High Court", "case_type": "contested_trial", "claim_amount": 50000}}

Now extract from the user's message:"""

        try:
            # Use AI to extract
            if self.ai_service and hasattr(self.ai_service, 'client') and self.ai_service.client:
                response = await self.ai_service.generate_response(
                    prompt=prompt,
                    conversation_history=[],
                    max_tokens=200,
                )

                # Parse JSON response
                import json
                import re

                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    extracted = json.loads(json_match.group())
                    return extracted
                else:
                    logger.warning(f"AI didn't return valid JSON: {response}")
                    return {}
            else:
                # AI not available - return empty
                return {}

        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return {}

    async def _handle_complete(
        self,
        validation: ValidationResult,
        filled_fields: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        module_id: str,
    ) -> Dict[str, Any]:
        """
        Handle case where we have all information needed.

        Flow:
        1. Summarize understanding
        2. Calculate (this will be done by analysis engine)
        3. Explain naturally
        """
        logger.info("✅ Complete! Ready to calculate")

        # Generate summary
        summary = self.question_generator.generate_summary_message(filled_fields)

        return {
            "status": "complete",
            "message": summary + "\n\nLet me calculate the appropriate costs...",
            "completeness_score": 1.0,
            "next_action": "calculate",
            "filled_fields": filled_fields,
            "validation": validation.to_dict(),
        }

    async def _handle_gaps(
        self,
        validation: ValidationResult,
        filled_fields: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        newly_extracted: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle case where we still have gaps.

        Flow:
        1. Identify what's missing (logic tree)
        2. Generate natural questions (AI)
        3. Return to user
        """
        logger.info(f"❓ Gaps found: {len(validation.gaps)}")

        # Generate natural questions about gaps
        questions = await self.question_generator.generate_gap_questions(
            validation, filled_fields, conversation_history
        )

        return {
            "status": "gathering",
            "message": questions,
            "completeness_score": validation.completeness_score,
            "next_action": "ask_question",
            "filled_fields": filled_fields,
            "newly_extracted": newly_extracted,
            "gaps": [gap.to_dict() for gap in validation.gaps],
            "validation": validation.to_dict(),
        }

    def get_required_fields(self, module_id: str) -> List[str]:
        """
        Get list of fields that may be required for this module.

        Useful for AI to know what to look for.

        Args:
            module_id: Module identifier

        Returns:
            List of field names
        """
        return self.gap_detector.get_required_fields(module_id)
