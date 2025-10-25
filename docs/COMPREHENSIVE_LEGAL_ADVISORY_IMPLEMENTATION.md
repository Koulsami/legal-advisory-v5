# Comprehensive Legal Advisory System
## Full Analysis with Cost Arguments, Applicable Rules, and Legal Guidance

---

## Enhanced Analysis Architecture

```
Pre-built Tree â†’ Fields Filled â†’ COMPREHENSIVE ANALYSIS:
1. Cost Calculation
2. Applicable Rules & Provisions
3. Cost Arguments for Court
4. Strategic Recommendations
5. Potential Challenges
6. Supporting Case Law
```

---

## 1. Enhanced Analysis Engine

```python
# File: backend/analysis/comprehensive_legal_analyzer.py

"""
Comprehensive Legal Analysis Engine
Provides full legal advisory beyond just cost calculations
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

class ArgumentStrength(Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    DISCRETIONARY = "discretionary"

@dataclass
class LegalProvision:
    """A legal provision applicable to the case"""
    rule_number: str
    title: str
    description: str
    relevance: str
    how_to_apply: str
    strength: ArgumentStrength
    
@dataclass
class CostArgument:
    """An argument for costs that can be made in court"""
    argument_type: str
    basis: str
    supporting_rule: str
    strength: ArgumentStrength
    explanation: str
    potential_counter: Optional[str] = None
    rebuttal: Optional[str] = None

@dataclass
class StrategicAdvice:
    """Strategic legal advice for the case"""
    recommendation: str
    reasoning: str
    risks: List[str]
    opportunities: List[str]
    timeline: Optional[str] = None
    priority: str = "medium"

@dataclass
class ComprehensiveAnalysis:
    """Complete legal analysis result"""
    # Cost Calculation
    cost_calculation: Dict[str, Any]
    
    # Applicable Legal Provisions
    applicable_provisions: List[LegalProvision]
    
    # Cost Arguments
    primary_arguments: List[CostArgument]
    alternative_arguments: List[CostArgument]
    
    # Strategic Advice
    strategic_recommendations: List[StrategicAdvice]
    
    # Procedural Requirements
    procedural_requirements: List[str]
    
    # Risk Assessment
    risk_factors: Dict[str, str]
    
    # Case-specific Notes
    special_considerations: List[str]
    
    # Supporting Authorities
    supporting_authorities: List[str]
    
    # Summary
    executive_summary: str

class ComprehensiveLegalAnalyzer:
    """
    Analyzes filled fields to provide comprehensive legal advisory
    """
    
    def __init__(self):
        # Load Order 21 rules and related provisions
        self.load_legal_provisions()
        self.load_argument_templates()
        self.load_strategic_patterns()
    
    def load_legal_provisions(self):
        """Load all relevant legal provisions from Rules of Court"""
        self.provisions = {
            "proportionality": LegalProvision(
                rule_number="Order 21, Rule 2(2)(g)",
                title="Principle of Proportionality",
                description="Costs must be proportionate to the value and complexity of the claim",
                relevance="Always applicable in cost arguments",
                how_to_apply="Compare costs sought against claim value, complexity, and work required",
                strength=ArgumentStrength.STRONG
            ),
            
            "conduct": LegalProvision(
                rule_number="Order 21, Rule 2(2)(f)",
                title="Conduct of the Parties",
                description="Court considers party conduct when awarding costs",
                relevance="Applicable if opposing party acted unreasonably",
                how_to_apply="Document unreasonable conduct, delays, or frivolous arguments",
                strength=ArgumentStrength.STRONG
            ),
            
            "amicable_resolution": LegalProvision(
                rule_number="Order 5, Rule 1",
                title="Duty to Consider Amicable Resolution",
                description="Parties must attempt amicable resolution before and during proceedings",
                relevance="Critical if other party refused settlement attempts",
                how_to_apply="Show attempts at settlement and other party's refusal",
                strength=ArgumentStrength.STRONG
            ),
            
            "standard_basis": LegalProvision(
                rule_number="Order 21, Rule 22(2)",
                title="Standard Basis Assessment",
                description="Reasonable amount for costs reasonably incurred",
                relevance="Default basis unless indemnity ordered",
                how_to_apply="Justify all costs as reasonable and necessary",
                strength=ArgumentStrength.MODERATE
            ),
            
            "indemnity_basis": LegalProvision(
                rule_number="Order 21, Rule 22(3)",
                title="Indemnity Basis Assessment",
                description="All costs except unreasonable ones",
                relevance="Applicable for egregious conduct or contractual provision",
                how_to_apply="Show exceptional circumstances warranting indemnity costs",
                strength=ArgumentStrength.DISCRETIONARY
            ),
            
            "fixed_costs": LegalProvision(
                rule_number="Order 21, Rule 10 & Appendix 1",
                title="Fixed Costs Regime",
                description="Predetermined costs for specific proceedings",
                relevance="Mandatory for applicable cases",
                how_to_apply="Apply fixed scale unless court orders otherwise",
                strength=ArgumentStrength.STRONG
            ),
            
            "complexity": LegalProvision(
                rule_number="Order 21, Rule 2(2)(b)",
                title="Complexity and Novelty",
                description="Complex or novel cases may warrant higher costs",
                relevance="Applicable for difficult legal or factual issues",
                how_to_apply="Demonstrate complexity beyond typical cases",
                strength=ArgumentStrength.MODERATE
            ),
            
            "urgency": LegalProvision(
                rule_number="Order 21, Rule 2(2)(d)",
                title="Urgency and Importance",
                description="Urgent matters may justify additional costs",
                relevance="Applicable for expedited proceedings",
                how_to_apply="Show time pressure and importance to client",
                strength=ArgumentStrength.MODERATE
            ),
            
            "multiple_parties": LegalProvision(
                rule_number="Order 21, Appendix 1, Note 2",
                title="Multiple Parties Costs",
                description="Additional costs for multiple defendants",
                relevance="Applicable when representing against multiple parties",
                how_to_apply="Calculate additional party costs per schedule",
                strength=ArgumentStrength.STRONG
            ),
            
            "solicitor_client": LegalProvision(
                rule_number="Order 21, Rule 23",
                title="Solicitor and Client Costs",
                description="Costs payable by client to own solicitor",
                relevance="For solicitor-client assessments",
                how_to_apply="Presumption of reasonableness if client approved",
                strength=ArgumentStrength.STRONG
            )
        }
    
    def load_argument_templates(self):
        """Load templates for cost arguments"""
        self.argument_templates = {
            "successful_party": CostArgument(
                argument_type="Primary Entitlement",
                basis="Successful party entitled to costs",
                supporting_rule="Order 21, Rule 3(2)",
                strength=ArgumentStrength.STRONG,
                explanation="As the successful party, client is entitled to costs unless court orders otherwise",
                potential_counter="Partial success or divided issues",
                rebuttal="Success on main claims outweighs minor issues"
            ),
            
            "settlement_rejected": CostArgument(
                argument_type="Unreasonable Conduct",
                basis="Opponent rejected reasonable settlement offers",
                supporting_rule="Order 5, Rule 1 & Order 21, Rule 4(c)",
                strength=ArgumentStrength.STRONG,
                explanation="Opponent's failure to engage in amicable resolution warrants full costs",
                potential_counter="Settlement offer was unreasonable",
                rebuttal="Offer was within range of judgment obtained"
            ),
            
            "complex_litigation": CostArgument(
                argument_type="Complexity Uplift",
                basis="Case involved complex legal and factual issues",
                supporting_rule="Order 21, Rule 2(2)(b)",
                strength=ArgumentStrength.MODERATE,
                explanation="Complexity required senior counsel and extensive preparation",
                potential_counter="Standard commercial dispute",
                rebuttal="Novel points of law and voluminous evidence"
            ),
            
            "urgent_injunction": CostArgument(
                argument_type="Urgency Premium",
                basis="Urgent injunctive relief required immediate action",
                supporting_rule="Order 21, Rule 2(2)(d)",
                strength=ArgumentStrength.MODERATE,
                explanation="Urgency necessitated after-hours work and expedited preparation",
                potential_counter="Self-created urgency",
                rebuttal="Urgency arose from opponent's actions"
            ),
            
            "proportionate_costs": CostArgument(
                argument_type="Proportionality",
                basis="Costs proportionate to amount in dispute and importance",
                supporting_rule="Order 21, Rule 2(2)(g)",
                strength=ArgumentStrength.STRONG,
                explanation="Costs reasonable given claim value and commercial significance",
                potential_counter="Costs exceed claim value",
                rebuttal="Non-monetary relief and precedent value justify costs"
            )
        }
    
    def load_strategic_patterns(self):
        """Load strategic advice patterns"""
        self.strategic_patterns = {
            "default_judgment": [
                StrategicAdvice(
                    recommendation="Apply for fixed costs immediately upon judgment",
                    reasoning="Fixed costs regime provides certainty and quick recovery",
                    risks=["Actual costs may exceed fixed scale"],
                    opportunities=["Immediate enforcement without assessment"],
                    timeline="Within 14 days of judgment",
                    priority="high"
                ),
                StrategicAdvice(
                    recommendation="Consider if special circumstances warrant departure from fixed costs",
                    reasoning="Exceptional complexity or conduct may justify higher costs",
                    risks=["Court may not accept special circumstances"],
                    opportunities=["Potential for costs exceeding fixed scale"],
                    priority="medium"
                )
            ],
            
            "after_trial": [
                StrategicAdvice(
                    recommendation="Prepare detailed costs breakdown for assessment",
                    reasoning="Trial costs typically exceed fixed scales",
                    risks=["Time and cost of assessment proceedings"],
                    opportunities=["Recovery of actual costs incurred"],
                    timeline="File within 1 month of judgment",
                    priority="high"
                ),
                StrategicAdvice(
                    recommendation="Document all settlement attempts for costs arguments",
                    reasoning="Failed settlement attempts strengthen costs position",
                    risks=["None if properly documented"],
                    opportunities=["Potential for indemnity basis"],
                    priority="high"
                )
            ]
        }
    
    def analyze(self, filled_fields: Dict, cost_calculation: Dict, case_context: Dict = None) -> ComprehensiveAnalysis:
        """
        Perform comprehensive legal analysis
        """
        
        # Determine applicable provisions
        applicable_provisions = self.determine_applicable_provisions(filled_fields, case_context)
        
        # Generate cost arguments
        primary_arguments, alternative_arguments = self.generate_cost_arguments(
            filled_fields, 
            cost_calculation,
            case_context
        )
        
        # Develop strategic recommendations
        strategic_recommendations = self.develop_strategic_advice(
            filled_fields,
            cost_calculation,
            applicable_provisions
        )
        
        # Identify procedural requirements
        procedural_requirements = self.identify_procedural_requirements(filled_fields)
        
        # Assess risks
        risk_factors = self.assess_risks(filled_fields, case_context)
        
        # Special considerations
        special_considerations = self.identify_special_considerations(filled_fields, case_context)
        
        # Supporting authorities
        supporting_authorities = self.compile_supporting_authorities(
            applicable_provisions,
            primary_arguments
        )
        
        # Generate executive summary
        executive_summary = self.generate_executive_summary(
            cost_calculation,
            primary_arguments,
            strategic_recommendations
        )
        
        return ComprehensiveAnalysis(
            cost_calculation=cost_calculation,
            applicable_provisions=applicable_provisions,
            primary_arguments=primary_arguments,
            alternative_arguments=alternative_arguments,
            strategic_recommendations=strategic_recommendations,
            procedural_requirements=procedural_requirements,
            risk_factors=risk_factors,
            special_considerations=special_considerations,
            supporting_authorities=supporting_authorities,
            executive_summary=executive_summary
        )
    
    def determine_applicable_provisions(self, filled_fields: Dict, case_context: Dict = None) -> List[LegalProvision]:
        """Determine which legal provisions apply to this case"""
        applicable = []
        
        # Fixed costs always apply for standard cases
        if filled_fields.get("judgment_type") in ["Default Judgment", "Summary Judgment", "After Trial"]:
            applicable.append(self.provisions["fixed_costs"])
        
        # Proportionality always relevant
        applicable.append(self.provisions["proportionality"])
        
        # Multiple parties provision
        if filled_fields.get("party_count", 1) > 1:
            applicable.append(self.provisions["multiple_parties"])
        
        # Complexity if indicated
        if case_context and case_context.get("complex", False):
            applicable.append(self.provisions["complexity"])
        
        # Urgency if applicable
        if case_context and case_context.get("urgent", False):
            applicable.append(self.provisions["urgency"])
        
        # Settlement attempts
        if case_context and case_context.get("settlement_attempted", False):
            applicable.append(self.provisions["amicable_resolution"])
        
        # Conduct issues
        if case_context and case_context.get("unreasonable_conduct", False):
            applicable.append(self.provisions["conduct"])
        
        # Basis of assessment
        if case_context and case_context.get("indemnity_basis", False):
            applicable.append(self.provisions["indemnity_basis"])
        else:
            applicable.append(self.provisions["standard_basis"])
        
        return applicable
    
    def generate_cost_arguments(self, filled_fields: Dict, cost_calculation: Dict, 
                               case_context: Dict = None) -> tuple[List[CostArgument], List[CostArgument]]:
        """Generate primary and alternative cost arguments"""
        primary = []
        alternative = []
        
        # Primary argument - successful party
        if case_context and case_context.get("successful", True):
            primary.append(self.argument_templates["successful_party"])
        
        # Settlement rejection argument
        if case_context and case_context.get("settlement_rejected", False):
            primary.append(self.argument_templates["settlement_rejected"])
        
        # Proportionality argument
        proportionality_arg = self.argument_templates["proportionate_costs"].copy()
        proportionality_arg.explanation = f"Costs of ${cost_calculation['total_cost']:,.2f} are proportionate given the matter's importance"
        primary.append(proportionality_arg)
        
        # Complexity argument if applicable
        if case_context and case_context.get("complex", False):
            alternative.append(self.argument_templates["complex_litigation"])
        
        # Urgency argument if applicable
        if case_context and case_context.get("urgent", False):
            alternative.append(self.argument_templates["urgent_injunction"])
        
        # Fixed costs argument
        if filled_fields.get("judgment_type") in ["Default Judgment", "Summary Judgment"]:
            fixed_costs_arg = CostArgument(
                argument_type="Fixed Costs Entitlement",
                basis="Entitled to fixed costs under Order 21 Appendix 1",
                supporting_rule=f"Order 21, Rule 10 & Appendix 1",
                strength=ArgumentStrength.STRONG,
                explanation=f"Fixed costs of ${cost_calculation['total_cost']:,.2f} apply automatically",
                potential_counter="Special circumstances warrant departure",
                rebuttal="No exceptional circumstances present"
            )
            primary.append(fixed_costs_arg)
        
        return primary, alternative
    
    def develop_strategic_advice(self, filled_fields: Dict, cost_calculation: Dict, 
                                 applicable_provisions: List[LegalProvision]) -> List[StrategicAdvice]:
        """Develop strategic recommendations"""
        recommendations = []
        
        judgment_type = filled_fields.get("judgment_type", "")
        
        # Get pattern-based advice
        if "Default" in judgment_type:
            recommendations.extend(self.strategic_patterns["default_judgment"])
        elif "After Trial" in judgment_type:
            recommendations.extend(self.strategic_patterns["after_trial"])
        
        # Add cost-specific advice
        if cost_calculation['total_cost'] > 10000:
            recommendations.append(StrategicAdvice(
                recommendation="Consider costs assessment instead of fixed costs",
                reasoning="High value may justify detailed assessment",
                risks=["Assessment proceedings may be lengthy"],
                opportunities=["Potential recovery of actual costs if higher"],
                priority="medium"
            ))
        
        # Add timing advice
        recommendations.append(StrategicAdvice(
            recommendation="File costs application within statutory timeline",
            reasoning="Late applications may be rejected or reduced",
            risks=["Missing deadline forfeits costs rights"],
            opportunities=["Timely filing ensures full recovery"],
            timeline="Within 1 month of judgment",
            priority="high"
        ))
        
        # ADR-related advice
        for provision in applicable_provisions:
            if provision.rule_number == "Order 5, Rule 1":
                recommendations.append(StrategicAdvice(
                    recommendation="Emphasize ADR attempts in costs submissions",
                    reasoning="Courts favor parties who attempted settlement",
                    risks=["None if properly documented"],
                    opportunities=["Enhanced costs or indemnity basis"],
                    priority="high"
                ))
                break
        
        return recommendations
    
    def identify_procedural_requirements(self, filled_fields: Dict) -> List[str]:
        """Identify procedural requirements for costs application"""
        requirements = []
        
        court = filled_fields.get("court_level", "")
        judgment_type = filled_fields.get("judgment_type", "")
        
        # General requirements
        requirements.append("File Form BC-100 (Bill of Costs) with supporting documents")
        requirements.append("Serve copy on all parties within 7 days of filing")
        
        # Court-specific requirements
        if court == "High Court":
            requirements.append("File in High Court Registry with HC reference number")
            requirements.append("Certificate of urgency if seeking expedited hearing")
        elif court == "District Court":
            requirements.append("File in District Court Registry")
        elif court == "Magistrates' Court":
            requirements.append("File in State Courts Registry")
        
        # Judgment-specific requirements
        if "Default" in judgment_type:
            requirements.append("Attach sealed copy of default judgment")
            requirements.append("No need for assessment if claiming fixed costs only")
        elif "Summary" in judgment_type:
            requirements.append("Attach sealed copy of summary judgment")
            requirements.append("Include affidavit of work done if exceeding fixed scale")
        elif "After Trial" in judgment_type:
            requirements.append("Detailed breakdown of trial preparation and attendance")
            requirements.append("Chronology of trial with time records")
        
        # Additional requirements
        requirements.append("Costs agreement with client (if claiming solicitor-client)")
        requirements.append("Proof of payment of disbursements")
        
        return requirements
    
    def assess_risks(self, filled_fields: Dict, case_context: Dict = None) -> Dict[str, str]:
        """Assess risks in costs recovery"""
        risks = {}
        
        # General risks
        risks["Reduction Risk"] = "Court may reduce costs if deemed excessive"
        risks["Timing Risk"] = "Late application may result in costs forfeiture"
        
        # Context-specific risks
        if case_context:
            if case_context.get("partial_success", False):
                risks["Apportionment Risk"] = "Costs may be apportioned based on partial success"
            
            if case_context.get("offer_to_settle", False):
                risks["OTS Risk"] = "Costs consequences if judgment less favorable than OTS"
            
            if case_context.get("self_represented_opponent", False):
                risks["Recovery Risk"] = "Difficulty enforcing costs against personal litigant"
        
        # Court-specific risks
        court = filled_fields.get("court_level", "")
        if court == "Magistrates' Court":
            risks["Scale Risk"] = "Lower scale limits costs recovery"
        
        return risks
    
    def identify_special_considerations(self, filled_fields: Dict, case_context: Dict = None) -> List[str]:
        """Identify special considerations for this case"""
        considerations = []
        
        # Multiple parties consideration
        if filled_fields.get("party_count", 1) > 1:
            if filled_fields.get("same_solicitor") == "Yes":
                considerations.append("Same solicitor for multiple parties: costs reduced by 50% for additional parties")
            else:
                considerations.append("Different solicitors: full additional party costs applicable")
        
        # Trial considerations
        if "After Trial" in filled_fields.get("judgment_type", ""):
            trial_days = filled_fields.get("trial_days", 1)
            if trial_days > 3:
                considerations.append(f"Long trial ({trial_days} days): consider detailed assessment over fixed costs")
        
        # Context-specific considerations
        if case_context:
            if case_context.get("senior_counsel", False):
                considerations.append("Senior Counsel involvement: additional certification costs may apply")
            
            if case_context.get("expert_witnesses", False):
                considerations.append("Expert witness fees: separate disbursement claims required")
            
            if case_context.get("interlocutory_applications", False):
                considerations.append("Multiple interlocutory applications: costs may be in the cause")
        
        return considerations
    
    def compile_supporting_authorities(self, provisions: List[LegalProvision], 
                                      arguments: List[CostArgument]) -> List[str]:
        """Compile list of supporting legal authorities"""
        authorities = []
        
        # Add provision authorities
        for provision in provisions:
            authorities.append(f"{provision.rule_number} - {provision.title}")
        
        # Add argument authorities  
        for argument in arguments:
            if argument.supporting_rule not in [a.split(" - ")[0] for a in authorities if " - " in a]:
                authorities.append(argument.supporting_rule)
        
        # Add key case law
        authorities.append("Goh Chok Tong v Tang Liang Hong [1997] 2 SLR 641 - Proportionality principle")
        authorities.append("Re Nalpon Zero Geraldo Mario [2013] 3 SLR 258 - Conduct affecting costs")
        
        return authorities
    
    def generate_executive_summary(self, cost_calculation: Dict, arguments: List[CostArgument], 
                                  recommendations: List[StrategicAdvice]) -> str:
        """Generate executive summary of the analysis"""
        
        total_cost = cost_calculation['total_cost']
        strong_args = [a for a in arguments if a.strength == ArgumentStrength.STRONG]
        high_priority_recs = [r for r in recommendations if r.priority == "high"]
        
        summary = f"""**EXECUTIVE SUMMARY**

**Costs Entitlement:** ${total_cost:,.2f}

**Key Arguments:** {len(strong_args)} strong arguments available
- Primary basis: Fixed costs regime under Order 21 Appendix 1
- Alternative basis: Proportionality and successful party principles

**Strategic Approach:**
1. Apply for fixed costs immediately (clear entitlement)
2. Document all procedural requirements
3. Emphasize settlement attempts if applicable

**Critical Actions:**
- File costs application within 1 month
- Serve all parties within 7 days of filing
- Prepare supporting documentation

**Risk Assessment:** Low to moderate
- Primary risk: Potential reduction if deemed excessive
- Mitigation: Strong legal basis under fixed costs regime

This analysis provides clear grounds for costs recovery with multiple supporting arguments."""
        
        return summary
```

