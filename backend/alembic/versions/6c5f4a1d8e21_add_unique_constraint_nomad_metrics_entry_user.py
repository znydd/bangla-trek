"""add unique constraint on nomad_metrics entry_id + user_id

Revision ID: 6c5f4a1d8e21
Revises: 0f2d2d6a3c27
Create Date: 2026-03-28 10:30:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6c5f4a1d8e21"
down_revision: Union[str, Sequence[str], None] = "0f2d2d6a3c27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Keep the newest record per (entry_id, user_id), remove older duplicates.
    op.execute(
        """
        DELETE FROM nomad_metrics nm
        USING (
            SELECT id
            FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY entry_id, user_id
                        ORDER BY submitted_at DESC, id DESC
                    ) AS rn
                FROM nomad_metrics
            ) ranked
            WHERE ranked.rn > 1
        ) duplicates
        WHERE nm.id = duplicates.id
        """
    )

    op.create_unique_constraint(
        "uq_nomad_metrics_entry_user",
        "nomad_metrics",
        ["entry_id", "user_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_nomad_metrics_entry_user", "nomad_metrics", type_="unique")
