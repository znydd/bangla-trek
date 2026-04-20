import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.group_trip import GroupTripMember
from app.models.trip_budget import GroupTripBudget, GroupTripExpense
from app.models.user import User
from app.schemas.trip_budget import (
    BudgetCategoryTotal,
    BudgetSummary,
    GroupTripBudgetRead,
    GroupTripBudgetUpsert,
    GroupTripExpenseCreate,
    GroupTripExpenseRead,
    GroupTripExpenseUpdate,
)


class TripBudgetService:
    def __init__(self, db: Session):
        self.db = db

    def _require_member(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> None:
        is_member = (
            self.db.execute(
                select(GroupTripMember).where(
                    (GroupTripMember.trip_id == trip_id)
                    & (GroupTripMember.user_id == user_id)
                )
            )
            .scalar_one_or_none()
            is not None
        )
        if not is_member:
            raise PermissionError("You must be a member of this trip")

    def get_budget(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> Optional[GroupTripBudgetRead]:
        self._require_member(trip_id, user_id)
        budget = (
            self.db.execute(select(GroupTripBudget).where(GroupTripBudget.trip_id == trip_id))
            .scalar_one_or_none()
        )
        return GroupTripBudgetRead.model_validate(budget) if budget else None

    def upsert_budget(
        self, trip_id: uuid.UUID, user_id: uuid.UUID, payload: GroupTripBudgetUpsert
    ) -> GroupTripBudgetRead:
        self._require_member(trip_id, user_id)
        existing = (
            self.db.execute(select(GroupTripBudget).where(GroupTripBudget.trip_id == trip_id))
            .scalar_one_or_none()
        )
        if existing:
            existing.total_budget = payload.total_budget
            existing.currency = payload.currency
            # reset alerts when budget changes materially
            existing.alert_80_sent = False
            existing.alert_100_sent = False
            self.db.commit()
            self.db.refresh(existing)
            return GroupTripBudgetRead.model_validate(existing)

        budget = GroupTripBudget(
            trip_id=trip_id,
            created_by_user_id=user_id,
            total_budget=payload.total_budget,
            currency=payload.currency,
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return GroupTripBudgetRead.model_validate(budget)

    def list_expenses(self, trip_id: uuid.UUID, user_id: uuid.UUID, limit: int = 200) -> list[GroupTripExpenseRead]:
        self._require_member(trip_id, user_id)
        rows = (
            self.db.execute(
                select(GroupTripExpense, User.name, User.picture_url)
                .join(User, User.id == GroupTripExpense.user_id)
                .where(GroupTripExpense.trip_id == trip_id)
                .order_by(GroupTripExpense.spent_at.desc())
                .limit(limit)
            )
            .all()
        )
        results: list[GroupTripExpenseRead] = []
        for exp, name, picture_url in rows:
            item = GroupTripExpenseRead.model_validate(exp)
            item.user_name = name
            item.user_picture_url = picture_url
            results.append(item)
        return results

    def create_expense(
        self, trip_id: uuid.UUID, user_id: uuid.UUID, payload: GroupTripExpenseCreate
    ) -> GroupTripExpenseRead:
        self._require_member(trip_id, user_id)
        exp = GroupTripExpense(
            trip_id=trip_id,
            user_id=user_id,
            amount=payload.amount,
            currency=payload.currency,
            category=payload.category,
            note=payload.note,
            spent_at=payload.spent_at or datetime.utcnow(),
        )
        self.db.add(exp)
        self.db.commit()
        self.db.refresh(exp)
        return GroupTripExpenseRead.model_validate(exp)

    def update_expense(
        self, trip_id: uuid.UUID, expense_id: uuid.UUID, user_id: uuid.UUID, payload: GroupTripExpenseUpdate
    ) -> GroupTripExpenseRead:
        self._require_member(trip_id, user_id)
        exp = (
            self.db.execute(
                select(GroupTripExpense).where(
                    (GroupTripExpense.id == expense_id) & (GroupTripExpense.trip_id == trip_id)
                )
            )
            .scalar_one_or_none()
        )
        if not exp:
            raise ValueError("Expense not found")

        # allow editing by trip members; restrict delete to creator later if needed
        updates = payload.model_dump(exclude_unset=True)
        for k, v in updates.items():
            if v is not None:
                setattr(exp, k, v)
        self.db.commit()
        self.db.refresh(exp)
        return GroupTripExpenseRead.model_validate(exp)

    def delete_expense(self, trip_id: uuid.UUID, expense_id: uuid.UUID, user_id: uuid.UUID) -> None:
        self._require_member(trip_id, user_id)
        exp = (
            self.db.execute(
                select(GroupTripExpense).where(
                    (GroupTripExpense.id == expense_id) & (GroupTripExpense.trip_id == trip_id)
                )
            )
            .scalar_one_or_none()
        )
        if not exp:
            raise ValueError("Expense not found")
        self.db.delete(exp)
        self.db.commit()

    def get_summary(self, trip_id: uuid.UUID, user_id: uuid.UUID) -> BudgetSummary:
        self._require_member(trip_id, user_id)
        budget = (
            self.db.execute(select(GroupTripBudget).where(GroupTripBudget.trip_id == trip_id))
            .scalar_one_or_none()
        )
        if not budget:
            raise ValueError("Budget not set")

        spent_total = (
            self.db.execute(
                select(func.coalesce(func.sum(GroupTripExpense.amount), 0.0)).where(
                    GroupTripExpense.trip_id == trip_id
                )
            ).scalar()
            or 0.0
        )

        per_cat = self.db.execute(
            select(
                GroupTripExpense.category,
                func.coalesce(func.sum(GroupTripExpense.amount), 0.0),
            )
            .where(GroupTripExpense.trip_id == trip_id)
            .group_by(GroupTripExpense.category)
            .order_by(func.sum(GroupTripExpense.amount).desc())
        ).all()

        remaining = max(0.0, float(budget.total_budget) - float(spent_total))
        percent_used = float(spent_total) / float(budget.total_budget) if budget.total_budget else 0.0

        crossed_80 = percent_used >= 0.8 and not budget.alert_80_sent
        crossed_100 = percent_used >= 1.0 and not budget.alert_100_sent

        # persist alert flags to avoid repeated alerts
        if crossed_80:
            budget.alert_80_sent = True
        if crossed_100:
            budget.alert_100_sent = True
        if crossed_80 or crossed_100:
            self.db.commit()

        return BudgetSummary(
            trip_id=trip_id,
            currency=budget.currency,
            budget_total=budget.total_budget,
            spent_total=float(spent_total),
            remaining=remaining,
            percent_used=round(percent_used, 4),
            totals_by_category=[
                BudgetCategoryTotal(category=cat, total=float(total)) for cat, total in per_cat
            ],
            crossed_80=crossed_80,
            crossed_100=crossed_100,
        )