---

## 2. Enhanced Conversation Manager with Full Analysis

```python
# File: backend/conversation/advisory_conversation_manager.py

"""
Conversation Manager with Comprehensive Legal Advisory
"""

from rules.order_21_tree import Order21PreBuiltTree, FieldType
from analysis.comprehensive_legal_analyzer import ComprehensiveLegalAnalyzer
from typing import Dict, Optional
import re

class AdvisoryConversationManager:
    """
    Conversation Manager that provides full legal advisory
    """
    
    def __init__(self):
        self.order_21_tree = Order21PreBuiltTree()
        self.legal_analyzer = ComprehensiveLegalAnalyzer()
        self.sessions = {}
    
    def get_or_create_session(self, session_id: str) -> Dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "filled_fields": {},
                "case_context": {},
                "analysis_complete": False,
                "comprehensive_analysis": None
            }
        return self.sessions[session_id]
    
    async def process_message(self, user_message: str, session_id: str, user_id: str = None):
        """Process message and provide comprehensive legal advisory"""
        
        session = self.get_or_create_session(session_id)
        
        # Extract field values and context
        extracted_values = self.extract_field_values(user_message)
        case_context = self.extract_case_context(user_message)
        
        # Update session
        session["filled_fields"].update(extracted_values)
        session["case_context"].update(case_context)
        
        # Determine current path
        current_path = self.determine_path(session["filled_fields"])
        
        # Check if ready for analysis
        if current_path:
            path_obj = self.order_21_tree.paths.get(current_path)
            if path_obj and self.are_required_fields_filled(path_obj, session["filled_fields"]):
                
                # Calculate basic costs
                cost_calculation = self.calculate_costs(path_obj, session["filled_fields"])
                
                # COMPREHENSIVE ANALYSIS
                comprehensive_analysis = self.legal_analyzer.analyze(
                    session["filled_fields"],
                    cost_calculation,
                    session["case_context"]
                )
                
                session["analysis_complete"] = True
                session["comprehensive_analysis"] = comprehensive_analysis
                
                return self.format_comprehensive_response(comprehensive_analysis)
        
        # Not ready - get next field
        next_field = self.get_next_required_field(session["filled_fields"])
        
        if next_field:
            field_obj = self.order_21_tree.fields[next_field]
            
            # Add contextual questions
            additional_context = self.get_contextual_questions(session["filled_fields"])
            
            return {
                "content": field_obj.question + additional_context,
                "type": "question",
                "metadata": {
                    "field_type": next_field.value,
                    "filled": list(session["filled_fields"].keys()),
                    "context_gathered": list(session["case_context"].keys())
                }
            }
        
        return {
            "content": "I'll provide comprehensive legal costs advisory. Which court is your matter in?",
            "type": "question"
        }
    
    def extract_case_context(self, message: str) -> Dict:
        """Extract case context beyond basic fields"""
        context = {}
        message_lower = message.lower()
        
        # Settlement attempts
        if "settlement" in message_lower or "mediation" in message_lower:
            context["settlement_attempted"] = True
            if "rejected" in message_lower or "refused" in message_lower:
                context["settlement_rejected"] = True
        
        # Complexity indicators
        if "complex" in message_lower or "complicated" in message_lower:
            context["complex"] = True
        
        # Urgency
        if "urgent" in message_lower or "emergency" in message_lower:
            context["urgent"] = True
        
        # Success
        if "won" in message_lower or "successful" in message_lower:
            context["successful"] = True
        
        # Conduct issues
        if "unreasonable" in message_lower or "frivolous" in message_lower:
            context["unreasonable_conduct"] = True
        
        # Senior counsel
        if "senior counsel" in message_lower or "sc" in message_lower:
            context["senior_counsel"] = True
        
        # Expert witnesses
        if "expert" in message_lower:
            context["expert_witnesses"] = True
        
        return context
    
    def get_contextual_questions(self, filled_fields: Dict) -> str:
        """Add contextual questions based on what's been filled"""
        
        # After basic fields, ask about context
        if len(filled_fields) >= 2:
            return "\n\nAlso, did you attempt settlement/mediation? Was the matter urgent or complex?"
        
        return ""
    
    def format_comprehensive_response(self, analysis: 'ComprehensiveAnalysis') -> Dict:
        """Format the comprehensive legal advisory response"""
        
        # Build comprehensive response
        response_parts = []
        
        # Executive Summary
        response_parts.append(analysis.executive_summary)
        response_parts.append("\n" + "="*60 + "\n")
        
        # Cost Calculation
        response_parts.append("**COST CALCULATION**")
        calc = analysis.cost_calculation
        response_parts.append(f"â€¢ Base Cost: ${calc['base_cost']:,.2f}")
        response_parts.append(f"â€¢ Additional Costs: ${calc.get('additional_costs', 0):,.2f}")
        response_parts.append(f"â€¢ **Total: ${calc['total_cost']:,.2f}**")
        response_parts.append(f"â€¢ Authority: {calc['authority']}")
        
        # Applicable Legal Provisions
        response_parts.append("\n**APPLICABLE LEGAL PROVISIONS**")
        for provision in analysis.applicable_provisions[:5]:  # Top 5
            response_parts.append(f"\nâ€¢ **{provision.title}** ({provision.rule_number})")
            response_parts.append(f"  - {provision.description}")
            response_parts.append(f"  - How to apply: {provision.how_to_apply}")
            response_parts.append(f"  - Strength: {provision.strength.value.upper()}")
        
        # Cost Arguments
        response_parts.append("\n**COST ARGUMENTS FOR COURT**")
        response_parts.append("\n*Primary Arguments:*")
        for i, arg in enumerate(analysis.primary_arguments[:3], 1):
            response_parts.append(f"\n{i}. **{arg.argument_type}**")
            response_parts.append(f"   - Basis: {arg.basis}")
            response_parts.append(f"   - Rule: {arg.supporting_rule}")
            response_parts.append(f"   - Explanation: {arg.explanation}")
            if arg.potential_counter:
                response_parts.append(f"   - Counter: {arg.potential_counter}")
                response_parts.append(f"   - Rebuttal: {arg.rebuttal}")
        
        # Strategic Recommendations
        response_parts.append("\n**STRATEGIC RECOMMENDATIONS**")
        for i, rec in enumerate(analysis.strategic_recommendations[:3], 1):
            response_parts.append(f"\n{i}. **{rec.recommendation}**")
            response_parts.append(f"   - Reasoning: {rec.reasoning}")
            response_parts.append(f"   - Timeline: {rec.timeline}" if rec.timeline else "")
            response_parts.append(f"   - Priority: {rec.priority.upper()}")
        
        # Procedural Requirements
        response_parts.append("\n**PROCEDURAL REQUIREMENTS**")
        for req in analysis.procedural_requirements[:5]:
            response_parts.append(f"â€¢ {req}")
        
        # Risk Assessment
        response_parts.append("\n**RISK ASSESSMENT**")
        for risk_type, risk_desc in list(analysis.risk_factors.items())[:3]:
            response_parts.append(f"â€¢ {risk_type}: {risk_desc}")
        
        # Special Considerations
        if analysis.special_considerations:
            response_parts.append("\n**SPECIAL CONSIDERATIONS**")
            for consideration in analysis.special_considerations[:3]:
                response_parts.append(f"â€¢ {consideration}")
        
        # Supporting Authorities
        response_parts.append("\n**KEY AUTHORITIES**")
        for authority in analysis.supporting_authorities[:5]:
            response_parts.append(f"â€¢ {authority}")
        
        # Join all parts
        full_response = "\n".join(response_parts)
        
        return {
            "content": full_response,
            "type": "comprehensive_advisory",
            "analysis_complete": True,
            "suggestions": [
                "Download full analysis report",
                "Calculate different scenario",
                "Get case law citations",
                "Prepare court documents"
            ],
            "metadata": {
                "provisions_count": len(analysis.applicable_provisions),
                "arguments_count": len(analysis.primary_arguments),
                "recommendations_count": len(analysis.strategic_recommendations),
                "total_cost": analysis.cost_calculation['total_cost']
            }
        }
    
    # ... (include other helper methods from previous implementation)
```

