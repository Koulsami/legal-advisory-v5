"""
Case Law Database for Order 21 Rules of Court 2021
Singapore Judicial Interpretations (2022-2025)

This module contains structured case law data from Singapore courts
interpreting Order 21 of the Rules of Court 2021.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import date


@dataclass
class CaseLaw:
    """Represents a single case law entry"""
    case_id: str
    citation: str
    short_name: str
    year: int
    court: str  # SGCA, SGHC, SGHCR, SGHC(A)
    provision: str  # e.g., "Order 21 r 2(1)"
    principle: str  # Short summary
    interpretation: str  # Full interpretation
    verbatim_quote: str  # Direct quote from judgment
    paragraph_ref: str  # Paragraph numbers
    keywords: List[str]  # For searching
    relevance_tags: List[str]  # For matching to scenarios

    def get_formatted_citation(self) -> str:
        """Return formatted citation for display"""
        return f"*{self.short_name}* {self.citation}"

    def get_authority_statement(self) -> str:
        """Return statement suitable for legal writing"""
        return f"In {self.short_name} {self.citation}, the {self._get_court_name()} held that {self.principle.lower()}"

    def _get_court_name(self) -> str:
        """Convert court code to full name"""
        court_names = {
            "SGCA": "Court of Appeal",
            "SGHC": "High Court",
            "SGHCR": "High Court Registrar",
            "SGHC(A)": "Appellate Division of the High Court"
        }
        return court_names.get(self.court, "Court")


# ====================================================================================
# CASE LAW DATABASE
# ====================================================================================

CASE_LAW_DATABASE: Dict[str, List[CaseLaw]] = {

    # ================================================================================
    # POWER TO STAY APPEALS (Order 21 r 2(6))
    # ================================================================================
    "stay_appeals": [
        CaseLaw(
            case_id="2024_SGHCA_33",
            citation="[2024] SGHC(A) 33",
            short_name="Huttons Asia Pte Ltd v Chen Qiming",
            year=2024,
            court="SGHC(A)",
            provision="Order 21 r 2(6)",
            principle="Power to stay appeals for non-payment of costs is now express statutory power",
            interpretation="""Order 21 r 2(6) is a new and important provision that expressly empowers the court to stay or dismiss any application, action or appeal if a party refuses or neglects to pay costs ordered within the specified time. This provision obviates the need to rely on the court's inherent powers and represents a more robust approach compared to the previous Rules of Court 2014. The court now has express statutory power to stay appeals pending payment of costs below, and this power should be exercised when a party refuses or neglects to pay ordered costs, without needing to establish "special or exceptional circumstances" as was required under the old regime.""",
            verbatim_quote="""O 21 r 2(6) of the ROC 2021 now expressly stipulates that the court has the power to stay appeals pending payment of the costs below: Powers of Court (O. 21, r. 2) … (6) The Court may stay or dismiss any application, action or appeal or make any other order as the Court deems fit if a party refuses or neglects to pay any costs ordered within the specified time, whether the costs were ordered in the present proceedings or in some related proceedings. This is a new provision not previously found in the ROC 2014.""",
            paragraph_ref="[23-24]",
            keywords=["stay", "appeal", "non-payment", "costs", "express power", "statutory"],
            relevance_tags=["appeal", "stay_application", "enforcement", "non_payment"]
        ),
        CaseLaw(
            case_id="2024_SGHCA_33_discretion",
            citation="[2024] SGHC(A) 33",
            short_name="Huttons Asia Pte Ltd v Chen Qiming",
            year=2024,
            court="SGHC(A)",
            provision="Order 21 r 2(6)",
            principle="Power to stay appeals is discretionary and must be exercised judiciously",
            interpretation="""While Order 21 r 2(6) expressly empowers the court to stay or dismiss appeals where a party refuses or neglects to pay costs ordered, this power is discretionary (using "may" rather than "shall"). The court's discretion must be exercised judiciously. The situations mentioned in earlier cases under the inherent powers regime may remain useful as relevant circumstances to take into account, but the threshold is no longer "special or exceptional circumstances" as was required under the old inherent powers. The express statutory provision reflects a more robust approach aligned with the Ideals in Order 3 r 1(2) of the ROC 2021, particularly to achieve fair and practical results suited to the needs of the parties.""",
            verbatim_quote="""O 21 r 2(6) is not phrased in mandatory terms. Given the use of the word "may", as opposed to "shall", this highlights that the court is vested with the discretion to decide whether to stay an appeal pending payment of the costs below. The court's discretion must of course be exercised judiciously.""",
            paragraph_ref="[29, 27]",
            keywords=["discretion", "stay", "appeal", "judicious", "robust approach"],
            relevance_tags=["appeal", "stay_application", "discretion", "judicial_approach"]
        ),
    ],

    # ================================================================================
    # COURT'S DISCRETION ON COSTS (Order 21 r 2(1))
    # ================================================================================
    "courts_discretion": [
        CaseLaw(
            case_id="2023_SGCA_40",
            citation="[2023] SGCA 40",
            short_name="Founder Group (Hong Kong) Ltd v Singapore JHC Co Pte Ltd",
            year=2023,
            court="SGCA",
            provision="Order 21 r 2(1)",
            principle="Wide discretionary power on costs is not constrained by specific non-party costs provisions",
            interpretation="""Order 21 r 2(1) preserves the wide discretionary power of the court to determine all issues relating to costs. This broad discretion is not constrained by Order 21 r 5, which specifies certain situations for non-party cost orders. The court retains a general power to order costs against non-parties where it is just to do so, beyond the specific situations listed in Order 21 r 5(1). The language of O 21 r 5 does not limit the court's power under O 21 r 2(1) to order costs against non-parties only in specified situations. Two factors should "almost always" be present: (1) close connection between non-party and proceedings (funding or control), and (2) the non-party must have caused the incurring of costs.""",
            verbatim_quote="""Order 59 r 2(2) of the ROC 2014 is preserved in O 21 r 2(1) of the ROC 2021, which provides as follows: Powers of Court (O. 21, r. 2) 2.—(1) Subject to any written law, costs are in the discretion of the Court and the Court has the power to determine all issues relating to the costs of or incidental to all proceedings in the Supreme Court or the State Courts at any stage of the proceedings or after the conclusion of the proceedings.""",
            paragraph_ref="[74-75]",
            keywords=["discretion", "costs", "non-party", "power", "broad"],
            relevance_tags=["discretion", "non_party_costs", "general_principles"]
        ),
        CaseLaw(
            case_id="2025_SGHCR_18_discretion",
            citation="[2025] SGHCR 18",
            short_name="Armira Capital Ltd v Ji Zenghe",
            year=2025,
            court="SGHCR",
            provision="Order 21 r 2(1)",
            principle="Court's discretion on costs cannot be fettered by private contractual arrangements",
            interpretation="""Order 21 r 2(1) establishes that costs are in the discretion of the court and the court has the power to determine all issues relating to costs. This important principle means that even where there is a contractual indemnity for costs, the court retains its discretion to assess costs and cannot have that discretion fettered by private contractual arrangements. A contractual clause attempting to provide for 100% recovery of all lawyer's fees as billed would constitute an attempt to fetter the court's discretion and would not be upheld. The court must still scrutinize costs claimed, even under an indemnity basis.""",
            verbatim_quote="""Order 2 r 13(1) of the Rules states that costs are in the discretion of the court and the court has the power to determine all issues relating to the costs of or incidental to all proceedings. This important principle is reiterated in Order 21 r 2(1) of the Rules. Such a clause may constitute an attempt to fetter that discretion.""",
            paragraph_ref="[30]",
            keywords=["discretion", "contractual indemnity", "fetter", "scrutiny"],
            relevance_tags=["discretion", "indemnity_basis", "contractual_costs"]
        ),
    ],

    # ================================================================================
    # FACTORS IN EXERCISING DISCRETION (Order 21 r 2(2))
    # ================================================================================
    "discretion_factors": [
        CaseLaw(
            case_id="2025_SGHCR_18_factors",
            citation="[2025] SGHCR 18",
            short_name="Armira Capital Ltd v Ji Zenghe",
            year=2025,
            court="SGHCR",
            provision="Order 21 r 2(2)",
            principle="Court must consider proportionality even when assessing costs on indemnity basis",
            interpretation="""Order 21 r 2(2) sets out non-exhaustive factors that the court must have regard to in exercising its power to fix or assess costs. These include: (a) efforts at amicable resolution; (b) complexity and difficulty; (c) skill, knowledge and time expended; (d) urgency and importance; (e) number of solicitors; (f) conduct of parties; (g) proportionality; and (h) stage of proceedings. The court MUST have regard to proportionality under Order 21 r 2(2)(g), even when assessing costs on an indemnity basis. This is a mandatory consideration that cannot be overridden by foreign assessment practices or contractual arrangements.""",
            verbatim_quote="""Order 21 r 2(2) of the Rules reads as follows: (2) In exercising its power to fix or assess costs, the Court must have regard to all relevant circumstances, including — (a) efforts made by the parties at amicable resolution; (b) the complexity of the case and the difficulty or novelty of the questions involved; (c) the skill, specialised knowledge and responsibility required of, and the time and labour expended by, the solicitor; (d) the urgency and importance of the action to the parties; (e) the number of solicitors involved in the case for each party; (f) the conduct of the parties; (g) the principle of proportionality; and (h) the stage at which the proceedings were concluded.""",
            paragraph_ref="[46-47, 103]",
            keywords=["proportionality", "factors", "discretion", "mandatory", "indemnity"],
            relevance_tags=["proportionality", "indemnity_basis", "assessment_factors"]
        ),
        CaseLaw(
            case_id="2023_SGCA_45_conduct",
            citation="[2023] SGCA 45",
            short_name="QBE Insurance (Singapore) Pte Ltd v Relax Beach Co Ltd",
            year=2023,
            court="SGCA",
            provision="Order 21 r 2(2)(f)",
            principle="Conduct of parties is especially important for indemnity costs claims",
            interpretation="""In exercising its discretion to award costs, particularly indemnity costs, the court must have regard to all relevant circumstances under Order 21 r 2(2), including complexity, efforts at amicable resolution, and difficulty of questions involved. Indemnity costs are only granted in exceptional circumstances and need to be specifically justified. The merits of the case are especially important when dealing with indemnity costs claims because it goes to whether the position taken was wholly without basis. The touchstone is unreasonable conduct, not conduct that attracts moral condemnation. A completely unmeritorious action may justify indemnity costs, but withdrawal of an appeal shortly before hearing does not automatically justify indemnity costs.""",
            verbatim_quote="""In the context of a court exercising its discretion to award costs, and, in particular, when dealing with a claim for indemnity costs, the merits of the case can become especially important because it goes to the heart of the question of whether the position taken was wholly without basis, thus resulting in a waste of time and resource.""",
            paragraph_ref="[35-36]",
            keywords=["conduct", "indemnity costs", "exceptional", "merits", "unreasonable"],
            relevance_tags=["indemnity_basis", "conduct", "exceptional_circumstances"]
        ),
    ],

    # ================================================================================
    # COSTS FOLLOW THE EVENT (Order 21 r 3(2))
    # ================================================================================
    "costs_follow_event": [
        CaseLaw(
            case_id="2024_SGHC_146",
            citation="[2024] SGHC 146",
            short_name="Tjiang Giok Moy v Ang Jimmy Tjun Min",
            year=2024,
            court="SGHC",
            provision="Order 21 r 3(2)",
            principle="Successful party entitled to costs except in exceptional circumstances",
            interpretation="""Order 21 r 3(2) codifies the principle that costs follow the event. The court must order costs in favour of a successful party, except when circumstances warrant a different order. A party who exercises their right to appear and be heard, and whose objections are successful, is entitled to costs as a successful party. The mere fact that a party's submissions require review by the counterparty does not make those submissions an unnecessary protraction of proceedings - parties with standing have a right to be heard.""",
            verbatim_quote="""Order 21 r 3(2) of the ROC 2021 provides that: The Court must, subject to this Order, order the costs of any proceedings in favour of a successful party, except when it appears to the Court that in the circumstances of the case some other order should be made as to the whole or any part of the costs.""",
            paragraph_ref="[7-8]",
            keywords=["costs follow event", "successful party", "standing", "right to be heard"],
            relevance_tags=["successful_party", "general_principles", "standing"]
        ),
    ],

    # ================================================================================
    # INDEMNITY COSTS AND ASSESSMENT (Order 21 r 22(3))
    # ================================================================================
    "indemnity_assessment": [
        CaseLaw(
            case_id="2025_SGHCR_18_indemnity",
            citation="[2025] SGHCR 18",
            short_name="Armira Capital Ltd v Ji Zenghe",
            year=2025,
            court="SGHCR",
            provision="Order 21 r 22(3)",
            principle="Indemnity basis requires item-by-item assessment with Lin Jian Wei approach",
            interpretation="""Order 21 r 22(3) provides that on assessment on an indemnity basis, all costs are to be allowed except insofar as they are of an unreasonable amount or have been unreasonably incurred. Any doubts must be resolved in favour of the receiving party. However, this does not mean automatic acceptance of all costs claimed. The Lin Jian Wei approach continues to apply under the Rules of Court 2021: the court should assess the relative complexity, reasonableness and proportionality of amounts claimed on an item-by-item basis, then assess the proportionality of the resulting aggregate costs. All Order 21 r 2(2) considerations are relevant. Indemnity costs are generally one-third more than standard costs, but this is a rule of guidance, not a hard and fast rule.""",
            verbatim_quote="""Where costs are to be assessed on an indemnity basis, Order 21 r 22(3) of the Rules states that all costs are to be allowed except in so far as they are of an unreasonable amount or have been unreasonably incurred, and any doubts which the Registrar may have as to whether the costs were reasonably incurred or were reasonable in amount are to be resolved in favour of the receiving party.""",
            paragraph_ref="[23, 43]",
            keywords=["indemnity", "assessment", "Lin Jian Wei", "item-by-item", "proportionality"],
            relevance_tags=["indemnity_basis", "assessment", "taxation"]
        ),
        CaseLaw(
            case_id="2025_SGHCR_18_purpose",
            citation="[2025] SGHCR 18",
            short_name="Armira Capital Ltd v Ji Zenghe",
            year=2025,
            court="SGHCR",
            provision="Order 21 r 2(2) and Indemnity Costs",
            principle="Indemnity principle serves to compensate winner and enhance access to justice",
            interpretation="""The indemnity principle makes the vindicated winner whole for the costs of what has been shown, by the court's judgment, to be unmeritorious litigation. It serves to compensate the winner rather than to punish the loser. The ultimate policy of the indemnity principle is rooted not in compensation but in enhancing access to justice. The indemnity principle facilitates a meritorious litigant's pursuit of justice by ensuring retrospectively that they attain justice at their opponent's expense rather than their own. Costs should be assessed by reference to generally accepted reasonable levels to ensure access to justice, and should not be dependent on subjective factors such as how much an individual litigant might have been willing to spend.""",
            verbatim_quote="""The indemnity principle makes the vindicated winner whole for the costs of what he has shown, by the court's judgment, to be unmeritorious litigation. It therefore serves to compensate the winner, rather than to punish the loser for his original wrongdoing. The ultimate policy of the indemnity principle is rooted not in compensation but in enhancing access to justice.""",
            paragraph_ref="[79-80]",
            keywords=["indemnity principle", "access to justice", "compensation", "vindicated winner"],
            relevance_tags=["indemnity_basis", "policy", "access_to_justice"]
        ),
    ],

    # ================================================================================
    # CONDUCT AND INDEMNITY COSTS (Order 21 r 2(2)(f))
    # ================================================================================
    "conduct_indemnity": [
        CaseLaw(
            case_id="2024_SGHC_146_conduct",
            citation="[2024] SGHC 146",
            short_name="Tjiang Giok Moy v Ang Jimmy Tjun Min",
            year=2024,
            court="SGHC",
            provision="Order 21 r 2(2)(f)",
            principle="Four categories of conduct justify indemnity costs",
            interpretation="""Under Order 21 r 2(2)(f), the court must have regard to the conduct of the parties in fixing costs. Indemnity costs are an exception rather than the norm. There are four broad categories of conduct that may justify indemnity costs: (1) where action is brought in bad faith, as means of oppression or for improper purposes; (2) where action is speculative, hypothetical or clearly without basis; (3) where a party's conduct during proceedings is dishonest, abusive or improper; and (4) where action amounts to wasteful or duplicative litigation or abuse of process. The critical requirement is that there must be some conduct or circumstance which takes the case out of the norm. Whether the party's conduct caused prejudice to the other party, the context and nature of the dispute, and the general penal element to indemnity costs are all relevant factors.""",
            verbatim_quote="""Without attempting to be prescriptive, there are, from my review of the case law, the following broad categories of conduct by a party which may provide good reason for an order of indemnity costs to be made: (a) where the action is brought in bad faith, as a means of oppression or for other improper purposes; (b) where the action is speculative, hypothetical or clearly without basis; (c) where a party's conduct in the course of proceedings is dishonest, abusive or improper; and (d) where the action amounts to wasteful or duplicative litigation or is otherwise an abuse of process.""",
            paragraph_ref="[14-15]",
            keywords=["conduct", "indemnity", "bad faith", "abuse", "improper", "categories"],
            relevance_tags=["indemnity_basis", "conduct", "exceptional_circumstances", "bad_faith"]
        ),
    ],

    # ================================================================================
    # NON-PARTY COSTS (Order 21 r 5)
    # ================================================================================
    "non_party_costs": [
        CaseLaw(
            case_id="2023_SGCA_40",
            citation="[2023] SGCA 40",
            short_name="Founder Group (Hong Kong) Ltd v Singapore JHC Co Pte Ltd",
            year=2023,
            court="SGCA",
            provision="Order 21 r 5",
            principle="Court retains broad power to order costs against non-parties beyond specified situations",
            interpretation="""Order 21 r 2(1) preserves the wide discretionary power of the court to determine all issues relating to costs. This broad discretion is not constrained by Order 21 r 5, which specifies certain situations for non-party cost orders. The court retains a general power to order costs against non-parties where it is just to do so, beyond the specific situations listed in Order 21 r 5(1). The language of O 21 r 5 does not limit the court's power under O 21 r 2(1) to order costs against non-parties only in specified situations.""",
            verbatim_quote="""Further, there is nothing in the language of O 21 r 5 of the ROC 2021 that suggests it is meant to constrain the wide discretion of the court that is provided for in O 21 r 2(1), or to otherwise limit the court's power to order costs against non-parties to the specific situations mentioned there. In our judgment, the court retains a broad power to order costs against a non-party where it is just to do so.""",
            paragraph_ref="[74-75]",
            keywords=["non-party", "discretion", "broad power", "just"],
            relevance_tags=["non_party_costs", "discretion"]
        ),
    ],

    # ================================================================================
    # SOLICITOR COSTS ORDERS (Order 21 r 6)
    # ================================================================================
    "solicitor_costs": [
        CaseLaw(
            case_id="2025_SGHCR_33",
            citation="[2025] SGHCR 33",
            short_name="Tajudin bin Gulam Rasul v Suriaya bte Haja Mohideen",
            year=2025,
            court="SGHCR",
            provision="Order 21 r 6",
            principle="Personal costs orders against solicitors for citing fictitious AI-generated authorities",
            interpretation="""Order 21 rule 6 codifies the court's inherent power to make personal costs orders against advocates and solicitors. Where an advocate and solicitor cites a fictitious AI-generated authority to the court, the court may make a personal costs order against them. The underlying principle is that advocates and solicitors are officers of the court, and the court has a right and duty to supervise their conduct and penalize conduct that tends to defeat justice. This is based on two practical and ethical considerations: (1) solicitors have a duty to exercise reasonable care and skill in conducting clients' affairs despite immunity from negligence claims for court work, and (2) a litigant should not be financially prejudiced by unjustifiable conduct by the counterparty or their solicitor.""",
            verbatim_quote="""In the context of civil proceedings, this inherent power has been codified in Order 21 rule 6 of the Rules of Court 2021. Where an advocate and solicitor cites a fictitious AI-generated authority to the court, the court may make a personal costs order against him.""",
            paragraph_ref="[44-46]",
            keywords=["solicitor", "personal costs", "AI", "fictitious authority", "officer of court"],
            relevance_tags=["solicitor_costs", "professional_conduct", "AI_hallucination"]
        ),
    ],

    # ================================================================================
    # LITIGANTS-IN-PERSON (Order 21 r 7)
    # ================================================================================
    "litigant_in_person": [
        CaseLaw(
            case_id="2022_SGHC_232",
            citation="[2022] SGHC 232",
            short_name="Chan Hui Peng v Public Utilities Board",
            year=2022,
            court="SGHC",
            provision="Order 21 r 7",
            principle="Costs for litigants-in-person only available to successful parties",
            interpretation="""Order 21 rule 7 allows the court to award costs to a successful party who is not represented by solicitors that would compensate them reasonably for the time and work required for the proceedings and for all expenses incurred reasonably. However, this provision does not entitle a litigant-in-person to costs as of right. The court may award such costs only to a successful litigant-in-person. The fundamental principle that costs follow the event is not displaced - an unsuccessful litigant-in-person has no basis for claiming costs. The compensation should be reasonable for the time and work actually required, not necessarily based on the litigant's work income or subjective valuation of their time.""",
            verbatim_quote="""Order 21 rule 7 of ROC 2021, which reads: The Court may award costs to a successful party who is not represented by solicitors that would compensate him or her reasonably for the time and work required for the proceedings and for all expenses incurred reasonably. The position is even more pointed under the ROC 2021 rule: the court "may award costs to a successful [litigant-in person]" [emphasis added].""",
            paragraph_ref="[65, 68]",
            keywords=["litigant-in-person", "successful party", "reasonable compensation", "time and work"],
            relevance_tags=["litigant_in_person", "successful_party", "compensation"]
        ),
    ],

    # ================================================================================
    # BILL OF COSTS REQUIREMENTS (Order 21 r 20)
    # ================================================================================
    "bill_of_costs": [
        CaseLaw(
            case_id="2025_SGHCR_18_bill",
            citation="[2025] SGHCR 18",
            short_name="Armira Capital Ltd v Ji Zenghe",
            year=2025,
            court="SGHCR",
            provision="Order 21 r 20",
            principle="Bill of Costs must follow prescribed form with three separate sections",
            interpretation="""Order 21 r 20 requires that a Bill of Costs must be filed in accordance with the prescribed forms and practice directions. Specifically, the Bill must set out three separate sections: (1) work done in the cause or matter except for assessment of costs (Section 1), (2) work done for and in the assessment of costs (Section 2), and (3) all disbursements made in the cause or matter (Section 3). This must be done in accordance with Form B31 of Appendix B of the Supreme Court Practice Directions 2021. The factors for the court to take into account under Order 21 r 2(2) should also be set out in Section 1.""",
            verbatim_quote="""As required under Order 21 r 20 of the Rules of Court 2021 ("the Rules") and in accordance with Form B31 of Appendix B of the Supreme Court Practice Directions 2021, BC 171 set out, in three separate sections, the applicant's claim for an award of costs for the following: work done in the cause or matter except for assessment of costs (Section 1), work done for and in the assessment of costs (Section 2) and all disbursements made in the cause or matter (Section 3).""",
            paragraph_ref="[20, 24]",
            keywords=["bill of costs", "form", "sections", "prescribed", "practice directions"],
            relevance_tags=["bill_of_costs", "procedure", "form_requirements"]
        ),
    ],
}


