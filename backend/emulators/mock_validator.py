"""
Mock Validator for Testing
Implements IValidator interface with predictable validation logic
"""
from typing import Dict, Any, List, Tuple
from backend.interfaces.validation import IValidator, ValidationError


class MockValidator(IValidator):
    """
    Mock implementation of IValidator for testing.
    Provides predictable validation results.
    """
    
    def __init__(self):
        self._validation_count = 0
        self._protected_fields = [
            "total_costs",
            "breakdown",
            "calculation_method",
            "applicable_rules"
        ]
    
    # ============================================
    # VALIDATION
    # ============================================
    
    async def validate(
        self,
        original: Dict[str, Any],
        enhanced: Dict[str, Any]
    ) -> Tuple[bool, List[ValidationError]]:
        """
        Validate enhanced result against original.
        
        Checks:
        1. Protected fields not modified
        2. Citations not hallucinated
        3. Legal terminology preserved
        """
        self._validation_count += 1
        errors = []
        
        # Validate protected fields
        protected_errors = self.validate_protected_fields(original, enhanced)
        errors.extend(protected_errors)
        
        # Validate citations
        citation_errors = self.validate_citations(enhanced)
        errors.extend(citation_errors)
        
        # Validate legal terminology
        terminology_errors = self.validate_legal_terminology(enhanced)
        errors.extend(terminology_errors)
        
        is_valid = len(errors) == 0
        return (is_valid, errors)
    
    def validate_protected_fields(
        self,
        original: Dict[str, Any],
        enhanced: Dict[str, Any]
    ) -> List[ValidationError]:
        """
        Check that protected fields weren't modified.
        """
        errors = []
        
        for field in self._protected_fields:
            if field in original:
                original_value = original[field]
                enhanced_value = enhanced.get(field)
                
                if original_value != enhanced_value:
                    errors.append(ValidationError(
                        field=field,
                        error_type="protected_field_modified",
                        message=f"Protected field '{field}' was modified",
                        severity="critical",
                        original_value=str(original_value),
                        enhanced_value=str(enhanced_value)
                    ))
        
        return errors
    
    def validate_citations(
        self,
        enhanced: Dict[str, Any]
    ) -> List[ValidationError]:
        """
        Verify citations weren't hallucinated.
        
        Mock implementation checks for suspicious patterns.
        """
        errors = []
        
        # Check if there are any citations
        citations = enhanced.get("citations", [])
        
        # Mock check: flag any citation with "hallucinated" in it
        for citation in citations:
            if isinstance(citation, str) and "hallucinated" in citation.lower():
                errors.append(ValidationError(
                    field="citations",
                    error_type="hallucinated_citation",
                    message=f"Suspicious citation detected: {citation}",
                    severity="high",
                    original_value="",
                    enhanced_value=citation
                ))
        
        return errors
    
    def validate_legal_terminology(
        self,
        enhanced: Dict[str, Any]
    ) -> List[ValidationError]:
        """
        Check legal terminology wasn't changed incorrectly.
        
        Mock implementation checks for known problematic terms.
        """
        errors = []
        
        # Get all text content
        content = str(enhanced)
        
        # Mock check: flag certain problematic terms
        problematic_terms = {
            "guarranteed": "guaranteed",
            "definitly": "definitely",
            "aproximate": "approximate"
        }
        
        for wrong, correct in problematic_terms.items():
            if wrong in content.lower():
                errors.append(ValidationError(
                    field="content",
                    error_type="terminology_error",
                    message=f"Incorrect spelling: '{wrong}' should be '{correct}'",
                    severity="medium",
                    original_value=wrong,
                    enhanced_value=correct
                ))
        
        return errors
    
    # ============================================
    # HEALTH CHECK
    # ============================================
    
    async def health_check(self) -> bool:
        """
        Check if validator is functioning.
        """
        try:
            # Test with minimal data
            test_original = {"field": "value"}
            test_enhanced = {"field": "value"}
            is_valid, errors = await self.validate(test_original, test_enhanced)
            return is_valid and isinstance(errors, list)
        except Exception:
            return False
    
    # ============================================
    # UTILITY
    # ============================================
    
    def get_validation_count(self) -> int:
        """Get number of validate() calls made"""
        return self._validation_count
    
    def reset_validation_count(self) -> None:
        """Reset validation counter"""
        self._validation_count = 0
    
    def add_protected_field(self, field: str) -> None:
        """Add a field to the protected list"""
        if field not in self._protected_fields:
            self._protected_fields.append(field)
    
    def get_protected_fields(self) -> List[str]:
        """Get list of protected fields"""
        return self._protected_fields.copy()
