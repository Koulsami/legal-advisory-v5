"""
ITreeFramework Interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .data_structures import LogicTreeNode


class ITreeFramework(ABC):
    """Tree framework for managing logic trees"""
    
    @abstractmethod
    def build_tree(
        self,
        rules: List[Dict[str, Any]]
    ) -> List[LogicTreeNode]:
        """Build tree from rules"""
        pass
    
    @abstractmethod
    def query_tree(
        self,
        tree: List[LogicTreeNode],
        query: Dict[str, Any]
    ) -> List[LogicTreeNode]:
        """Query tree with filters"""
        pass
