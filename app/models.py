from dataclasses import dataclass
from datetime import datetime
from typing import Optional

STATUSES = ("Planned", "In Progress", "Done", "Paused")
PRIORITIES = ("Low", "Medium", "High", "Critical")
ITEM_TYPES = ("Document", "Asset", "Supply", "Warranty", "Other")

@dataclass
class Task:
    id: Optional[int]=None
    title: str=""
    category: str="General"
    priority: str="Medium"
    due_date: str=""
    recurrence: str="None"
    status: str="Planned"
    notes: str=""
    created_at: str=""
    updated_at: str=""

@dataclass
class Document:
    id: Optional[int]=None
    name: str=""
    category: str="Identity"
    expiry_date: str=""
    location: str=""
    notes: str=""
    created_at: str=""

@dataclass
class Contact:
    id: Optional[int]=None
    name: str=""
    relationship: str=""
    phone: str=""
    email: str=""
    notes: str=""

@dataclass
class InventoryItem:
    id: Optional[int]=None
    name: str=""
    item_type: str="Other"
    category: str="General"
    quantity: float=1
    unit: str="unit"
    expiry_date: str=""
    replacement_cost: float=0
    location: str=""
    notes: str=""

@dataclass
class Financial:
    id: Optional[int]=None
    name: str=""
    amount: float=0
    frequency: str="Monthly"
    essential: bool=True
    due_day: int=1
    notes: str=""

@dataclass
class EmergencyPlan:
    id: Optional[int]=None
    name: str=""
    scenario: str="General"
    instructions: str=""
    meeting_point: str=""
    last_reviewed: str=""
    notes: str=""
