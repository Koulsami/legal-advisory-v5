"""
Result Explainer
Legal Advisory System v5.0

Generates rich legal explanations for calculation results with:
- Specific Order 21 rule citations
- Legal reasoning for why rules apply
- Special circumstance identification
- Strategic implications

Part of the Hybrid AI + Logic Tree architecture.
"""

from typing import Dict, List, Any, Optional
from backend.common_services.logging_config import get_logger

logger = get_logger(__name__)


class ResultExplainer:
    """
    Explains calculation results with legal citations and strategic guidance.

    This component makes the system not just a calculator, but a legal advisor
    that explains the "why" behind the "what".
    """

    def __init__(self, ai_service):
        """
        Initialize result explainer.

        Args:
            ai_service: ClaudeAIService for natural language generation
        """
        self.ai_service = ai_service
        logger.info("ResultExplainer initialized")

    async def explain_result(
        self,
        calculation_result: Dict[str, Any],
        filled_fields: Dict[str, Any],
        decision_path: Optional[List[str]] = None,
    ) -> str:
        """
        Generate comprehensive explanation of calculation result.

        Args:
            calculation_result: The calculation result from analysis engine
            filled_fields: All case details
            decision_path: Path taken through decision tree (node IDs)

        Returns:
            Rich explanation with citations, reasoning, and implications
        """
        logger.info("Generating result explanation")

        # Extract applicable rules from decision path
        applicable_rules = self._extract_applicable_rules(filled_fields, decision_path)

        # Identify special circumstances
        special_circumstances = self._identify_special_circumstances(filled_fields)

        # Build explanation sections
        sections = []

        # 1. Calculation Summary
        sections.append(self._format_calculation_summary(calculation_result))

        # 2. Legal Basis with Rule Citations
        legal_basis = await self._generate_legal_basis(
            calculation_result,
            filled_fields,
            applicable_rules
        )
        sections.append(legal_basis)

        # 3. Special Circumstances Explanation
        if special_circumstances:
            circumstances_explanation = await self._explain_special_circumstances(
                special_circumstances,
                filled_fields
            )
            sections.append(circumstances_explanation)

        # 4. Strategic Implications
        strategic_implications = self._generate_strategic_implications(
            filled_fields,
            special_circumstances
        )
        sections.append(strategic_implications)

        # Combine all sections
        full_explanation = "\n\n".join(sections)

        logger.info(f"Explanation generated ({len(full_explanation)} chars)")
        return full_explanation

    def _format_calculation_summary(self, calculation_result: Dict[str, Any]) -> str:
        """Format the calculation summary section."""
        # Extract key values
        total = calculation_result.get("total_costs", 0)
        breakdown = calculation_result.get("breakdown", {})

        summary = "**CALCULATION SUMMARY**\n\n"

        # Add breakdown if available
        if breakdown:
            for item, amount in breakdown.items():
                item_name = item.replace("_", " ").title()
                if isinstance(amount, (int, float)):
                    summary += f"• {item_name}: ${amount:,.2f}\n"
                else:
                    summary += f"• {item_name}: {amount}\n"

        summary += f"\n**Total Costs: ${total:,.2f}**"

        return summary

    def _extract_applicable_rules(
        self,
        filled_fields: Dict[str, Any],
        decision_path: Optional[List[str]]
    ) -> List[Dict[str, str]]:
        """
        Extract applicable Order 21 rules based on case details.

        Returns list of rules with citations and descriptions.
        """
        rules = []

        # Rule mapping based on case characteristics
        court_level = filled_fields.get("court_level", "")
        case_type = filled_fields.get("case_type", "")
        claim_nature = filled_fields.get("claim_nature", "")

        # Base rule based on case type
        if case_type == "default_judgment":
            rules.append({
                "citation": "Order 21, Rule 3(2)",
                "title": "Default Judgment Costs",
                "description": "Costs for cases concluded by default judgment"
            })
        elif case_type == "summary_judgment":
            rules.append({
                "citation": "Order 21, Rule 3(3)",
                "title": "Summary Judgment Costs",
                "description": "Costs for cases concluded by summary judgment"
            })
        elif case_type == "contested_trial":
            rules.append({
                "citation": "Order 21, Rule 3(1) & Appendix 1",
                "title": "Contested Trial Costs",
                "description": "Costs for fully contested trials at first instance"
            })

        # Claim nature rules
        if claim_nature == "liquidated":
            rules.append({
                "citation": "Order 21, Appendix 1, Section A",
                "title": "Liquidated Claims",
                "description": "Standard costs for claims of specific sums owed"
            })
        elif claim_nature == "unliquidated":
            rules.append({
                "citation": "Order 21, Appendix 1, Section B",
                "title": "Unliquidated Claims",
                "description": "Costs for claims where damages are assessed by court"
            })

        # Court-specific rules
        if court_level == "High Court":
            rules.append({
                "citation": "Order 21, Appendix 1, Part I",
                "title": "High Court Scale",
                "description": "Cost scales applicable to High Court proceedings"
            })
        elif court_level == "District Court":
            rules.append({
                "citation": "Order 21, Appendix 1, Part II",
                "title": "District Court Scale",
                "description": "Cost scales applicable to District Court proceedings"
            })

        return rules

    def _identify_special_circumstances(
        self,
        filled_fields: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify special circumstances that affect costs.

        Returns list of special circumstances with details.
        """
        circumstances = []

        # ADR refusal
        if filled_fields.get("adr_refused"):
            circumstances.append({
                "type": "adr_refusal",
                "title": "ADR Non-Compliance",
                "impact": "Adverse costs / Cost protection",
                "severity": "significant"
            })

        # Multiple defendants
        defendant_count = filled_fields.get("defendant_count", 1)
        if defendant_count > 1:
            circumstances.append({
                "type": "multiple_defendants",
                "title": f"Multiple Defendants ({defendant_count})",
                "impact": "Additional costs awarded",
                "severity": "moderate"
            })

        # Interlocutory applications
        interlocutory_count = filled_fields.get("interlocutory_applications", 0)
        if interlocutory_count > 0:
            circumstances.append({
                "type": "interlocutory_applications",
                "title": f"Interlocutory Applications ({interlocutory_count})",
                "impact": "Separate costs for each application",
                "severity": "moderate"
            })

        # Extended trial duration
        trial_days = filled_fields.get("trial_days", 0)
        if trial_days > 3:
            circumstances.append({
                "type": "extended_trial",
                "title": f"Extended Trial ({trial_days} days)",
                "impact": "Trial duration uplift applies",
                "severity": "moderate"
            })

        # Urgency/expedition
        if filled_fields.get("urgent"):
            circumstances.append({
                "type": "urgency",
                "title": "Urgent/Expedited Proceedings",
                "impact": "Potential costs uplift",
                "severity": "moderate"
            })

        # Complexity factors
        if filled_fields.get("complex_matter"):
            circumstances.append({
                "type": "complexity",
                "title": "Complex Matter",
                "impact": "Higher costs scale may apply",
                "severity": "significant"
            })

        return circumstances

    async def _generate_legal_basis(
        self,
        calculation_result: Dict[str, Any],
        filled_fields: Dict[str, Any],
        applicable_rules: List[Dict[str, str]]
    ) -> str:
        """
        Generate the legal basis section with AI.

        Explains which rules apply and WHY.
        """
        if not self.ai_service or not hasattr(self.ai_service, 'client') or not self.ai_service.client:
            # Fallback to template-based
            return self._template_legal_basis(applicable_rules)

        # Build prompt for AI
        prompt = f"""You are a legal costs expert explaining a calculation under Singapore's Order 21.

Case Details:
{self._format_case_details(filled_fields)}

Applicable Rules:
{self._format_rules_for_prompt(applicable_rules)}

Task: Write a "LEGAL BASIS" section that:
1. Cites specific Order 21 rules (e.g., "Under Order 21, Rule 4(1)...")
2. Explains WHY each rule applies to this case
3. Uses professional but clear language
4. Connects the rules to the case facts

Format as:
**LEGAL BASIS**

Under [Citation]:
[Clear explanation of why this rule applies and what it means for this case]

Under [Citation]:
[Clear explanation...]

Keep it concise but informative. Use 2-4 paragraphs total."""

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                conversation_history=[],
                max_tokens=600
            )
            return response
        except Exception as e:
            logger.error(f"AI legal basis generation failed: {e}")
            return self._template_legal_basis(applicable_rules)

    def _template_legal_basis(self, applicable_rules: List[Dict[str, str]]) -> str:
        """Fallback template for legal basis."""
        if not applicable_rules:
            return "**LEGAL BASIS**\n\nCosts calculated according to Order 21 of the Rules of Court."

        basis = "**LEGAL BASIS**\n\n"
        for rule in applicable_rules:
            basis += f"**{rule['citation']} - {rule['title']}:**\n"
            basis += f"{rule['description']}\n\n"

        return basis.strip()

    async def _explain_special_circumstances(
        self,
        special_circumstances: List[Dict[str, Any]],
        filled_fields: Dict[str, Any]
    ) -> str:
        """
        Explain special circumstances in detail.

        This is where we explain things like ADR refusal consequences.
        """
        if not special_circumstances:
            return ""

        explanations = []

        for circumstance in special_circumstances:
            circ_type = circumstance["type"]

            if circ_type == "adr_refusal":
                explanation = self._explain_adr_refusal(filled_fields)
            elif circ_type == "multiple_defendants":
                explanation = self._explain_multiple_defendants(filled_fields)
            elif circ_type == "interlocutory_applications":
                explanation = self._explain_interlocutory_applications(filled_fields)
            elif circ_type == "extended_trial":
                explanation = self._explain_extended_trial(filled_fields)
            else:
                explanation = f"**{circumstance['title']}:**\n{circumstance['impact']}"

            explanations.append(explanation)

        return "**SPECIAL CIRCUMSTANCES**\n\n" + "\n\n".join(explanations)

    def _explain_adr_refusal(self, filled_fields: Dict[str, Any]) -> str:
        """Explain ADR refusal consequences - IMPORTANT feature."""
        return """**Under Order 21, Rule 4(1) - ADR Non-Compliance:**

The opposing party's refusal to participate in Alternative Dispute Resolution (ADR) triggers adverse cost consequences under Order 21, Rule 4.

**Implications for You:**
• You are entitled to claim ADVERSE COSTS - typically 10-15% above the standard scale
• This reflects the court's view that ADR refusal is unreasonable conduct

**Under Order 21, Rule 4(2) - Cost Protection:**
If the opposing party ultimately succeeds in their case, the court has discretion to award them NO COSTS or reduced costs due to their ADR refusal. This protects you from bearing their full legal costs even if you lose.

**Important:** Courts view ADR refusal very unfavorably. This significantly strengthens your costs position."""

    def _explain_multiple_defendants(self, filled_fields: Dict[str, Any]) -> str:
        """Explain multiple defendants impact."""
        count = filled_fields.get("defendant_count", 0)
        additional = count - 1

        return f"""**Under Order 21, Appendix 1, Note 5 - Multiple Defendants:**

With {count} defendants involved, additional costs are awarded to reflect the increased complexity and work required. The standard provision adds approximately $500-1,000 per additional defendant beyond the first.

**Implications:**
• Total additional costs for {additional} extra defendant(s)
• Each defendant's representation status may further affect costs
• If defendants have separate counsel, costs may increase
• Joint and several liability for costs typically applies"""

    def _explain_interlocutory_applications(self, filled_fields: Dict[str, Any]) -> str:
        """Explain interlocutory applications costs."""
        count = filled_fields.get("interlocutory_applications", 0)

        return f"""**Under Order 21, Appendix 1, Section C - Interlocutory Applications:**

The {count} interlocutory application(s) filed during proceedings attract separate costs. Each substantive application typically costs $1,500-2,000 depending on complexity.

**Under Order 21, Rule 7 - Costs Follow the Event:**
If you succeeded in your interlocutory applications, you're entitled to recover these costs even if they were not specifically reserved at the time.

**Types of Applications:**
• Summary judgment applications: Higher costs range
• Discovery/interrogatory applications: Standard costs
• Costs may be on indemnity basis if application was clearly unreasonable"""

    def _explain_extended_trial(self, filled_fields: Dict[str, Any]) -> str:
        """Explain extended trial duration impact."""
        days = filled_fields.get("trial_days", 0)

        return f"""**Trial Duration Uplift - {days} Days:**

Trials exceeding 3 days attract an uplift to reflect the additional work and preparation required. The standard uplift is approximately 15-25% for trials of {days} days.

This recognizes the increased complexity, witness management, and sustained advocacy required for longer trials."""

    def _generate_strategic_implications(
        self,
        filled_fields: Dict[str, Any],
        special_circumstances: List[Dict[str, Any]]
    ) -> str:
        """
        Generate strategic implications and practical guidance.
        """
        implications = []

        # ADR-specific implications
        if any(c["type"] == "adr_refusal" for c in special_circumstances):
            implications.extend([
                "Document all ADR offers and rejections with dates",
                "Maintain correspondence showing reasonable ADR attempts",
                "This strengthens your costs application significantly"
            ])

        # Multiple defendants
        if filled_fields.get("defendant_count", 1) > 1:
            implications.extend([
                "Confirm each defendant's representation status",
                "Joint and several liability means you can recover from any defendant",
                "Consider separate costs orders if defendants had conflicting positions"
            ])

        # General strategic points
        implications.extend([
            "Prepare detailed breakdown of costs for assessment",
            "Contemporaneous time records strengthen costs claims",
            "Court has discretion - reasonableness is key"
        ])

        if not implications:
            implications = ["Ensure all costs claimed are reasonable and properly documented"]

        strategic_section = "**STRATEGIC IMPLICATIONS**\n\n"
        for implication in implications:
            strategic_section += f"• {implication}\n"

        return strategic_section.strip()

    # Helper methods

    def _format_case_details(self, filled_fields: Dict[str, Any]) -> str:
        """Format case details for AI prompt."""
        details = []
        for key, value in filled_fields.items():
            if value:
                details.append(f"• {key.replace('_', ' ').title()}: {value}")
        return "\n".join(details) if details else "No details provided"

    def _format_rules_for_prompt(self, rules: List[Dict[str, str]]) -> str:
        """Format rules for AI prompt."""
        formatted = []
        for rule in rules:
            formatted.append(f"• {rule['citation']}: {rule['description']}")
        return "\n".join(formatted) if formatted else "General Order 21 provisions"
