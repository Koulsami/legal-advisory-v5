"""
IValidator Interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .data_structures import ValidationError


class IValidator(ABC):
    """Validator for AI outputs and user inputs"""
    
    @abstractmethod
    async def validate(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> tuple[bool, List[ValidationError]]:
        """
        Validate data against schema.
        
        Returns:
            (is_valid, errors)
        """
        pass
