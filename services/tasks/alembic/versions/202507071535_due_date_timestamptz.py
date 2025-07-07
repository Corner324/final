"""make due_date timestamptz

Revision ID: 202507071535
Revises: 202407041215
Create Date: 2025-07-07 15:35:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "202507071535"
down_revision = "202407041215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # В Postgres нельзя напрямую сменить тип без USING, поэтому выполняем SQL
    op.execute(
        "ALTER TABLE tasks ALTER COLUMN due_date TYPE TIMESTAMP WITH TIME ZONE USING due_date AT TIME ZONE 'UTC'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE tasks ALTER COLUMN due_date TYPE TIMESTAMP WITHOUT TIME ZONE"
    )
