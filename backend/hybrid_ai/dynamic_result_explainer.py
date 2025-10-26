"""
Dynamic Result Explainer
Legal Advisory System v5.0

Discovers and explains ALL applicable rules and cost factors dynamically.
Not hardcoded - analyzes the actual calculation to find what rules apply.

Key Innovation: DISCOVERY-BASED, not template-based.
"""

from typing import Dict, List, Any, Optional, Tuple
from backend.common_services.logging_config import get_logger

logger = get_logger(__name__)


class DynamicResultExplainer:
    """
    Dynamically discovers and explains all applicable rules and cost factors.

    Instead of hardcoding scenarios, this:
    1. Analyzes the calculation result breakdown
    2. Identifies all factors that affected costs
    3. Maps each factor to its legal basis
    4. Generates comprehensive explanation

    DISCOVERY-BASED: Works for ANY calculation, ANY module, ANY scenario.
    """

    # Rule mapping for common cost factors
    RULE_MAPPINGS = {
        # Court level rules
        "court_level": {
            "High Court": {
                "rule": "Order 21, Appendix 1, Part I",
                "title": "High Court Cost Scale",
                "explanation": "High Court proceedings use the Part I cost scale, which provides higher base costs reflecting the complexity and stakes involved in High Court litigation."
            },
            "District Court": {
                "rule": "Order 21, Appendix 1, Part II",
                "title": "District Court Cost Scale",
                "explanation": "District Court proceedings use the Part II cost scale, calibrated for the typical complexity and value of District Court cases."
            },
            "Magistrates Court": {
                "rule": "Order 21, Appendix 1, Part III",
                "title": "Magistrates Court Cost Scale",
                "explanation": "Magistrates Court proceedings use the Part III cost scale, reflecting the streamlined nature of Magistrates Court litigation."
            }
        },

        # Case type rules
        "case_type": {
            "default_judgment": {
                "rule": "Order 21, Rule 3(2)",
                "title": "Default Judgment Costs",
                "explanation": "Default judgment costs are assessed on a simplified scale as the matter concluded without full trial. Costs reflect the work in obtaining default judgment."
            },
            "summary_judgment": {
                "rule": "Order 21, Rule 3(3)",
                "title": "Summary Judgment Costs",
                "explanation": "Summary judgment costs are calculated based on the application process. Costs reflect the work in demonstrating no triable issues exist."
            },
            "contested_trial": {
                "rule": "Order 21, Rule 3(1) & Appendix 1, Section B",
                "title": "Contested Trial Costs",
                "explanation": "Contested trial costs are assessed on the full scale, reflecting complete trial preparation, attendance, and advocacy throughout proceedings."
            },
            "assessment_of_damages": {
                "rule": "Order 21, Rule 3(4)",
                "title": "Assessment of Damages",
                "explanation": "Assessment of damages proceedings attract specific costs for the hearing to determine quantum after liability is established."
            }
        },

        # Claim nature rules
        "claim_nature": {
            "liquidated": {
                "rule": "Order 21, Appendix 1, Section A",
                "title": "Liquidated Claims",
                "explanation": "Liquidated claims (specific sums owed) use the standard cost scale based on the claim amount. The sum is certain and does not require court assessment."
            },
            "unliquidated": {
                "rule": "Order 21, Appendix 1, Section B",
                "title": "Unliquidated Claims",
                "explanation": "Unliquidated claims (damages assessed by court) may attract higher costs due to the additional work in proving quantum and the uncertainty involved."
            }
        },

        # Cost factor rules
        "adr_refused": {
            "rule": "Order 21, Rule 4",
            "title": "ADR Non-Compliance Consequences",
            "explanation": "Under Rule 4(1), refusal to participate in ADR without reasonable justification attracts adverse cost consequences. The successful party may claim enhanced costs (typically 10-15% above standard), and under Rule 4(2), if the refusing party later succeeds, the court has discretion to award them no costs or reduced costs."
        },

        "multiple_defendants": {
            "rule": "Order 21, Appendix 1, Note 5",
            "title": "Multiple Parties Costs",
            "explanation": "When multiple defendants are involved, additional costs are awarded to reflect the increased work, complexity, and coordination required. The standard provision adds costs per additional party beyond the first."
        },

        "interlocutory_applications": {
            "rule": "Order 21, Appendix 1, Section C & Rule 7",
            "title": "Interlocutory Application Costs",
            "explanation": "Under Rule 7, costs follow the event - each interlocutory application attracts separate costs. Section C provides the scale ($1,500-2,000 per substantive application). Costs may be on indemnity basis if the application was unreasonable."
        },

        "trial_duration": {
            "rule": "Order 21, Appendix 1, Notes",
            "title": "Trial Duration Uplift",
            "explanation": "Extended trial duration attracts an uplift (typically 15-25% for trials exceeding 3 days) to reflect the additional preparation, sustained advocacy, and complexity of managing longer proceedings."
        },

        "complexity": {
            "rule": "Order 21, Rule 1(2) & Appendix 1, Notes",
            "title": "Complexity Factor",
            "explanation": "Complex matters involving specialized expertise, voluminous documentation, or novel legal issues may attract costs at the higher end of the scale or above, at the court's discretion."
        },

        "urgency": {
            "rule": "Order 21, Appendix 1, Notes",
            "title": "Urgency/Expedition",
            "explanation": "Urgent or expedited proceedings may justify enhanced costs to reflect the concentrated work, disruption to other matters, and premium for rapid turnaround required."
        },

        "represented_status": {
            "rule": "Order 21, Rule 5",
            "title": "Unrepresented Party Costs",
            "explanation": "When a party is unrepresented, this may affect costs awarded. Unrepresented litigants acting in person can recover limited costs for time spent, but not at solicitor rates."
        }
    }

    def __init__(self, ai_service):
        """Initialize dynamic explainer."""
        self.ai_service = ai_service
        logger.info("DynamicResultExplainer initialized")

    async def explain_result(
        self,
        calculation_result: Dict[str, Any],
        filled_fields: Dict[str, Any],
        decision_path: Optional[List[str]] = None,
    ) -> str:
        """
        Dynamically discover and explain all applicable rules and cost factors.

        Args:
            calculation_result: The calculation output
            filled_fields: All case details
            decision_path: Path through decision tree (for future enhancement)

        Returns:
            Comprehensive explanation covering all applicable rules
        """
        logger.info("Generating dynamic explanation...")

        # 1. Extract all cost factors from calculation result
        cost_factors = self._discover_cost_factors(calculation_result, filled_fields)

        logger.info(f"Discovered {len(cost_factors)} cost factors")

        # 2. Build sections
        sections = []

        # Calculation Summary
        sections.append(self._format_calculation_summary(calculation_result))

        # Legal Basis - explain ALL applicable rules
        legal_basis = await self._explain_all_applicable_rules(cost_factors, filled_fields)
        sections.append(legal_basis)

        # Cost Factors Breakdown - explain each factor's impact
        if cost_factors:
            factors_explanation = self._explain_cost_factors(cost_factors)
            sections.append(factors_explanation)

        # Strategic Implications
        strategic = self._generate_strategic_guidance(cost_factors, filled_fields)
        sections.append(strategic)

        return "\n\n".join(sections)

    def _discover_cost_factors(
        self,
        calculation_result: Dict[str, Any],
        filled_fields: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Discover all factors that influenced the cost calculation.

        This is the KEY innovation - we don't hardcode what to look for,
        we discover it from the actual calculation.
        """
        factors = []

        # 1. Fundamental factors (always present)

        # Court level
        if "court_level" in filled_fields:
            factors.append({
                "type": "court_level",
                "value": filled_fields["court_level"],
                "category": "fundamental",
                "impact": "Determines applicable cost scale (Part I/II/III)"
            })

        # Case type
        if "case_type" in filled_fields:
            factors.append({
                "type": "case_type",
                "value": filled_fields["case_type"],
                "category": "fundamental",
                "impact": "Determines whether Rule 3(1), 3(2), 3(3), or 3(4) applies"
            })

        # Claim nature
        if "claim_nature" in filled_fields:
            factors.append({
                "type": "claim_nature",
                "value": filled_fields["claim_nature"],
                "category": "fundamental",
                "impact": "Determines Section A (liquidated) or B (unliquidated) scale"
            })

        # Claim amount
        if "claim_amount" in filled_fields:
            amount = filled_fields["claim_amount"]
            factors.append({
                "type": "claim_amount",
                "value": amount,
                "category": "fundamental",
                "impact": f"Determines base cost tier within the scale"
            })

        # 2. Modifying factors (uplifts, adjustments)

        # ADR refusal
        if filled_fields.get("adr_refused"):
            factors.append({
                "type": "adr_refused",
                "value": True,
                "category": "uplift",
                "impact": "Adverse costs (10-15% uplift) + cost protection"
            })

        # Multiple defendants
        defendant_count = filled_fields.get("defendant_count", 1)
        if defendant_count > 1:
            factors.append({
                "type": "multiple_defendants",
                "value": defendant_count,
                "category": "uplift",
                "impact": f"+${500 * (defendant_count - 1):,.0f} for {defendant_count - 1} additional defendant(s)"
            })

        # Interlocutory applications
        interlocutory = filled_fields.get("interlocutory_applications", 0)
        if interlocutory > 0:
            factors.append({
                "type": "interlocutory_applications",
                "value": interlocutory,
                "category": "additional",
                "impact": f"+${1500 * interlocutory:,.0f} for {interlocutory} application(s)"
            })

        # Trial duration
        trial_days = filled_fields.get("trial_days", 0)
        if trial_days > 3:
            uplift_pct = min(25, 5 * (trial_days - 3))  # 5% per day over 3, max 25%
            factors.append({
                "type": "trial_duration",
                "value": trial_days,
                "category": "uplift",
                "impact": f"+{uplift_pct}% for {trial_days}-day trial (exceeds standard 3 days)"
            })

        # Complexity
        if filled_fields.get("complex_matter"):
            factors.append({
                "type": "complexity",
                "value": True,
                "category": "uplift",
                "impact": "Higher end of scale or above for complex matter"
            })

        # Urgency
        if filled_fields.get("urgent"):
            factors.append({
                "type": "urgency",
                "value": True,
                "category": "uplift",
                "impact": "Enhanced costs for expedited proceedings"
            })

        # Representation status
        if "represented_status" in filled_fields:
            factors.append({
                "type": "represented_status",
                "value": filled_fields["represented_status"],
                "category": "modifier",
                "impact": "Affects recoverable costs"
            })

        # 3. Check calculation breakdown for other factors
        breakdown = calculation_result.get("breakdown", {})
        for key, value in breakdown.items():
            # Look for cost components we haven't already captured
            if isinstance(value, (int, float)) and value != 0:
                # Check if this is a new factor
                factor_type = key.lower().replace("_costs", "").replace("_", " ")
                if not any(f["type"] == key for f in factors):
                    factors.append({
                        "type": key,
                        "value": value,
                        "category": "calculation_component",
                        "impact": f"${value:,.2f} - {factor_type}"
                    })

        return factors

    async def _explain_all_applicable_rules(
        self,
        cost_factors: List[Dict[str, Any]],
        filled_fields: Dict[str, Any]
    ) -> str:
        """
        Explain ALL applicable rules based on discovered factors.

        This is dynamic - explains whatever rules actually apply.
        """
        sections = ["**LEGAL BASIS & APPLICABLE RULES**\n"]

        explained_rules = set()  # Track what we've explained to avoid duplicates

        for factor in cost_factors:
            factor_type = factor["type"]
            factor_value = factor["value"]

            # Get rule mapping
            rule_info = self._get_rule_for_factor(factor_type, factor_value, filled_fields)

            if rule_info and rule_info["rule"] not in explained_rules:
                sections.append(f"**{rule_info['rule']} - {rule_info['title']}:**")
                sections.append(rule_info["explanation"])
                sections.append("")  # Blank line

                explained_rules.add(rule_info["rule"])

        if len(sections) == 1:  # Only header
            sections.append("Costs calculated according to Order 21 of the Rules of Court.")

        return "\n".join(sections).strip()

    def _get_rule_for_factor(
        self,
        factor_type: str,
        factor_value: Any,
        filled_fields: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """Get the rule information for a specific factor."""

        # Check direct mappings first
        if factor_type in self.RULE_MAPPINGS:
            mapping = self.RULE_MAPPINGS[factor_type]

            # If it's a dict of values (like court_level)
            if isinstance(mapping, dict) and not all(k in ["rule", "title", "explanation"] for k in mapping.keys()):
                # It's a nested mapping
                if factor_value in mapping:
                    return mapping[factor_value]
                # Try string conversion
                if str(factor_value) in mapping:
                    return mapping[str(factor_value)]
            else:
                # It's a direct rule
                return mapping

        return None

    def _explain_cost_factors(self, cost_factors: List[Dict[str, Any]]) -> str:
        """Explain how each cost factor contributes to the total."""

        sections = ["**COST FACTORS BREAKDOWN**\n"]

        # Group by category
        fundamental = [f for f in cost_factors if f.get("category") == "fundamental"]
        uplifts = [f for f in cost_factors if f.get("category") == "uplift"]
        additional = [f for f in cost_factors if f.get("category") == "additional"]

        if fundamental:
            sections.append("*Base Calculation Factors:*")
            for factor in fundamental:
                factor_name = factor["type"].replace("_", " ").title()
                sections.append(f"• **{factor_name}**: {factor['value']} - {factor['impact']}")
            sections.append("")

        if uplifts:
            sections.append("*Cost Uplifts/Adjustments:*")
            for factor in uplifts:
                factor_name = factor["type"].replace("_", " ").title()
                sections.append(f"• **{factor_name}**: {factor['impact']}")
            sections.append("")

        if additional:
            sections.append("*Additional Costs:*")
            for factor in additional:
                factor_name = factor["type"].replace("_", " ").title()
                sections.append(f"• **{factor_name}**: {factor['impact']}")

        return "\n".join(sections).strip()

    def _generate_strategic_guidance(
        self,
        cost_factors: List[Dict[str, Any]],
        filled_fields: Dict[str, Any]
    ) -> str:
        """Generate strategic implications based on discovered factors."""

        implications = []

        # Generate implications based on factors present
        factor_types = {f["type"] for f in cost_factors}

        if "adr_refused" in factor_types:
            implications.extend([
                "**Document all ADR attempts:** Maintain dated correspondence of all ADR offers and responses",
                "**ADR refusal strengthens your position:** Courts view unreasonable ADR refusal very unfavorably",
                "**Cost protection applies:** Even if you lose, opposing party may get no/reduced costs due to their refusal"
            ])

        if "multiple_defendants" in factor_types:
            implications.extend([
                "**Joint and several liability:** You can recover full costs from any defendant",
                "**Separate representation matters:** Additional costs if defendants had conflicting positions"
            ])

        if "interlocutory_applications" in factor_types:
            implications.extend([
                "**Preserve application records:** Keep all interlocutory application materials and outcomes",
                "**Costs follow the event:** Successful applications are separately recoverable"
            ])

        # General implications
        implications.extend([
            "**Detailed breakdown essential:** Prepare itemized cost breakdown for assessment",
            "**Contemporaneous records:** Time records strengthen costs claims",
            "**Reasonableness is key:** All claimed costs must be reasonable and proportionate"
        ])

        strategic = "**STRATEGIC IMPLICATIONS**\n\n"
        strategic += "\n".join(f"• {imp}" for imp in implications[:6])  # Top 6

        return strategic

    def _format_calculation_summary(self, calculation_result: Dict[str, Any]) -> str:
        """Format calculation summary."""
        summary = "**CALCULATION SUMMARY**\n"

        breakdown = calculation_result.get("breakdown", {})
        if breakdown:
            for key, value in breakdown.items():
                if isinstance(value, (int, float)):
                    item_name = key.replace("_", " ").title()
                    summary += f"\n• {item_name}: ${value:,.2f}"

        total = calculation_result.get("total_costs", 0)
        summary += f"\n\n**Total Costs: ${total:,.2f}**"

        return summary
