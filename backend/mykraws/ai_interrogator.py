"""
AI Interrogator
Legal Advisory System v6.0

Generates natural, conversational questions using AI with:
- Rules of Court as context
- MyKraws personality guidelines
- Conversation history awareness
- Information gap detection
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from backend.common_services.logging_config import get_logger
from backend.hybrid_ai.claude_ai_service import ClaudeAIService

logger = get_logger(__name__)


@dataclass
class InterrogationContext:
    """Context for AI interrogation"""
    module_id: str
    filled_fields: Dict[str, Any]
    required_fields: List[Dict[str, Any]]
    optional_fields: List[Dict[str, Any]]
    rules_of_court: List[Dict[str, str]]
    conversation_history: List[Dict[str, str]]
    personality_guidelines: str


class AIInterrogator:
    """
    AI-driven interrogation engine for Phase 3.

    Generates natural questions by providing AI with:
    - Complete Rules of Court context
    - MyKraws personality guidelines
    - Current information state
    - Conversation history

    The AI asks ONE question at a time, explains WHY it's needed,
    and references specific Rules of Court.
    """

    def __init__(
        self,
        ai_service: ClaudeAIService,
        module_registry,
        personality_manager
    ):
        """
        Initialize AI interrogator.

        Args:
            ai_service: Claude AI service for question generation
            module_registry: Access to module requirements and rules
            personality_manager: MyKraws personality system
        """
        self.ai_service = ai_service
        self.module_registry = module_registry
        self.personality = personality_manager

        logger.info("AIInterrogator initialized")

    async def generate_question(
        self,
        session,
        user_message: str
    ) -> str:
        """
        Generate next natural question based on information gaps.

        This is the core of Phase 3 interrogation.

        Flow:
        1. Extract information from user's latest message
        2. Identify information gaps
        3. Provide Rules of Court + personality to AI
        4. Generate natural question
        5. Return question (will be validated before delivery)

        Args:
            session: Current conversation session
            user_message: User's latest message

        Returns:
            AI-generated question (UNVALIDATED - must be validated before delivery)
        """
        logger.info(f"Generating interrogation question for session {session.session_id[:8]}")

        # 1. Extract information from user message
        extracted_info = await self._extract_information(user_message, session)

        # Update session with extracted info
        for field, value in extracted_info.items():
            session.filled_fields[field] = value
            logger.info(f"Extracted: {field} = {value}")

        # 2. Build interrogation context
        context = await self._build_context(session)

        # 3. Update completeness score
        session.completeness_score = self._calculate_completeness(context)

        # 4. Check if information is sufficient
        if session.completeness_score >= 0.7:
            logger.info(f"Information sufficient: {session.completeness_score:.0%}")
            return self._generate_sufficiency_message(context)

        # 5. Identify next information gap
        next_gap = self._identify_next_gap(context)

        if not next_gap:
            logger.warning("No gaps found but completeness < 70% - using fallback")
            return "Could you tell me more about your case?"

        # 6. Generate natural question using AI
        if self.ai_service and hasattr(self.ai_service, 'client') and self.ai_service.client:
            question = await self._generate_ai_question(context, next_gap)
        else:
            # Fallback: structured question
            logger.warning("AI service not available - using structured question")
            question = self._generate_structured_question(next_gap)

        logger.info(f"Generated question about: {next_gap['field_name']}")
        return question

    async def _extract_information(
        self,
        user_message: str,
        session
    ) -> Dict[str, Any]:
        """
        Extract structured information from user's message.

        Uses pattern extraction + AI extraction (hybrid approach from v5).

        Args:
            user_message: User's message
            session: Current session

        Returns:
            Dict of extracted field values
        """
        # Use pattern extractor for reliable extraction
        from backend.common_services.pattern_extractor import PatternExtractor

        pattern_extractor = PatternExtractor()
        pattern_extracted = pattern_extractor.extract_all(
            user_message,
            context={"current_fields": session.filled_fields}
        )

        # For now, rely on pattern extraction
        # TODO: Add AI-based extraction for fields patterns can't handle
        return pattern_extracted

    async def _build_context(self, session) -> InterrogationContext:
        """
        Build complete context for interrogation.

        Includes:
        - Module requirements (required/optional fields)
        - Rules of Court for the module
        - Conversation history
        - Personality guidelines

        Args:
            session: Current session

        Returns:
            InterrogationContext
        """
        # Get module
        module = self.module_registry.get_module(session.module_id)
        if not module:
            raise ValueError(f"Module {session.module_id} not found")

        # Get field requirements
        field_requirements = module.get_field_requirements()
        required_fields = [
            {
                "field_name": fr.field_name,
                "field_type": fr.field_type,
                "description": fr.description
            }
            for fr in field_requirements if fr.required
        ]
        optional_fields = [
            {
                "field_name": fr.field_name,
                "field_type": fr.field_type,
                "description": fr.description
            }
            for fr in field_requirements if not fr.required
        ]

        # Get Rules of Court for this module
        rules_of_court = self._extract_rules_of_court(module)

        # Format conversation history
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in session.messages[-10:]  # Last 10 messages
        ]

        # Get personality guidelines
        personality_guidelines = self.personality.format_personality_for_prompt()

        return InterrogationContext(
            module_id=session.module_id,
            filled_fields=session.filled_fields,
            required_fields=required_fields,
            optional_fields=optional_fields,
            rules_of_court=rules_of_court,
            conversation_history=conversation_history,
            personality_guidelines=personality_guidelines
        )

    def _extract_rules_of_court(self, module) -> List[Dict[str, Any]]:
        """
        Extract relevant Rules of Court from module's logic tree.

        Per FR-P3-01, provides:
        - Rule citations
        - Rule text (actual legal provisions from logic tree nodes)
        - Logical deductions (WHAT, WHICH, IF-THEN, MODALITY, GIVEN, WHY)

        Args:
            module: Legal module

        Returns:
            List of rule dicts with citation, text, and logical deductions
        """
        rules = []

        # Get logic tree from module registry's tree framework
        try:
            tree_framework = self.module_registry.tree_framework
            logic_tree = tree_framework.get_module_tree(module.metadata.module_id)

            # Extract from each logic tree node
            for node in logic_tree:
                rule = {
                    "citation": node.citation,
                    "node_id": node.node_id,
                    "logical_deductions": {}
                }

                # Extract WHAT (definitions and concepts)
                if node.what:
                    rule["logical_deductions"]["WHAT"] = [
                        w.get("description", str(w)) for w in node.what
                    ]

                # Extract WHICH (categorizations and types)
                if node.which:
                    rule["logical_deductions"]["WHICH"] = [
                        w.get("description", str(w)) for w in node.which
                    ]

                # Extract IF-THEN (conditional rules)
                if node.if_then:
                    rule["logical_deductions"]["IF_THEN"] = [
                        f"IF {it.get('condition', '')} THEN {it.get('consequence', '')}"
                        for it in node.if_then
                    ]

                # Extract MODALITY (requirements: must/may/shall)
                if node.modality:
                    rule["logical_deductions"]["MODALITY"] = [
                        m.get("description", str(m)) for m in node.modality
                    ]

                # Extract GIVEN (contextual conditions)
                if node.given:
                    rule["logical_deductions"]["GIVEN"] = [
                        g.get("description", str(g)) for g in node.given
                    ]

                # Extract WHY (rationale and purpose)
                if node.why:
                    rule["logical_deductions"]["WHY"] = [
                        w.get("description", str(w)) for w in node.why
                    ]

                # Only include nodes with actual logical deductions
                if rule["logical_deductions"]:
                    rules.append(rule)

        except KeyError as e:
            logger.warning(f"Could not load logic tree: {e}")
        except Exception as e:
            logger.error(f"Error extracting rules: {e}")

        return rules

    def _calculate_completeness(self, context: InterrogationContext) -> float:
        """
        Calculate information completeness score.

        Args:
            context: Interrogation context

        Returns:
            Completeness score (0.0 to 1.0)
        """
        total_required = len(context.required_fields)
        if total_required == 0:
            return 1.0

        filled_required = sum(
            1 for field in context.required_fields
            if field["field_name"] in context.filled_fields
        )

        return filled_required / total_required

    def _identify_next_gap(self, context: InterrogationContext) -> Optional[Dict[str, Any]]:
        """
        Identify next information gap to ask about.

        Prioritizes required fields over optional fields.

        Args:
            context: Interrogation context

        Returns:
            Next field to ask about, or None if complete
        """
        # Find first missing required field
        for field in context.required_fields:
            if field["field_name"] not in context.filled_fields:
                return field

        # All required fields filled - check optional fields
        for field in context.optional_fields:
            if field["field_name"] not in context.filled_fields:
                # Only ask about optional field if it's relevant
                if self._is_optional_field_relevant(field, context.filled_fields):
                    return field

        return None

    def _is_optional_field_relevant(
        self,
        field: Dict[str, Any],
        filled_fields: Dict[str, Any]
    ) -> bool:
        """
        Check if optional field is relevant given current information.

        Args:
            field: Field metadata
            filled_fields: Currently filled fields

        Returns:
            True if should ask about this optional field
        """
        field_name = field["field_name"]

        # trial_days only relevant for contested trials
        if field_name == "trial_days":
            return filled_fields.get("case_type") == "contested_trial"

        # complexity_level relevant for high-value or complex cases
        if field_name == "complexity_level":
            claim_amount = filled_fields.get("claim_amount", 0)
            return claim_amount > 100000  # > $100k

        # Default: ask about optional fields
        return True

    async def _generate_ai_question(
        self,
        context: InterrogationContext,
        gap: Dict[str, Any]
    ) -> str:
        """
        Generate natural question using AI.

        Provides complete context to AI including Rules of Court.

        Args:
            context: Full interrogation context
            gap: Information gap to ask about

        Returns:
            AI-generated question (UNVALIDATED)
        """
        # Build comprehensive prompt
        prompt = self._build_interrogation_prompt(context, gap)

        try:
            # Generate question
            response = await self.ai_service.generate_response(
                prompt=prompt,
                conversation_history=[],  # History already in prompt
                max_tokens=300
            )

            return response.strip()

        except Exception as e:
            logger.error(f"AI question generation failed: {e}")
            # Fallback to structured question
            return self._generate_structured_question(gap)

    def _build_interrogation_prompt(
        self,
        context: InterrogationContext,
        gap: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive AI prompt for question generation.

        Args:
            context: Full interrogation context
            gap: Information gap to ask about

        Returns:
            Formatted prompt for AI
        """
        # Format filled fields
        filled_summary = "\n".join(
            f"- {k}: {v}" for k, v in context.filled_fields.items()
        ) if context.filled_fields else "None yet"

        # Format rules for context with logical deductions
        rules_lines = []
        for r in context.rules_of_court:
            rules_lines.append(f"\n{r['citation']}:")
            for deduction_type, deductions in r.get('logical_deductions', {}).items():
                if deductions:
                    rules_lines.append(f"  {deduction_type}:")
                    for deduction in deductions:
                        rules_lines.append(f"    - {deduction}")
        rules_summary = "\n".join(rules_lines) if rules_lines else "No rules loaded"

        # Format recent conversation
        conv_summary = "\n".join(
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in context.conversation_history[-5:]  # Last 5 messages
        ) if context.conversation_history else "This is the first question"

        prompt = f"""{context.personality_guidelines}

CURRENT TASK: Generate ONE natural question to gather the next piece of information.

RULES OF COURT CONTEXT (Singapore):
{rules_summary}

INFORMATION GATHERED SO FAR:
{filled_summary}

RECENT CONVERSATION:
{conv_summary}

NEXT INFORMATION NEEDED:
- Field: {gap['field_name']}
- Type: {gap['field_type']}
- Description: {gap['description']}

YOUR TASK:
Generate ONE natural, conversational question to gather this information.

REQUIREMENTS:
1. Acknowledge the user's previous answer first (if applicable)
2. Ask about the field in natural language (not "What is the {gap['field_name']}?")
3. Explain WHY you need this information
4. Reference the specific Rule of Court that requires it
5. Be warm and friendly (MyKraws personality)
6. Keep it conversational, not formal

EXAMPLE FORMAT:
"Thanks for sharing that! To calculate your costs accurately, I need to know about [natural description].

Under [Rule Citation], the [court/judgment type/etc] affects the cost calculation. [Brief explanation of why it matters].

[Natural question asking for the information]"

Generate your question now:
"""

        return prompt

    def _generate_structured_question(self, gap: Dict[str, Any]) -> str:
        """
        Generate structured question as fallback (when AI unavailable).

        Args:
            gap: Information gap

        Returns:
            Structured question
        """
        field_name = gap["field_name"]
        description = gap["description"]

        # Map field names to natural questions
        question_map = {
            "court_level": "Which court is your matter in - High Court, District Court, or Magistrates Court?",
            "case_type": "What type of judgment or proceeding is this? For example, was it a default judgment, summary judgment, or a contested trial?",
            "claim_amount": "What is the amount claimed or in dispute? This helps determine the appropriate cost scale.",
            "trial_days": "How many days did the trial last? This affects the cost calculation for contested trials.",
            "complexity_level": "How would you describe the complexity of your matter - straightforward, moderate, or complex?"
        }

        if field_name in question_map:
            return question_map[field_name]

        # Generic fallback
        return f"Could you tell me about the {description.lower()}?"

    def _generate_sufficiency_message(self, context: InterrogationContext) -> str:
        """
        Generate message when information is sufficient.

        Args:
            context: Interrogation context

        Returns:
            Message indicating we're ready to analyze
        """
        summary = ", ".join(
            f"{k.replace('_', ' ')}" for k in context.filled_fields.keys()
        )

        return f"Perfect! I have all the information I need about your {summary}. Let me calculate the appropriate costs for you..."
