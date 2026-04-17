import uuid
from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


ExpenseCategory = Literal[
    "accommodation",
    "food",
    "transport",
    "attractions",
    "shopping",
    "other",
]


class GroupTripBudgetUpsert(BaseModel):
    total_budget: float = Field(..., gt=0)
    currency: str = Field("BDT", min_length=1, max_length=8)


class GroupTripBudgetRead(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    created_by_user_id: uuid.UUID
    total_budget: float
    currency: str
    alert_80_sent: bool
    alert_100_sent: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GroupTripExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field("BDT", min_length=1, max_length=8)
    category: ExpenseCategory
    note: Optional[str] = Field(default=None, max_length=500)
    spent_at: Optional[datetime] = None


class GroupTripExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = Field(default=None, min_length=1, max_length=8)
    category: Optional[ExpenseCategory] = None
    note: Optional[str] = Field(default=None, max_length=500)
    spent_at: Optional[datetime] = None


class GroupTripExpenseRead(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    user_id: uuid.UUID
    amount: float
    currency: str
    category: str
    note: Optional[str] = None
    spent_at: datetime
    created_at: datetime
    updated_at: datetime

    user_name: Optional[str] = None
    user_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BudgetCategoryTotal(BaseModel):
    category: str
    total: float


class BudgetSummary(BaseModel):
    trip_id: uuid.UUID
    currency: str
    budget_total: float
    spent_total: float
    remaining: float
    percent_used: float = Field(..., ge=0.0)
    totals_by_category: List[BudgetCategoryTotal] = []

    crossed_80: bool = False
    crossed_100: bool = False

    model_config = ConfigDict(from_attributes=True)

