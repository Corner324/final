"""add ratings table

Revision ID: 202507071540
Revises: 083f32fd8826
Create Date: 2025-07-07 16:40:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "202507071540"
down_revision = "083f32fd8826"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "ratings" in inspector.get_table_names():
        # таблица уже есть (контейнер мог упасть после частичного применения)
        return

    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False, index=True),
        sa.Column("timeliness_score", sa.Integer(), nullable=False),
        sa.Column("completeness_score", sa.Integer(), nullable=False),
        sa.Column("quality_score", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("ratings")
