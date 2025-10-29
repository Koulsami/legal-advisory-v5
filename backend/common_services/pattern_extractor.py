"""
Pattern-Based Information Extractor
Legal Advisory System v5.0

Extracts structured information from natural language using regex patterns.
This runs BEFORE AI extraction to catch obvious patterns reliably.
"""

import re
from typing import Dict, Optional, Any
from decimal import Decimal


class PatternExtractor:
    """
    Extracts legal information from natural language using pattern matching.

    More reliable than AI for common patterns:
    - Court levels
    - Case types
    - Monetary amounts
    - Trial durations
    - Claim types (liquidated/unliquidated)
    """

    # Court level patterns
    COURT_PATTERNS = {
        "High Court": r'\b(high\s*court|hc)\b',
        "District Court": r'\b(district\s*court|dc)\b',
        "Magistrates Court": r'\b(magistrates?\s*court|mc)\b',
    }

    # Case type patterns (Order 21)
    CASE_TYPE_PATTERNS = {
        "default_judgment": r'\bdefault\s*judgment\b',
        "summary_judgment": r'\bsummary\s*judgment\b',
        "contested_trial": r'\bcontested\s*trial\b|\btrial\b',
        "assessment_of_damages": r'\bassessment\s*of\s*damages\b',
    }

    # APPLICATION TYPE PATTERNS (Appendix G - Part II: Summonses)
    APPLICATION_TYPE_PATTERNS = {
        "adjournment": r'\badjournment\b',
        "extension_of_time": r'\bextension\s*of\s*time\b|\bextension\b',
        "amendment_of_pleadings": r'\bamendment\s*(?:of\s*)?pleadings?\b|\bamend(?:ing)?\s*pleadings?\b',
        "further_and_better_particulars": r'\bfurther\s*(?:and|&)\s*better\s*particulars\b|\bfbp\b',
        "production_of_documents": r'\bproduction\s*of\s*documents\b|\bdiscovery\b',
        "security_for_costs": r'\bsecurity\s*for\s*costs\b',
        "interim_payments": r'\binterim\s*payments?\b',
        "striking_out_partial": r'\bstriking\s*out\s*(?:part|portion|parts?)\b',
        "striking_out_whole": r'\bstrik(?:e|ing)\s*out\b(?!\s*part)',
        "summary_judgment_given": r'\bsummary\s*judgment\s*(?:given|granted|obtained)\b',
        "summary_judgment_dismissed": r'\bsummary\s*judgment\s*(?:dismissed|rejected|refused)\b',
        "setting_aside_judgment": r'\bsetting\s*aside\s*(?:judgment|order)\b|\bset\s*aside\b',
        "stay_for_arbitration": r'\bstay\s*(?:of\s*)?(?:proceedings?\s*)?for\s*arbitration\b',
        "stay_forum_non_conveniens": r'\bstay\s*(?:on\s*)?forum\s*non\s*conveniens\b|\bfnc\b',
        "stay_pending_appeal": r'\bstay\s*pending\s*appeal\b|\bstay\s*of\s*execution\b',
        "examination_enforcement_respondent": r'\bexamination\s*of\s*(?:enforcement\s*)?respondent\b|\beor\b',
        "discharge_of_solicitor": r'\bdischarge\s*of\s*solicitor\b',
        "setting_aside_service": r'\bsetting\s*aside\s*(?:of\s*)?service\b',
        "permission_to_appeal": r'\bpermission\s*to\s*appeal\b|\bleave\s*to\s*appeal\b',
        "division_of_issues": r'\bdivision\s*of\s*issues\b|\bseparate\s*trials?\b',
        "injunction_search_order": r'\binjunction\b|\bsearch\s*order\b|\bmareva\b|\banton\s*piller\b',
        "committal_order": r'\bcommittal\s*order\b|\bcontempt\b',
        "unless_order": r'\bunless\s*order\b'
    }

    # TRIAL CATEGORY PATTERNS (Appendix G - Part III: Trials)
    TRIAL_CATEGORY_PATTERNS = {
        "motor_accident": r'\bmotor\s*accident\b|\bcar\s*accident\b|\btraffic\s*accident\b|\bmva\b',
        "simple_torts": r'\bsimple\s*tort\b',
        "torts": r'\btort\b|\bdefamation\b|\bnegligence\b(?!\s*medical)(?!\s*professional)',
        "commercial": r'\bcommercial\b|\bcontract\b|\bbreach\s*of\s*contract\b|\bbanking\b|\bfinance\b|\bcorporation\b|\bcompany\s*law\b|\binsolvency\b',
        "equity_and_trusts": r'\bequity\b|\btrust\b|\bfiduciary\b|\bbeneficiary\b',
        "construction": r'\bconstruction\b|\bbuilding\s*contract\b|\bdefects\b',
        "intellectual_property": r'\bintellectual\s*property\b|\b(?:ip|patent|trademark|copyright)\b|\binformation\s*technology\b|\bit\s*dispute\b',
        "admiralty": r'\badmiralty\b|\bmaritime\b|\bshipping\b',
        "medical_negligence": r'\bmedical\s*negligence\b|\bprofessional\s*negligence\b|\bmalpractice\b'
    }

    # TRIAL PHASE PATTERNS
    TRIAL_PHASE_PATTERNS = {
        "pre_trial": r'\bpre[-\s]?trial\b|\bbeforethe trial\b|\bpreparation\b',
        "trial": r'\b(?:during\s*)?trial\b(?!\s*pre)',
        "post_trial": r'\bpost[-\s]?trial\b|\bafter\s*trial\b',
        "settled_before_trial": r'\bsettled\s*before\s*trial\b|\bpre[-\s]?trial\s*settlement\b'
    }

    # ORIGINATING APPLICATION PATTERNS (Appendix G - Part IV)
    ORIGINATING_APP_PATTERNS = {
        "arbitration": r'\barbitration\b',
        "insolvency_and_restructuring": r'\binsolvency\b|\brestructuring\b|\bbankruptcy\b|\bliquidation\b|\bjudicial\s*management\b',
        "judicial_review": r'\bjudicial\s*review\b|\bpublic\s*law\b|\badministrative\s*law\b',
        "mortgage_action": r'\bmortgage\s*action\b|\bforeclosure\b|\bmortgage\s*enforcement\b',
        "sopa": r'\bsopa\b|\bsecurity\s*of\s*payment\b|\badjudication\b(?=.*building)'
    }

    # APPEAL LEVEL PATTERNS (Appendix G - Part V)
    APPEAL_LEVEL_PATTERNS = {
        "general_division": r'\bgeneral\s*division\b|\bjudge\s*in\s*general\s*division\b',
        "appellate_division": r'\bappellate\s*division\b',
        "court_of_appeal": r'\bcourt\s*of\s*appeal\b|\bca\b(?=.*appeal)',
    }

    # APPEAL FROM PATTERNS
    APPEAL_FROM_PATTERNS = {
        "interlocutory": r'\binterlocutory\b|\binterim\b',
        "trial": r'\btrial\b|\bfinal\s*judgment\b'
    }

    # CONTESTED/UNCONTESTED PATTERNS
    CONTESTED_PATTERNS = {
        "contested": r'\bcontested\b|\bopposed\b|\bdisputed\b',
        "uncontested": r'\buncontested\b|\bunopposed\b|\bby\s*consent\b|\bconsent\s*order\b'
    }

    # DURATION PATTERNS (for applications in minutes)
    DURATION_MINUTES_PATTERNS = [
        r'(\d+)\s*(?:mins?|minutes?)\s*(?:hearing|duration)?',
        r'(?:hearing|duration)\s*(?:of\s*)?(\d+)\s*(?:mins?|minutes?)',
        r'(\d+)\s*(?:mins?|minutes?)\s*(?:long|application)',
        r'(?:lasted|took|hearing)\s*(\d+)\s*(?:mins?|minutes?)',
    ]

    # DURATION PATTERNS (for hearing in hours)
    DURATION_HOURS_PATTERNS = [
        r'(\d+)\s*(?:hrs?|hours?)\s*(?:hearing|duration)?',
        r'(?:hearing|duration)\s*(?:of\s*)?(\d+)\s*(?:hrs?|hours?)',
        r'(\d+)\s*(?:hrs?|hours?)\s*(?:long|hearing)',
    ]

    # Liquidated/Unliquidated patterns
    CLAIM_NATURE_PATTERNS = {
        "liquidated": r'\bliquidated\b',
        "unliquidated": r'\bunliquidated\b',
    }

    # Amount patterns (SGD, $, etc.)
    AMOUNT_PATTERNS = [
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $50,000 or $50000.00
        r'SGD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # SGD 50,000
        r'(?:SGD|S\$)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # S$ 50,000
        r'\b(\d+(?:,\d{3})*)\s*(?:dollars?|sgd)\b',  # 50,000 dollars
        r'(?:damages?|claim|amount|sum)(?:\s+of)?\s*(\d+(?:,\d{3})*)',  # damages of 300,000
        r'\b(\d{1,3}(?:,\d{3})+)\b',  # Plain numbers with commas: 300,000, 1,500, etc.
        r'\b(\d{4,})\b',  # Plain numbers >= 1000 (likely amounts)
    ]

    # Trial duration patterns
    TRIAL_DAYS_PATTERNS = [
        r'(\d+)\s*[-]?\s*days?\s*(?:contested\s*)?trial',  # 3-day trial, 3 day trial
        r'trial\s*[,.]?\s*(\d+)\s*days?',  # trial, 3 days or trial 3 days
        r'contested\s*trial\s*[,.]?\s*(\d+)\s*days?',  # contested trial, 3 days
        r'(\d+)\s*trial\s*days?',  # 3 trial days
        r'trial\s*(?:of\s*|for\s*)?(\d+)\s*days?',  # trial of 3 days / trial for 3 days
        r'(\d+)\s*days?\s*(?:of\s*)?(?:contested\s*)?trial',  # 3 days of contested trial
        r'(\d+)\s*days?\s*contested',  # 3 days contested
    ]

    # ADR refusal patterns
    ADR_REFUSAL_PATTERNS = [
        r'\brefused\s*(?:to\s*participate\s*in\s*)?(?:adr|mediation|arbitration)',
        r'\b(?:adr|mediation|arbitration)\s*(?:was\s*)?refused',
        r'\brejected\s*(?:adr|mediation|arbitration)',
        r'\b(?:adr|mediation|arbitration)\s*(?:was\s*)?rejected',
        r'\bdeclined\s*(?:adr|mediation|arbitration)',
        r'\brefused\s*(?:mediation|arbitration|adr)',
    ]

    def __init__(self):
        """Initialize pattern extractor."""
        pass

    def extract_all(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract all possible information from text.

        Args:
            text: User message text
            context: Optional context (current field values)

        Returns:
            Dictionary of extracted field values
        """
        text_lower = text.lower()
        extracted = {}

        # Extract court level
        court = self.extract_court_level(text_lower)
        if court:
            extracted["court_level"] = court

        # Extract case type
        case_type = self.extract_case_type(text_lower)
        if case_type:
            extracted["case_type"] = case_type

        # Extract claim nature (liquidated/unliquidated)
        claim_nature = self.extract_claim_nature(text_lower)
        if claim_nature:
            extracted["claim_nature"] = claim_nature

        # Extract claim amount
        amount = self.extract_amount(text)
        if amount:
            extracted["claim_amount"] = float(amount)

        # Extract trial days
        trial_days = self.extract_trial_days(text_lower)
        if trial_days:
            extracted["trial_days"] = int(trial_days)

        # Extract ADR refusal
        adr_refused = self.extract_adr_refusal(text_lower)
        if adr_refused:
            extracted["adr_refused"] = True

        # ======== NEW: Appendix G Extractions ========

        # Extract application type (Appendix G Part II)
        app_type = self.extract_application_type(text_lower)
        if app_type:
            extracted["application_type"] = app_type
            extracted["source"] = "appendix_g"

        # Extract trial category (Appendix G Part III)
        trial_category = self.extract_trial_category(text_lower)
        if trial_category:
            extracted["trial_category"] = trial_category
            extracted["source"] = "appendix_g"

        # Extract trial phase
        trial_phase = self.extract_trial_phase(text_lower)
        if trial_phase:
            extracted["trial_phase"] = trial_phase

        # Extract originating application type (Appendix G Part IV)
        orig_app_type = self.extract_originating_app_type(text_lower)
        if orig_app_type:
            extracted["originating_app_type"] = orig_app_type
            extracted["source"] = "appendix_g"

        # Extract appeal level (Appendix G Part V)
        appeal_level = self.extract_appeal_level(text_lower)
        if appeal_level:
            extracted["appeal_level"] = appeal_level
            extracted["source"] = "appendix_g"

        # Extract appeal from (what the appeal is from)
        appeal_from = self.extract_appeal_from(text_lower)
        if appeal_from:
            extracted["appeal_from"] = appeal_from

        # Extract contested status
        contested_status = self.extract_contested_status(text_lower)
        if contested_status is not None:
            extracted["contested"] = contested_status

        # Extract duration in minutes
        duration_mins = self.extract_duration_minutes(text_lower)
        if duration_mins:
            extracted["duration_minutes"] = duration_mins

        # Extract duration in hours (convert to minutes)
        duration_hours = self.extract_duration_hours(text_lower)
        if duration_hours:
            extracted["duration_minutes"] = duration_hours * 60

        return extracted

    def extract_court_level(self, text: str) -> Optional[str]:
        """
        Extract court level from text.

        Args:
            text: Lowercase text

        Returns:
            Court level or None
        """
        for court, pattern in self.COURT_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return court
        return None

    def extract_case_type(self, text: str) -> Optional[str]:
        """
        Extract case type from text.

        Args:
            text: Lowercase text

        Returns:
            Case type or None
        """
        for case_type, pattern in self.CASE_TYPE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Special handling: if text contains "default", prioritize it
                if "default" in text and case_type == "default_judgment":
                    return case_type
                # Don't match "trial" alone if "default" or "summary" is present
                if case_type == "contested_trial":
                    if "default" in text or "summary" in text:
                        continue
                return case_type
        return None

    def extract_claim_nature(self, text: str) -> Optional[str]:
        """
        Extract claim nature (liquidated/unliquidated).

        Args:
            text: Lowercase text

        Returns:
            "liquidated" or "unliquidated" or None
        """
        for nature, pattern in self.CLAIM_NATURE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return nature
        return None

    def extract_amount(self, text: str) -> Optional[Decimal]:
        """
        Extract monetary amount from text.

        Args:
            text: Text (preserve case for numbers)

        Returns:
            Decimal amount or None
        """
        for pattern in self.AMOUNT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the number, remove commas
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = Decimal(amount_str)
                    # Sanity check: legal claims are usually between 1,000 and 10,000,000
                    if 100 <= amount <= 100000000:
                        return amount
                except (ValueError, IndexError):
                    continue
        return None

    def extract_trial_days(self, text: str) -> Optional[int]:
        """
        Extract trial duration in days.

        Args:
            text: Lowercase text

        Returns:
            Number of days or None
        """
        for pattern in self.TRIAL_DAYS_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    days = int(match.group(1))
                    # Sanity check: trials are usually 1-100 days
                    if 1 <= days <= 100:
                        return days
                except (ValueError, IndexError):
                    continue
        return None

    def extract_adr_refusal(self, text: str) -> bool:
        """
        Extract ADR refusal indicator.

        Args:
            text: Lowercase text

        Returns:
            True if ADR refusal detected, False otherwise
        """
        for pattern in self.ADR_REFUSAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def extract_field(self, field_name: str, text: str) -> Optional[Any]:
        """
        Extract specific field from text.

        Args:
            field_name: Name of field to extract
            text: User message text

        Returns:
            Extracted value or None
        """
        text_lower = text.lower()

        if field_name == "court_level":
            return self.extract_court_level(text_lower)
        elif field_name == "case_type":
            return self.extract_case_type(text_lower)
        elif field_name == "claim_nature":
            return self.extract_claim_nature(text_lower)
        elif field_name == "claim_amount":
            amount = self.extract_amount(text)
            return float(amount) if amount else None
        elif field_name == "trial_days":
            return self.extract_trial_days(text_lower)
        elif field_name == "adr_refused":
            return self.extract_adr_refusal(text_lower)
        elif field_name == "application_type":
            return self.extract_application_type(text_lower)
        elif field_name == "trial_category":
            return self.extract_trial_category(text_lower)
        elif field_name == "trial_phase":
            return self.extract_trial_phase(text_lower)
        elif field_name == "originating_app_type":
            return self.extract_originating_app_type(text_lower)
        elif field_name == "appeal_level":
            return self.extract_appeal_level(text_lower)
        elif field_name == "appeal_from":
            return self.extract_appeal_from(text_lower)
        elif field_name == "contested":
            return self.extract_contested_status(text_lower)
        elif field_name == "duration_minutes":
            return self.extract_duration_minutes(text_lower)

        return None

    # ============================================================================
    # NEW EXTRACTION METHODS FOR APPENDIX G
    # ============================================================================

    def extract_application_type(self, text: str) -> Optional[str]:
        """
        Extract application type (Appendix G Part II).

        Args:
            text: Lowercase text

        Returns:
            Application type key or None
        """
        for app_type, pattern in self.APPLICATION_TYPE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return app_type
        return None

    def extract_trial_category(self, text: str) -> Optional[str]:
        """
        Extract trial category (Appendix G Part III).

        Args:
            text: Lowercase text

        Returns:
            Trial category key or None
        """
        # Check more specific patterns first
        for category in ["medical_negligence", "intellectual_property", "motor_accident", "simple_torts"]:
            pattern = self.TRIAL_CATEGORY_PATTERNS[category]
            if re.search(pattern, text, re.IGNORECASE):
                return category

        # Then check broader categories
        for category, pattern in self.TRIAL_CATEGORY_PATTERNS.items():
            if category not in ["medical_negligence", "intellectual_property", "motor_accident", "simple_torts"]:
                if re.search(pattern, text, re.IGNORECASE):
                    return category

        return None

    def extract_trial_phase(self, text: str) -> Optional[str]:
        """
        Extract trial phase.

        Args:
            text: Lowercase text

        Returns:
            Trial phase key or None
        """
        for phase, pattern in self.TRIAL_PHASE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return phase
        return None

    def extract_originating_app_type(self, text: str) -> Optional[str]:
        """
        Extract originating application type (Appendix G Part IV).

        Args:
            text: Lowercase text

        Returns:
            Originating application type key or None
        """
        for app_type, pattern in self.ORIGINATING_APP_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return app_type
        return None

    def extract_appeal_level(self, text: str) -> Optional[str]:
        """
        Extract appeal level (Appendix G Part V).

        Args:
            text: Lowercase text

        Returns:
            Appeal level key or None
        """
        # Check in priority order (most specific first)
        for level in ["court_of_appeal", "appellate_division", "general_division"]:
            pattern = self.APPEAL_LEVEL_PATTERNS[level]
            if re.search(pattern, text, re.IGNORECASE):
                return level
        return None

    def extract_appeal_from(self, text: str) -> Optional[str]:
        """
        Extract what the appeal is from (interlocutory vs trial).

        Args:
            text: Lowercase text

        Returns:
            "interlocutory" or "trial" or None
        """
        for appeal_from, pattern in self.APPEAL_FROM_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return appeal_from
        return None

    def extract_contested_status(self, text: str) -> Optional[bool]:
        """
        Extract whether application/matter is contested.

        Args:
            text: Lowercase text

        Returns:
            True if contested, False if uncontested, None if unclear
        """
        # Check uncontested first (more specific)
        if re.search(self.CONTESTED_PATTERNS["uncontested"], text, re.IGNORECASE):
            return False

        # Then check contested
        if re.search(self.CONTESTED_PATTERNS["contested"], text, re.IGNORECASE):
            return True

        return None

    def extract_duration_minutes(self, text: str) -> Optional[int]:
        """
        Extract duration in minutes.

        Args:
            text: Lowercase text

        Returns:
            Duration in minutes or None
        """
        for pattern in self.DURATION_MINUTES_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    minutes = int(match.group(1))
                    # Sanity check: hearings are usually 5-480 minutes (8 hours)
                    if 5 <= minutes <= 480:
                        return minutes
                except (ValueError, IndexError):
                    continue
        return None

    def extract_duration_hours(self, text: str) -> Optional[int]:
        """
        Extract duration in hours.

        Args:
            text: Lowercase text

        Returns:
            Duration in hours or None
        """
        for pattern in self.DURATION_HOURS_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    hours = int(match.group(1))
                    # Sanity check: hearings are usually 1-12 hours
                    if 1 <= hours <= 12:
                        return hours
                except (ValueError, IndexError):
                    continue
        return None
