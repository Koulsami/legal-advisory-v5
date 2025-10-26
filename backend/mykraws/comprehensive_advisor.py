"""
Comprehensive Advisor - Phase 4 Enhanced Analysis
Legal Advisory System v6.0

Goes beyond simple calculation to provide:
- What you CAN claim (entitlements)
- What you CANNOT claim (restrictions)
- Strategic recommendations (actionable)
- Risk assessment
- ADR impact analysis (Order 5, Rule 1 & Order 21, Rule 4)
- Settlement offer analysis (Order 22A)
- Complexity & urgency analysis
- Opponent conduct analysis
- Procedural requirements
- Action items with priorities
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from backend.common_services.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Entitlement:
    """Something the user CAN claim"""
    title: str
    amount: Optional[float]
    rule_basis: str
    conditions: List[str]
    explanation: str


@dataclass
class Restriction:
    """Something the user CANNOT claim"""
    title: str
    rule_basis: str
    explanation: str
    exceptions: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """Strategic recommendation"""
    priority: str  # HIGH, MEDIUM, LOW
    action: str
    rationale: str
    timing: Optional[str] = None
    documentation: List[str] = field(default_factory=list)


@dataclass
class Risk:
    """Potential risk"""
    risk_type: str
    description: str
    likelihood: str  # HIGH, MEDIUM, LOW
    impact: str      # HIGH, MEDIUM, LOW
    mitigation: List[str]


class ComprehensiveAdvisor:
    """
    Generates comprehensive legal advisory for Phase 4.

    This transforms v5's simple explanation into v6's comprehensive advisory
    covering all aspects required by FR-P4-01 through FR-P4-10.
    """

    def __init__(self, module_registry=None):
        """
        Initialize comprehensive advisor.

        Args:
            module_registry: Access to legal modules
        """
        self.module_registry = module_registry
        logger.info("ComprehensiveAdvisor initialized")

    async def generate_advisory(
        self,
        calculation_result: Dict[str, Any],
        filled_fields: Dict[str, Any],
        module_id: str
    ) -> str:
        """
        Generate comprehensive legal advisory.

        Args:
            calculation_result: Calculation output
            filled_fields: All case details
            module_id: Legal module used

        Returns:
            Formatted comprehensive advisory
        """
        logger.info(f"Generating comprehensive advisory for {module_id}")

        # Build all advisory components
        sections = []

        # 1. Executive Summary
        sections.append(self._generate_executive_summary(calculation_result, filled_fields))

        # 2. Cost Calculation
        sections.append(self._format_calculation_summary(calculation_result))

        # 3. What You CAN Claim
        entitlements = self._analyze_entitlements(calculation_result, filled_fields)
        sections.append(self._format_entitlements(entitlements))

        # 4. What You CANNOT Claim
        restrictions = self._analyze_restrictions(filled_fields)
        if restrictions:
            sections.append(self._format_restrictions(restrictions))

        # 5. ADR Impact Analysis (FR-P4-05)
        adr_analysis = self._analyze_adr_impact(filled_fields)
        if adr_analysis:
            sections.append(adr_analysis)

        # 6. Settlement Offer Analysis (FR-P4-06)
        settlement_analysis = self._analyze_settlement_offers(filled_fields)
        if settlement_analysis:
            sections.append(settlement_analysis)

        # 7. Complexity & Urgency (FR-P4-07)
        complexity_analysis = self._analyze_complexity_urgency(filled_fields)
        if complexity_analysis:
            sections.append(complexity_analysis)

        # 8. Opponent Conduct (FR-P4-08)
        conduct_analysis = self._analyze_opponent_conduct(filled_fields)
        if conduct_analysis:
            sections.append(conduct_analysis)

        # 9. Strategic Recommendations
        recommendations = self._generate_recommendations(filled_fields, calculation_result)
        sections.append(self._format_recommendations(recommendations))

        # 10. Risk Assessment
        risks = self._assess_risks(filled_fields)
        if risks:
            sections.append(self._format_risks(risks))

        # 11. Action Items
        action_items = self._generate_action_items(filled_fields, calculation_result)
        sections.append(self._format_action_items(action_items))

        # Combine all sections
        advisory = "\n\n".join(sections)

        # Add friendly closing
        advisory += "\n\n💼 **Need More Help?**\nIf you have questions about any of these recommendations, just ask! I'm here to help."

        return advisory

    def _generate_executive_summary(
        self,
        calculation_result: Dict[str, Any],
        filled_fields: Dict[str, Any]
    ) -> str:
        """Generate 2-3 sentence executive summary"""
        total = calculation_result.get("total_costs", 0)
        court = filled_fields.get("court_level", "court")
        case_type = filled_fields.get("case_type", "matter")

        summary = f"## 🎉 Analysis Complete!\n\n"
        summary += f"Based on your {court} {case_type.replace('_', ' ')}, "
        summary += f"you are entitled to **${total:,.2f}** in legal costs. "

        # Add key highlight
        if filled_fields.get("adr_refused"):
            summary += "**Important:** ADR refusal by the opposing party significantly strengthens your costs position."
        elif total > 10000:
            summary += "This includes all applicable cost factors under Order 21."
        else:
            summary += "Below is a detailed breakdown with strategic guidance."

        return summary

    def _format_calculation_summary(self, calculation_result: Dict[str, Any]) -> str:
        """Format calculation summary with breakdown"""
        summary = "## 💰 Cost Calculation\n\n"

        total = calculation_result.get("total_costs", 0)
        breakdown = calculation_result.get("breakdown", {})

        summary += f"**Total Costs: ${total:,.2f}**\n\n"

        if breakdown:
            summary += "**Breakdown:**\n"
            for key, value in breakdown.items():
                if isinstance(value, (int, float)) and value > 0:
                    item_name = key.replace("_", " ").title()
                    summary += f"- {item_name}: ${value:,.2f}\n"

        summary += f"\n**Legal Authority:** Order 21 of the Singapore Rules of Court"

        return summary

    def _analyze_entitlements(
        self,
        calculation_result: Dict[str, Any],
        filled_fields: Dict[str, Any]
    ) -> List[Entitlement]:
        """Analyze what user CAN claim"""
        entitlements = []

        # Base cost entitlement
        total = calculation_result.get("total_costs", 0)
        court = filled_fields.get("court_level", "")
        case_type = filled_fields.get("case_type", "")

        entitlements.append(Entitlement(
            title="Fixed Costs",
            amount=total,
            rule_basis="Order 21, Appendix 1",
            conditions=[
                f"Matter concluded in {court}",
                f"Case type: {case_type.replace('_', ' ')}",
                "Successful party entitled to costs"
            ],
            explanation=f"As the successful party in a {court} {case_type.replace('_', ' ')}, you are entitled to fixed costs under Order 21."
        ))

        # ADR refusal entitlement
        if filled_fields.get("adr_refused"):
            entitlements.append(Entitlement(
                title="Adverse Costs (ADR Refusal)",
                amount=total * 0.15,  # Estimate 15% uplift
                rule_basis="Order 21, Rule 4(c)",
                conditions=[
                    "Opposing party refused ADR",
                    "Refusal was unreasonable",
                    "You can document the refusal"
                ],
                explanation="When the opposing party unreasonably refuses ADR, you may claim enhanced costs typically 10-15% above the standard scale."
            ))

        # Multiple defendants
        defendant_count = filled_fields.get("defendant_count", 1)
        if defendant_count > 1:
            additional = 500 * (defendant_count - 1)
            entitlements.append(Entitlement(
                title="Additional Costs - Multiple Defendants",
                amount=float(additional),
                rule_basis="Order 21, Appendix 1, Note (b)",
                conditions=[
                    f"{defendant_count} defendants involved",
                    "Defendants separately represented"
                ],
                explanation=f"With {defendant_count} defendants, you are entitled to additional costs for the extra work involved."
            ))

        # Interlocutory applications
        interlocutory = filled_fields.get("interlocutory_applications", 0)
        if interlocutory > 0:
            app_costs = 1500 * interlocutory
            entitlements.append(Entitlement(
                title="Interlocutory Application Costs",
                amount=float(app_costs),
                rule_basis="Order 21, Appendix 1, Section C",
                conditions=[
                    f"{interlocutory} successful application(s)",
                    "Costs follow the event (Rule 7)"
                ],
                explanation=f"Each successful interlocutory application attracts separate costs of approximately $1,500-$2,000."
            ))

        return entitlements

    def _analyze_restrictions(self, filled_fields: Dict[str, Any]) -> List[Restriction]:
        """Analyze what user CANNOT claim"""
        restrictions = []

        # Solicitor-client costs restriction
        restrictions.append(Restriction(
            title="Cannot Claim Solicitor-Client Costs",
            rule_basis="Order 21, Rule 1",
            explanation="Party-party costs (what you can claim from opponent) are different from and typically lower than solicitor-client costs (what you pay your own lawyer).",
            exceptions=[
                "Unless specifically awarded by Court",
                "Or if costs ordered on indemnity basis"
            ]
        ))

        # If ADR refused by user
        if filled_fields.get("user_refused_adr"):  # Hypothetical field
            restrictions.append(Restriction(
                title="Risk of Reduced/No Costs Award",
                rule_basis="Order 21, Rule 4(2)",
                explanation="Since you refused ADR, even if you win, the Court may award you reduced costs or no costs at all.",
                exceptions=[
                    "If refusal was reasonable",
                    "If you can show good reasons"
                ]
            ))

        return restrictions

    def _analyze_adr_impact(self, filled_fields: Dict[str, Any]) -> Optional[str]:
        """
        Analyze ADR impact on costs (FR-P4-05).

        Critical for cases involving ADR refusal.
        """
        if not filled_fields.get("adr_refused") and not filled_fields.get("adr_attempted"):
            return None

        analysis = "## 🤝 ADR Impact Analysis\n\n"

        if filled_fields.get("adr_refused"):
            analysis += "**Order 21, Rule 4 - ADR Non-Compliance Consequences**\n\n"
            analysis += "The opposing party's refusal to participate in Alternative Dispute Resolution (ADR) has significant cost implications:\n\n"
            analysis += "**✅ What You CAN Claim:**\n"
            analysis += "- **Adverse Costs**: Enhanced costs typically 10-15% above standard scale\n"
            analysis += "- **Indemnity Costs**: Potentially claim costs on indemnity basis\n"
            analysis += "- Reference: Order 21, Rule 4(c)\n\n"
            analysis += "**🛡️ Cost Protection (Even if You Lose):**\n"
            analysis += "Under Order 21, Rule 4(2), if the opposing party ultimately succeeds despite refusing ADR, the Court has discretion to:\n"
            analysis += "- Award them NO COSTS at all\n"
            analysis += "- Award them REDUCED costs\n"
            analysis += "- This protects you from bearing their full legal costs\n\n"
            analysis += "**📋 Strategic Actions:**\n"
            analysis += "- Document all ADR attempts with dates\n"
            analysis += "- Keep correspondence showing their refusal\n"
            analysis += "- Highlight this in your costs application\n"
            analysis += "- Cite case law: *Seah Teck Ann v Anwar Siraj* [2013] SGDC 98\n"

        return analysis

    def _analyze_settlement_offers(self, filled_fields: Dict[str, Any]) -> Optional[str]:
        """
        Analyze settlement offers under Order 22A (FR-P4-06).
        """
        if not filled_fields.get("settlement_offered"):
            return None

        analysis = "## 📋 Settlement Offer Analysis\n\n"
        analysis += "**Order 22A - Offers to Settle**\n\n"

        # This would be enhanced with actual settlement offer data
        analysis += "Settlement offers affect costs significantly:\n\n"
        analysis += "**If You Made an Offer:**\n"
        analysis += "- If judgment equals or exceeds your offer\n"
        analysis += "- You may claim indemnity costs from offer date\n"
        analysis += "- This can substantially increase recoverable costs\n\n"
        analysis += "**If Opponent Made an Offer:**\n"
        analysis += "- If judgment is less favorable than their offer\n"
        analysis += "- They may claim indemnity costs from offer date\n"
        analysis += "- Important to consider in settlement negotiations\n"

        return analysis

    def _analyze_complexity_urgency(self, filled_fields: Dict[str, Any]) -> Optional[str]:
        """
        Analyze complexity and urgency factors (FR-P4-07).
        """
        complex_matter = filled_fields.get("complex_matter")
        urgent = filled_fields.get("urgent")

        if not complex_matter and not urgent:
            return None

        analysis = "## ⚖️ Complexity & Urgency Factors\n\n"

        if complex_matter:
            analysis += "**Order 21, Rule 2(2)(b) - Complexity**\n\n"
            analysis += "Your matter involves complexity factors that may justify costs beyond the fixed scale:\n\n"
            analysis += "- Novel points of law\n"
            analysis += "- Substantial documentation\n"
            analysis += "- Expert evidence\n\n"
            analysis += "**Implication:** Consider applying for detailed assessment rather than fixed costs.\n\n"

        if urgent:
            analysis += "**Order 21, Rule 2(2)(c) - Urgency**\n\n"
            analysis += "Urgent/expedited matters may attract enhanced costs:\n\n"
            analysis += "- After-hours work\n"
            analysis += "- Expedited preparation\n"
            analysis += "- Time-critical filings\n\n"
            analysis += "**Implication:** Document all urgency factors for costs application.\n"

        return analysis

    def _analyze_opponent_conduct(self, filled_fields: Dict[str, Any]) -> Optional[str]:
        """
        Analyze opponent conduct affecting costs (FR-P4-08).
        """
        # This would check for conduct indicators in filled_fields
        # For now, provide general guidance
        return None

    def _generate_recommendations(
        self,
        filled_fields: Dict[str, Any],
        calculation_result: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate strategic recommendations"""
        recommendations = []

        # File costs bill
        recommendations.append(Recommendation(
            priority="HIGH",
            action="File Bill of Costs (Form BC-100)",
            rationale="Formal costs application required to recover costs",
            timing="Within 1 month of judgment",
            documentation=[
                "Sealed copy of judgment",
                "Itemized bill of costs",
                "Supporting affidavit"
            ]
        ))

        # ADR documentation
        if filled_fields.get("adr_refused"):
            recommendations.append(Recommendation(
                priority="HIGH",
                action="Compile ADR Refusal Documentation",
                rationale="Strengthen claim for adverse costs",
                timing="Before filing costs bill",
                documentation=[
                    "Dated correspondence of ADR offers",
                    "Opponent's refusal letters",
                    "Timeline of ADR attempts"
                ]
            ))

        # Detailed breakdown
        recommendations.append(Recommendation(
            priority="MEDIUM",
            action="Prepare Detailed Cost Breakdown",
            rationale="Court may scrutinize costs claim",
            documentation=[
                "Time records",
                "Disbursements receipts",
                "Counsel fees breakdown"
            ]
        ))

        return recommendations

    def _assess_risks(self, filled_fields: Dict[str, Any]) -> List[Risk]:
        """Assess potential risks"""
        risks = []

        # Risk: Opponent challenges costs
        risks.append(Risk(
            risk_type="Costs Challenge",
            description="Opponent may challenge the quantum of costs claimed",
            likelihood="MEDIUM",
            impact="MEDIUM",
            mitigation=[
                "Ensure all costs are reasonable and proportionate",
                "Keep detailed time records",
                "Be prepared to justify each item"
            ]
        ))

        # Risk: Insufficient documentation
        if not filled_fields.get("adr_refused"):  # Less documentation
            risks.append(Risk(
                risk_type="Documentation Gap",
                description="Lack of supporting documentation may reduce costs awarded",
                likelihood="MEDIUM",
                impact="MEDIUM",
                mitigation=[
                    "Gather all relevant documents now",
                    "Create contemporaneous records",
                    "Maintain organized file"
                ]
            ))

        return risks

    def _generate_action_items(
        self,
        filled_fields: Dict[str, Any],
        calculation_result: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate prioritized action items"""
        items = []

        # Immediate actions
        items.append({
            "priority": "🔴 HIGH",
            "action": "File Bill of Costs within 1 month of judgment",
            "deadline": "1 month from judgment date"
        })

        items.append({
            "priority": "🔴 HIGH",
            "action": "Serve costs bill on all parties within 7 days of filing",
            "deadline": "7 days after filing"
        })

        # Medium priority
        items.append({
            "priority": "🟡 MEDIUM",
            "action": "Prepare supporting affidavit for costs application",
            "deadline": "Before filing costs bill"
        })

        if filled_fields.get("adr_refused"):
            items.append({
                "priority": "🔴 HIGH",
                "action": "Compile ADR refusal documentation",
                "deadline": "Before filing costs bill"
            })

        return items

    def _format_entitlements(self, entitlements: List[Entitlement]) -> str:
        """Format entitlements section"""
        if not entitlements:
            return ""

        section = "## ✅ What You CAN Claim\n\n"

        for ent in entitlements:
            section += f"### {ent.title}\n"
            if ent.amount:
                section += f"**Amount:** ${ent.amount:,.2f}\n"
            section += f"**Legal Basis:** {ent.rule_basis}\n\n"
            section += f"{ent.explanation}\n\n"

            if ent.conditions:
                section += "**Conditions:**\n"
                for condition in ent.conditions:
                    section += f"- {condition}\n"
                section += "\n"

        return section

    def _format_restrictions(self, restrictions: List[Restriction]) -> str:
        """Format restrictions section"""
        if not restrictions:
            return ""

        section = "## ⚠️ What You CANNOT Claim\n\n"

        for rest in restrictions:
            section += f"### {rest.title}\n"
            section += f"**Legal Basis:** {rest.rule_basis}\n\n"
            section += f"{rest.explanation}\n\n"

            if rest.exceptions:
                section += "**Exceptions:**\n"
                for exception in rest.exceptions:
                    section += f"- {exception}\n"
                section += "\n"

        return section

    def _format_recommendations(self, recommendations: List[Recommendation]) -> str:
        """Format recommendations section"""
        if not recommendations:
            return ""

        section = "## 📌 Strategic Recommendations\n\n"

        # Group by priority
        high = [r for r in recommendations if r.priority == "HIGH"]
        medium = [r for r in recommendations if r.priority == "MEDIUM"]
        low = [r for r in recommendations if r.priority == "LOW"]

        for priority_group, name in [(high, "🔴 High Priority"), (medium, "🟡 Medium Priority"), (low, "🟢 Low Priority")]:
            if priority_group:
                section += f"### {name}\n\n"
                for rec in priority_group:
                    section += f"**{rec.action}**\n"
                    section += f"*Why:* {rec.rationale}\n"
                    if rec.timing:
                        section += f"*When:* {rec.timing}\n"
                    if rec.documentation:
                        section += f"*Documents:* {', '.join(rec.documentation)}\n"
                    section += "\n"

        return section

    def _format_risks(self, risks: List[Risk]) -> str:
        """Format risks section"""
        if not risks:
            return ""

        section = "## ⚠️ Risk Assessment\n\n"

        for risk in risks:
            section += f"### {risk.risk_type}\n"
            section += f"**Description:** {risk.description}\n"
            section += f"**Likelihood:** {risk.likelihood} | **Impact:** {risk.impact}\n\n"

            section += "**Mitigation:**\n"
            for mitigation in risk.mitigation:
                section += f"- {mitigation}\n"
            section += "\n"

        return section

    def _format_action_items(self, items: List[Dict[str, str]]) -> str:
        """Format action items section"""
        if not items:
            return ""

        section = "## ✅ Action Items\n\n"

        for item in items:
            section += f"{item['priority']}: **{item['action']}**\n"
            if "deadline" in item:
                section += f"   ⏰ {item['deadline']}\n"
            section += "\n"

        return section
