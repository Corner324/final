"""add owner_id and is_team_event to calendar_events

Revision ID: 202407041240
Revises: e30f2e560cb5
Create Date: 2024-07-04 12:40:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "202407041240"
down_revision = "e30f2e560cb5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("calendar_events") as batch_op:
        batch_op.add_column(
            sa.Column("owner_id", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("is_team_event", sa.Integer(), nullable=False, server_default="0")
        )
    op.execute("ALTER TABLE calendar_events ALTER COLUMN owner_id DROP DEFAULT")
    op.execute("ALTER TABLE calendar_events ALTER COLUMN is_team_event DROP DEFAULT")


def downgrade() -> None:
    with op.batch_alter_table("calendar_events") as batch_op:
        batch_op.drop_column("is_team_event")
        batch_op.drop_column("owner_id")
