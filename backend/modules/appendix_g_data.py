"""
Appendix G Cost Guidelines Data
Practice Directions - Supreme Court of Singapore

This file contains all cost data from Appendix G of the Practice Directions.
Appendix G provides guidelines for party-and-party costs in the Supreme Court.

Source: Practice Directions Para. 138(1) - Appendix G
Last Updated: October 2025

Important Notes:
- These are GUIDELINES, not fixed scales
- Court has discretion to depart from these ranges
- Must consider Order 21, Rule 2(2) factors:
  * Efforts at amicable resolution
  * Complexity and novelty
  * Skill and time required
  * Urgency and importance
  * Number of solicitors
  * Conduct of parties
  * Proportionality
  * Stage of conclusion
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class CostRange:
    """Represents a cost range with min/max values."""
    min_cost: float
    max_cost: float
    notes: List[str] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = []

    def midpoint(self) -> float:
        """Calculate midpoint of the range."""
        return (self.min_cost + self.max_cost) / 2


# ============================================================================
# PART II: COSTS GUIDELINES FOR SUMMONSES
# ============================================================================

# Part II.A: General Guidelines
SUMMONS_GENERAL = {
    "uncontested": CostRange(
        min_cost=1000,
        max_cost=5000,
        notes=["For any uncontested summons"]
    ),
    "contested_less_45_mins": CostRange(
        min_cost=2000,
        max_cost=5000,
        notes=["Application on normal list lasting less than 45 minutes"]
    ),
    "contested_45_mins_or_longer": CostRange(
        min_cost=4000,
        max_cost=11000,
        notes=["Application on normal list lasting 45 minutes or longer"]
    ),
    "complex_3hrs": CostRange(
        min_cost=9000,
        max_cost=22000,
        notes=["Complex or lengthy application fixed for special hearing (duration of 3hrs)"]
    )
}

# Part II.B: Specific Applications
SUMMONS_SPECIFIC = {
    "adjournment": CostRange(
        min_cost=500,
        max_cost=2000,
        notes=[]
    ),

    "extension_of_time": CostRange(
        min_cost=1000,
        max_cost=4000,
        notes=[]
    ),

    "amendment_of_pleadings": CostRange(
        min_cost=1000,
        max_cost=7000,
        notes=[
            "The costs range relates only to the application itself",
            "Separate costs for the amendments (e.g., for costs thrown away) may be sought"
        ]
    ),

    "further_and_better_particulars": CostRange(
        min_cost=2000,
        max_cost=9000,
        notes=[]
    ),

    "production_of_documents": CostRange(
        min_cost=3000,
        max_cost=11000,
        notes=[]
    ),

    "security_for_costs": CostRange(
        min_cost=2000,
        max_cost=10000,
        notes=[]
    ),

    "interim_payments": CostRange(
        min_cost=2000,
        max_cost=10000,
        notes=["Order 13, Rule 8"]
    ),

    "striking_out_partial": CostRange(
        min_cost=3000,
        max_cost=12000,
        notes=["Striking out of part(s) of pleadings / affidavit"]
    ),

    "striking_out_whole": CostRange(
        min_cost=6000,
        max_cost=20000,
        notes=[
            "Striking out of whole suit / defence",
            "The costs range relates only to the application itself",
            "If applicant is successful, separate costs for the action (based on pre-trial range) may be sought"
        ]
    ),

    "summary_judgment_given": CostRange(
        min_cost=6000,
        max_cost=20000,
        notes=[
            "Summary judgment given (Order 9, Rule 17)",
            "Part 2(c) of Appendix 1, Order 21 provides fixed costs scale",
            "Court may depart from said scale: Order 21, Rule 10",
            "The costs range relates only to the application itself",
            "If plaintiff successful, separate costs for action (pre-trial range) may be sought"
        ]
    ),

    "summary_judgment_dismissed": CostRange(
        min_cost=6000,
        max_cost=20000,
        notes=[
            "Application for summary judgment dismissed",
            "Costs for the application only"
        ]
    ),

    "setting_aside_judgment": CostRange(
        min_cost=2000,
        max_cost=19000,
        notes=[]
    ),

    "stay_for_arbitration": CostRange(
        min_cost=5000,
        max_cost=23000,
        notes=["Stay of proceedings for arbitration"]
    ),

    "stay_forum_non_conveniens": CostRange(
        min_cost=6000,
        max_cost=21000,
        notes=["Stay of proceedings on forum non conveniens"]
    ),

    "stay_pending_appeal": CostRange(
        min_cost=3000,
        max_cost=11000,
        notes=["Stay of proceedings pending appeal"]
    ),

    "examination_enforcement_respondent": CostRange(
        min_cost=3000,
        max_cost=10000,
        notes=["Examination of Enforcement Respondent"]
    ),

    "discharge_of_solicitor": CostRange(
        min_cost=1000,
        max_cost=4000,
        notes=[]
    ),

    "setting_aside_service": CostRange(
        min_cost=3000,
        max_cost=14000,
        notes=["Setting aside of service"]
    ),

    "permission_to_appeal": CostRange(
        min_cost=4000,
        max_cost=15000,
        notes=["Permission to appeal to the Appellate Division or Court of Appeal"]
    ),

    "division_of_issues": CostRange(
        min_cost=3000,
        max_cost=12000,
        notes=["Division of issues at trial to be heard separately"]
    ),

    "injunction_search_order": CostRange(
        min_cost=10000,
        max_cost=35000,
        notes=["Injunction / search order"]
    ),

    "committal_order": CostRange(
        min_cost=4000,
        max_cost=16000,
        notes=["Application for committal order"]
    ),

    "unless_order": CostRange(
        min_cost=2000,
        max_cost=10000,
        notes=["Application for unless order"]
    )
}


# ============================================================================
# PART III: COSTS GUIDELINES FOR TRIALS
# ============================================================================

@dataclass
class TrialCosts:
    """Represents costs for a trial with pre-trial, trial, and post-trial phases."""
    pre_trial_min: float
    pre_trial_max: float
    trial_daily_min: float
    trial_daily_max: float
    post_trial_max: float
    notes: List[str] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = []


@dataclass
class SettledCosts:
    """Represents costs for matters settled before trial."""
    pleadings_min: float
    pleadings_max: float
    production_docs_min: float
    production_docs_max: float
    aeiCs_min: float
    aeiCs_max: float
    notes: List[str] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = []


# Part III.A: Party-and-Party Costs for Trials (except settled before trial)
TRIAL_COSTS = {
    "motor_accident": TrialCosts(
        pre_trial_min=15000,
        pre_trial_max=45000,
        trial_daily_min=6000,
        trial_daily_max=12000,
        post_trial_max=15000,
        notes=["Pre-trial Work includes Pleadings, Production of Documents, and AEICs"]
    ),

    "simple_torts": TrialCosts(
        pre_trial_min=15000,
        pre_trial_max=45000,
        trial_daily_min=6000,
        trial_daily_max=12000,
        post_trial_max=15000,
        notes=["Pre-trial Work includes Pleadings, Production of Documents, and AEICs"]
    ),

    "torts": TrialCosts(
        pre_trial_min=25000,
        pre_trial_max=70000,
        trial_daily_min=6000,
        trial_daily_max=16000,
        post_trial_max=30000,
        notes=[
            "Includes Defamation",
            "Pre-trial Work includes Pleadings, Production of Documents, and AEICs"
        ]
    ),

    "commercial": TrialCosts(
        pre_trial_min=25000,
        pre_trial_max=70000,
        trial_daily_min=6000,
        trial_daily_max=16000,
        post_trial_max=30000,
        notes=[
            "Includes Corporation/Company law disputes and Insolvency",
            "Includes Contract and Banking and Finance disputes",
            "Pre-trial Work includes Pleadings, Production of Documents, and AEICs"
        ]
    ),

    "equity_and_trusts": TrialCosts(
        pre_trial_min=25000,
        pre_trial_max=90000,
        trial_daily_min=6000,
        trial_daily_max=16000,
        post_trial_max=35000,
        notes=["Pre-trial Work includes Pleadings, Production of Documents, and AEICs"]
    ),

    "construction": TrialCosts(
        pre_trial_min=30000,
        pre_trial_max=90000,
        trial_daily_min=6000,
        trial_daily_max=18000,
        post_trial_max=35000,
        notes=["Pre-trial Work includes Pleadings, Production of Documents, and AEICs"]
    ),

    "intellectual_property": TrialCosts(
        pre_trial_min=30000,
        pre_trial_max=90000,
        trial_daily_min=6000,
        trial_daily_max=18000,
        post_trial_max=35000,
        notes=[
            "Intellectual property and information technology",
            "Pre-trial Work includes Pleadings, Production of Documents, and AEICs"
        ]
    ),

    "admiralty": TrialCosts(
        pre_trial_min=30000,
        pre_trial_max=90000,
        trial_daily_min=6000,
        trial_daily_max=18000,
        post_trial_max=35000,
        notes=["Pre-trial Work includes Pleadings, Production of Documents, and AEICs"]
    ),

    "medical_negligence": TrialCosts(
        pre_trial_min=30000,
        pre_trial_max=90000,
        trial_daily_min=6000,
        trial_daily_max=18000,
        post_trial_max=35000,
        notes=[
            "Medical and Professional negligence",
            "Pre-trial Work includes Pleadings, Production of Documents, and AEICs"
        ]
    )
}

# Part III.A(ii): Costs for matters settled before trial
SETTLED_BEFORE_TRIAL_COSTS = {
    "motor_accident": SettledCosts(
        pleadings_min=3000, pleadings_max=9000,
        production_docs_min=6000, production_docs_max=18000,
        aeiCs_min=6000, aeiCs_max=18000,
        notes=["Court may consider additional costs for getting up for trial"]
    ),

    "simple_torts": SettledCosts(
        pleadings_min=3000, pleadings_max=9000,
        production_docs_min=6000, production_docs_max=18000,
        aeiCs_min=6000, aeiCs_max=18000,
        notes=["Court may consider additional costs for getting up for trial"]
    ),

    "torts": SettledCosts(
        pleadings_min=5000, pleadings_max=14000,
        production_docs_min=10000, production_docs_max=28000,
        aeiCs_min=10000, aeiCs_max=28000,
        notes=[
            "Includes Defamation",
            "Court may consider additional costs for getting up for trial"
        ]
    ),

    "commercial": SettledCosts(
        pleadings_min=5000, pleadings_max=14000,
        production_docs_min=10000, production_docs_max=28000,
        aeiCs_min=10000, aeiCs_max=28000,
        notes=[
            "Includes Corporation/Company law, Insolvency, Contract, Banking and Finance",
            "Court may consider additional costs for getting up for trial"
        ]
    ),

    "equity_and_trusts": SettledCosts(
        pleadings_min=5000, pleadings_max=18000,
        production_docs_min=10000, production_docs_max=35000,
        aeiCs_min=10000, aeiCs_max=35000,
        notes=["Court may consider additional costs for getting up for trial"]
    ),

    "construction": SettledCosts(
        pleadings_min=6000, pleadings_max=18000,
        production_docs_min=12000, production_docs_max=35000,
        aeiCs_min=12000, aeiCs_max=35000,
        notes=["Court may consider additional costs for getting up for trial"]
    ),

    "intellectual_property": SettledCosts(
        pleadings_min=6000, pleadings_max=18000,
        production_docs_min=12000, production_docs_max=35000,
        aeiCs_min=12000, aeiCs_max=35000,
        notes=[
            "Intellectual property and information technology",
            "Court may consider additional costs for getting up for trial"
        ]
    ),

    "admiralty": SettledCosts(
        pleadings_min=6000, pleadings_max=18000,
        production_docs_min=12000, production_docs_max=35000,
        aeiCs_min=12000, aeiCs_max=35000,
        notes=["Court may consider additional costs for getting up for trial"]
    ),

    "medical_negligence": SettledCosts(
        pleadings_min=6000, pleadings_max=18000,
        production_docs_min=12000, production_docs_max=35000,
        aeiCs_min=12000, aeiCs_max=35000,
        notes=[
            "Medical and Professional negligence",
            "Court may consider additional costs for getting up for trial"
        ]
    )
}

# Part III.B: Costs for assessment
ASSESSMENT_COSTS = CostRange(
    min_cost=1500,
    max_cost=5000,
    notes=["Excludes disbursements"]
)


# ============================================================================
# PART IV: COSTS GUIDELINES FOR ORIGINATING APPLICATIONS
# ============================================================================

# Part IV.A: General Guidelines
ORIGINATING_APPLICATION_GENERAL = {
    "uncontested": CostRange(
        min_cost=5000,
        max_cost=13000,
        notes=["Inclusive of pre-hearing and post-hearing work", "Excludes enforcement proceedings"]
    ),
    "contested_per_day": CostRange(
        min_cost=12000,
        max_cost=30000,
        notes=["Per day", "Inclusive of pre-hearing and post-hearing work", "Excludes enforcement proceedings"]
    )
}

# Part IV.B: Specific Originating Applications
ORIGINATING_APPLICATION_SPECIFIC = {
    "arbitration": CostRange(
        min_cost=13000,
        max_cost=40000,
        notes=["Daily tariff", "Inclusive of pre-hearing and post-hearing work", "Excludes enforcement proceedings"]
    ),

    "insolvency_and_restructuring": CostRange(
        min_cost=12000,
        max_cost=35000,
        notes=["Daily tariff", "Inclusive of pre-hearing and post-hearing work", "Excludes enforcement proceedings"]
    ),

    "judicial_review": CostRange(
        min_cost=14000,
        max_cost=35000,
        notes=[
            "Judicial review, public and administrative law",
            "Daily tariff",
            "Inclusive of pre-hearing and post-hearing work",
            "Excludes enforcement proceedings"
        ]
    ),

    "mortgage_action": CostRange(
        min_cost=5000,
        max_cost=15000,
        notes=["Inclusive of pre-hearing and post-hearing work", "Excludes enforcement proceedings"]
    ),

    "order_6_rule_1_3_c": CostRange(
        min_cost=12000,
        max_cost=30000,
        notes=[
            "Originating applications commenced under Order 6, Rule 1(3)(c)",
            "Daily tariff",
            "Inclusive of pre-hearing and post-hearing work",
            "Excludes enforcement proceedings"
        ]
    ),

    "sopa": CostRange(
        min_cost=6000,
        max_cost=20000,
        notes=[
            "Building and Construction Industry Security of Payment Act 2004",
            "Inclusive of pre-hearing and post-hearing work",
            "Excludes enforcement proceedings"
        ]
    )
}


# ============================================================================
# PART V: COSTS GUIDELINES FOR APPEALS
# ============================================================================

APPEAL_COSTS = {
    "general_division": CostRange(
        min_cost=5000,
        max_cost=35000,
        notes=[
            "Appeals before a Judge in the General Division",
            "Includes appeals from the State Courts",
            "Per appeal/application basis"
        ]
    ),

    "appellate_division_interlocutory": CostRange(
        min_cost=15000,
        max_cost=40000,
        notes=[
            "Appeals before Appellate Division or Court of Appeal",
            "Against judgment/order from interlocutory application",
            "Court of Appeal may adjust costs if further appeal granted",
            "Per appeal/application basis"
        ]
    ),

    "appellate_division_trial": CostRange(
        min_cost=30000,
        max_cost=150000,
        notes=[
            "Appeals before Appellate Division or Court of Appeal",
            "Against judgment/order following trial or hearing of Originating Application",
            "Court of Appeal may adjust costs if further appeal granted",
            "Per appeal/application basis"
        ]
    ),

    "applications_without_hearing": CostRange(
        min_cost=6000,
        max_cost=20000,
        notes=[
            "Applications determined by Appellate Division or Court of Appeal",
            "Without oral hearing",
            "Per appeal/application basis"
        ]
    ),

    "applications_with_hearing": CostRange(
        min_cost=9000,
        max_cost=35000,
        notes=[
            "Applications determined by Appellate Division or Court of Appeal",
            "After an oral hearing",
            "Per appeal/application basis"
        ]
    )
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_summons_cost(application_type: str, contested: bool = True,
                     duration_mins: Optional[int] = None) -> CostRange:
    """
    Get cost range for a summons application.

    Args:
        application_type: Type of application (e.g., 'striking_out_whole')
        contested: Whether the application is contested
        duration_mins: Duration of hearing in minutes (for general guidelines)

    Returns:
        CostRange object with min/max costs and notes
    """
    # Try specific application types first (Part IIB)
    if application_type in SUMMONS_SPECIFIC:
        return SUMMONS_SPECIFIC[application_type]

    # Fall back to general guidelines (Part IIA)
    if not contested:
        return SUMMONS_GENERAL["uncontested"]

    if duration_mins is None:
        # Default to middle range
        return SUMMONS_GENERAL["contested_45_mins_or_longer"]
    elif duration_mins < 45:
        return SUMMONS_GENERAL["contested_less_45_mins"]
    elif duration_mins >= 180:  # 3 hours
        return SUMMONS_GENERAL["complex_3hrs"]
    else:
        return SUMMONS_GENERAL["contested_45_mins_or_longer"]


def get_trial_cost(case_category: str, trial_days: Optional[int] = None,
                   settled_before_trial: bool = False) -> Dict[str, Any]:
    """
    Get cost breakdown for a trial.

    Args:
        case_category: Category of case (e.g., 'commercial', 'construction')
        trial_days: Number of trial days (None if not yet determined)
        settled_before_trial: Whether matter was settled before trial

    Returns:
        Dictionary with cost breakdown
    """
    if settled_before_trial:
        if case_category not in SETTLED_BEFORE_TRIAL_COSTS:
            raise ValueError(f"Unknown case category: {case_category}")

        costs = SETTLED_BEFORE_TRIAL_COSTS[case_category]
        return {
            "type": "settled_before_trial",
            "pleadings": {"min": costs.pleadings_min, "max": costs.pleadings_max},
            "production_of_documents": {"min": costs.production_docs_min, "max": costs.production_docs_max},
            "aeiCs": {"min": costs.aeiCs_min, "max": costs.aeiCs_max},
            "total_min": costs.pleadings_min + costs.production_docs_min + costs.aeiCs_min,
            "total_max": costs.pleadings_max + costs.production_docs_max + costs.aeiCs_max,
            "notes": costs.notes
        }
    else:
        if case_category not in TRIAL_COSTS:
            raise ValueError(f"Unknown case category: {case_category}")

        costs = TRIAL_COSTS[case_category]

        # Calculate trial costs based on number of days
        if trial_days:
            trial_min = costs.trial_daily_min * trial_days
            trial_max = costs.trial_daily_max * trial_days
        else:
            # Assume 1 day if not specified
            trial_min = costs.trial_daily_min
            trial_max = costs.trial_daily_max

        return {
            "type": "trial",
            "pre_trial": {"min": costs.pre_trial_min, "max": costs.pre_trial_max},
            "trial": {
                "min": trial_min,
                "max": trial_max,
                "daily_min": costs.trial_daily_min,
                "daily_max": costs.trial_daily_max,
                "days": trial_days or 1
            },
            "post_trial": {"max": costs.post_trial_max},
            "total_min": costs.pre_trial_min + trial_min,
            "total_max": costs.pre_trial_max + trial_max + costs.post_trial_max,
            "notes": costs.notes
        }


def get_originating_application_cost(app_type: str, contested: bool = True,
                                     days: Optional[int] = None) -> CostRange:
    """
    Get cost range for an originating application.

    Args:
        app_type: Type of application (e.g., 'arbitration', 'insolvency')
        contested: Whether contested
        days: Number of days (for contested applications)

    Returns:
        CostRange object
    """
    # Try specific types first
    if app_type in ORIGINATING_APPLICATION_SPECIFIC:
        cost_range = ORIGINATING_APPLICATION_SPECIFIC[app_type]
        # For daily tariff types, multiply by days
        if days and days > 1 and "Daily tariff" in cost_range.notes:
            return CostRange(
                min_cost=cost_range.min_cost * days,
                max_cost=cost_range.max_cost * days,
                notes=cost_range.notes + [f"Calculated for {days} days"]
            )
        return cost_range

    # Fall back to general
    if not contested:
        return ORIGINATING_APPLICATION_GENERAL["uncontested"]
    else:
        cost_range = ORIGINATING_APPLICATION_GENERAL["contested_per_day"]
        if days and days > 1:
            return CostRange(
                min_cost=cost_range.min_cost * days,
                max_cost=cost_range.max_cost * days,
                notes=cost_range.notes + [f"Calculated for {days} days"]
            )
        return cost_range


def get_appeal_cost(appeal_level: str, appeal_from: Optional[str] = None) -> CostRange:
    """
    Get cost range for an appeal.

    Args:
        appeal_level: Level of appeal (e.g., 'general_division', 'appellate_division')
        appeal_from: What the appeal is from (e.g., 'interlocutory', 'trial')

    Returns:
        CostRange object
    """
    if appeal_level == "general_division":
        return APPEAL_COSTS["general_division"]

    elif appeal_level in ["appellate_division", "court_of_appeal"]:
        if appeal_from == "interlocutory":
            return APPEAL_COSTS["appellate_division_interlocutory"]
        elif appeal_from == "trial":
            return APPEAL_COSTS["appellate_division_trial"]
        else:
            # Default to interlocutory if not specified
            return APPEAL_COSTS["appellate_division_interlocutory"]

    elif appeal_level == "applications_without_hearing":
        return APPEAL_COSTS["applications_without_hearing"]

    elif appeal_level == "applications_with_hearing":
        return APPEAL_COSTS["applications_with_hearing"]

    else:
        raise ValueError(f"Unknown appeal level: {appeal_level}")


# ============================================================================
# METADATA
# ============================================================================

APPENDIX_G_METADATA = {
    "version": "1.0",
    "last_updated": "October 2025",
    "source": "Practice Directions Para. 138(1) - Appendix G",
    "authority": "Guidelines for Party-and-Party Costs Awards in the Supreme Court of Singapore",
    "total_scenarios": {
        "summonses_general": 4,
        "summonses_specific": 23,
        "trial_categories": 9,
        "originating_applications": 8,
        "appeal_levels": 5,
        "total": 49
    },
    "important_notes": [
        "These are guidelines, not fixed scales",
        "Court retains discretion to depart from guidelines",
        "Must consider Order 21, Rule 2(2) factors",
        "Costs exclude disbursements unless stated",
        "Post-trial work excludes enforcement proceedings"
    ]
}