# ====================================================================================
# HELPER FUNCTIONS
# ====================================================================================

def get_all_cases() -> List[CaseLaw]:
    """Return all cases in the database as a flat list"""
    all_cases = []
    for category_cases in CASE_LAW_DATABASE.values():
        all_cases.extend(category_cases)
    return all_cases


def get_cases_by_provision(provision: str) -> List[CaseLaw]:
    """Get all cases interpreting a specific provision"""
    all_cases = get_all_cases()
    return [case for case in all_cases if provision.lower() in case.provision.lower()]


def get_cases_by_keyword(keyword: str) -> List[CaseLaw]:
    """Get all cases matching a keyword"""
    all_cases = get_all_cases()
    keyword_lower = keyword.lower()
    return [case for case in all_cases
            if keyword_lower in [k.lower() for k in case.keywords]]


def get_cases_by_relevance_tag(tag: str) -> List[CaseLaw]:
    """Get all cases with a specific relevance tag"""
    all_cases = get_all_cases()
    return [case for case in all_cases if tag in case.relevance_tags]


def get_cases_by_year_range(start_year: int, end_year: int) -> List[CaseLaw]:
    """Get all cases within a year range"""
    all_cases = get_all_cases()
    return [case for case in all_cases
            if start_year <= case.year <= end_year]


def get_cases_by_court(court: str) -> List[CaseLaw]:
    """Get all cases from a specific court"""
    all_cases = get_all_cases()
    return [case for case in all_cases if case.court.upper() == court.upper()]


# ====================================================================================
# STATISTICS
# ====================================================================================

def get_database_statistics() -> Dict[str, any]:
    """Return statistics about the case law database"""
    all_cases = get_all_cases()

    # Count by court
    courts = {}
    for case in all_cases:
        courts[case.court] = courts.get(case.court, 0) + 1

    # Count by year
    years = {}
    for case in all_cases:
        years[case.year] = years.get(case.year, 0) + 1

    # Count by provision
    provisions = {}
    for case in all_cases:
        provisions[case.provision] = provisions.get(case.provision, 0) + 1

    return {
        "total_cases": len(all_cases),
        "categories": len(CASE_LAW_DATABASE),
        "by_court": courts,
        "by_year": years,
        "by_provision": provisions,
        "year_range": f"{min(years.keys())}-{max(years.keys())}"
    }
