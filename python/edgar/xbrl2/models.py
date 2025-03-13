"""
Data models for XBRL parsing.

This module defines the core data structures used throughout the XBRL parser.
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field

# Constants for label roles
STANDARD_LABEL = "http://www.xbrl.org/2003/role/label"
TERSE_LABEL = "http://www.xbrl.org/2003/role/terseLabel"
PERIOD_START_LABEL = "http://www.xbrl.org/2003/role/periodStartLabel"
PERIOD_END_LABEL = "http://www.xbrl.org/2003/role/periodEndLabel"
TOTAL_LABEL = "http://www.xbrl.org/2003/role/totalLabel"


class ElementCatalog(BaseModel):
    """
    A catalog of XBRL elements with their properties.
    
    This is the base data structure for element metadata as described in the design document.
    """
    name: str
    data_type: str
    period_type: str  # "instant" or "duration"
    balance: Optional[str] = None  # "debit", "credit", or None
    abstract: bool = False
    labels: Dict[str, str] = Field(default_factory=dict)
    
    def __str__(self) -> str:
        return self.name


class Context(BaseModel):
    """
    An XBRL context defining entity, period, and dimensional information.
    
    This corresponds to the Context Registry in the design document.
    """
    context_id: str
    entity: Dict[str, Any] = Field(default_factory=dict)
    period: Dict[str, Any] = Field(default_factory=dict)
    dimensions: Dict[str, str] = Field(default_factory=dict)
    
    @property
    def period_string(self) -> str:
        """Return a human-readable string representation of the period."""
        if self.period.get('type') == 'instant':
            return f"As of {self.period.get('instant')}"
        elif self.period.get('type') == 'duration':
            return f"From {self.period.get('startDate')} to {self.period.get('endDate')}"
        else:
            return "Forever"


class Fact(BaseModel):
    """
    An XBRL fact with value and references to context, unit, and element.
    
    This corresponds to the Fact Database in the design document.
    """
    element_id: str
    context_ref: str
    value: str
    unit_ref: Optional[str] = None
    decimals: Optional[Union[int, str]] = None  # int or "INF"
    numeric_value: Optional[float] = None
    footnotes: List[str] = Field(default_factory=list)


class PresentationNode(BaseModel):
    """
    A node in the presentation hierarchy.
    
    This corresponds to the Presentation Node in the design document.
    """
    element_id: str
    parent: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    order: float = 0.0
    preferred_label: Optional[str] = None
    depth: int = 0
    
    # Additional information linked from element catalog
    element_name: Optional[str] = None
    standard_label: Optional[str] = None
    is_abstract: bool = False
    labels: Dict[str, str] = Field(default_factory=dict)
    
    @property
    def display_label(self) -> str:
        """
        Return the appropriate label for display, prioritizing user-friendly options.
        
        Label selection priority:
        1. Preferred label (if specified in presentation linkbase)
        2. Terse label (for more concise display)
        3. Label (standard label)
        4. Element ID (fallback)
        """
        # 1. Use preferred label if specified and available
        if self.preferred_label and self.preferred_label in self.labels:
            return self.labels[self.preferred_label]
        
        # 2. Use terse label if available (more user-friendly)
        if TERSE_LABEL in self.labels:
            return self.labels[TERSE_LABEL]
        
        # 3. Fall back to standard label
        if self.standard_label:
            return self.standard_label
        
        # 4. Last resort: element ID
        return self.element_id


class PresentationTree(BaseModel):
    """
    A presentation tree for a specific role.
    
    This corresponds to the Presentation Hierarchy in the design document.
    """
    role_uri: str
    definition: str
    root_element_id: str
    all_nodes: Dict[str, PresentationNode] = Field(default_factory=dict)
    order: int = 0


class CalculationNode(BaseModel):
    """
    A node in the calculation hierarchy.
    
    This corresponds to the Calculation Node in the design document.
    """
    element_id: str
    children: List[str] = Field(default_factory=list)
    parent: Optional[str] = None
    weight: float = 1.0
    order: float = 0.0
    
    # Information linked from schema
    balance_type: Optional[str] = None  # "debit", "credit", or None
    period_type: Optional[str] = None  # "instant" or "duration"


class CalculationTree(BaseModel):
    """
    A calculation tree for a specific role.
    
    This corresponds to the Calculation Network in the design document.
    """
    role_uri: str
    definition: str
    root_element_id: str
    all_nodes: Dict[str, CalculationNode] = Field(default_factory=dict)


class Axis(BaseModel):
    """
    A dimensional axis (dimension) in XBRL.
    
    This corresponds to the Axis (Dimension) in the design document.
    """
    element_id: str
    label: str
    domain_id: Optional[str] = None
    default_member_id: Optional[str] = None
    is_typed_dimension: bool = False
    typed_domain_ref: str = ""


class Domain(BaseModel):
    """
    A domain in an XBRL dimensional structure.
    
    This corresponds to the Domain in the design document.
    """
    element_id: str
    label: str
    members: List[str] = Field(default_factory=list)  # List of domain member element IDs
    parent: Optional[str] = None  # Parent domain element ID


class Table(BaseModel):
    """
    A dimensional table (hypercube) in XBRL.
    
    This corresponds to the Table (Hypercube) in the design document.
    """
    element_id: str
    label: str
    role_uri: str
    axes: List[str] = Field(default_factory=list)  # List of axis element IDs
    line_items: List[str] = Field(default_factory=list)  # List of line item element IDs
    closed: bool = False
    context_element: str = "segment"


class XBRLProcessingError(Exception):
    """Exception raised for errors during XBRL processing."""
    pass