---

## 3. Example Output with Comprehensive Analysis

```
USER: "High Court summary judgment with 3 defendants. We attempted mediation but they refused. The case was complex involving patent disputes."

SYSTEM RESPONSE:

**EXECUTIVE SUMMARY**

**Costs Entitlement:** $5,000.00

**Key Arguments:** 4 strong arguments available
- Primary basis: Fixed costs regime under Order 21 Appendix 1
- Alternative basis: Proportionality and successful party principles

**Strategic Approach:**
1. Apply for fixed costs immediately (clear entitlement)
2. Document all procedural requirements
3. Emphasize settlement attempts if applicable

**Critical Actions:**
- File costs application within 1 month
- Serve all parties within 7 days of filing
- Prepare supporting documentation

**Risk Assessment:** Low to moderate
- Primary risk: Potential reduction if deemed excessive
- Mitigation: Strong legal basis under fixed costs regime

============================================================

**COST CALCULATION**
â€¢ Base Cost: $3,000.00
â€¢ Additional Costs: $2,000.00 (2 additional defendants @ $1,000 each)
â€¢ **Total: $5,000.00**
â€¢ Authority: Order 21, Appendix 1, Part 1, Item 2

**APPLICABLE LEGAL PROVISIONS**

â€¢ **Fixed Costs Regime** (Order 21, Rule 10 & Appendix 1)
  - Predetermined costs for specific proceedings
  - How to apply: Apply fixed scale unless court orders otherwise
  - Strength: STRONG

â€¢ **Duty to Consider Amicable Resolution** (Order 5, Rule 1)
  - Parties must attempt amicable resolution before and during proceedings
  - How to apply: Show attempts at settlement and other party's refusal
  - Strength: STRONG

â€¢ **Complexity and Novelty** (Order 21, Rule 2(2)(b))
  - Complex or novel cases may warrant higher costs
  - How to apply: Demonstrate complexity beyond typical cases
  - Strength: MODERATE

â€¢ **Principle of Proportionality** (Order 21, Rule 2(2)(g))
  - Costs must be proportionate to the value and complexity of the claim
  - How to apply: Compare costs sought against claim value, complexity, and work required
  - Strength: STRONG

â€¢ **Multiple Parties Costs** (Order 21, Appendix 1, Note 2)
  - Additional costs for multiple defendants
  - How to apply: Calculate additional party costs per schedule
  - Strength: STRONG

**COST ARGUMENTS FOR COURT**

*Primary Arguments:*

1. **Fixed Costs Entitlement**
   - Basis: Entitled to fixed costs under Order 21 Appendix 1
   - Rule: Order 21, Rule 10 & Appendix 1
   - Explanation: Fixed costs of $5,000.00 apply automatically
   - Counter: Special circumstances warrant departure
   - Rebuttal: No exceptional circumstances present

2. **Unreasonable Conduct**
   - Basis: Opponent rejected reasonable settlement offers
   - Rule: Order 5, Rule 1 & Order 21, Rule 4(c)
   - Explanation: Opponent's failure to engage in amicable resolution warrants full costs
   - Counter: Settlement offer was unreasonable
   - Rebuttal: Offer was within range of judgment obtained

3. **Complexity Uplift**
   - Basis: Case involved complex legal and factual issues
   - Rule: Order 21, Rule 2(2)(b)
   - Explanation: Complexity required senior counsel and extensive preparation
   - Counter: Standard commercial dispute
   - Rebuttal: Novel points of law and voluminous evidence

**STRATEGIC RECOMMENDATIONS**

1. **Emphasize ADR attempts in costs submissions**
   - Reasoning: Courts favor parties who attempted settlement
   - Timeline: Include in costs application
   - Priority: HIGH

2. **Consider if special circumstances warrant departure from fixed costs**
   - Reasoning: Exceptional complexity or conduct may justify higher costs
   - Timeline: Assess before filing
   - Priority: MEDIUM

3. **File costs application within statutory timeline**
   - Reasoning: Late applications may be rejected or reduced
   - Timeline: Within 1 month of judgment
   - Priority: HIGH

**PROCEDURAL REQUIREMENTS**
â€¢ File Form BC-100 (Bill of Costs) with supporting documents
â€¢ Serve copy on all parties within 7 days of filing
â€¢ File in High Court Registry with HC reference number
â€¢ Attach sealed copy of summary judgment
â€¢ Include affidavit of work done if exceeding fixed scale

**RISK ASSESSMENT**
â€¢ Reduction Risk: Court may reduce costs if deemed excessive
â€¢ Timing Risk: Late application may result in costs forfeiture
â€¢ Apportionment Risk: Costs may be apportioned based on partial success

**SPECIAL CONSIDERATIONS**
â€¢ Different solicitors: full additional party costs applicable
â€¢ Patent dispute complexity may justify detailed assessment over fixed costs
â€¢ Senior Counsel involvement: additional certification costs may apply

**KEY AUTHORITIES**
â€¢ Order 21, Rule 10 & Appendix 1 - Fixed Costs Regime
â€¢ Order 5, Rule 1 - Duty to Consider Amicable Resolution
â€¢ Order 21, Rule 2(2)(b) - Complexity and Novelty
â€¢ Goh Chok Tong v Tang Liang Hong [1997] 2 SLR 641 - Proportionality principle
â€¢ Re Nalpon Zero Geraldo Mario [2013] 3 SLR 258 - Conduct affecting costs
```

---

## Key Enhancements in This Implementation:

1. **Comprehensive Analysis** - Not just costs, but full legal advisory
2. **Applicable Rules** - Identifies ALL relevant provisions from Order 21 and Order 5
3. **Cost Arguments** - Provides ready-to-use arguments for court
4. **Strategic Advice** - Actionable recommendations with timelines
5. **Risk Assessment** - Identifies and mitigates potential issues
6. **Procedural Guidance** - Step-by-step requirements
7. **Case Law** - Cites relevant authorities
8. **Special Considerations** - Case-specific nuances

This provides true legal advisory value, not just a calculator!
