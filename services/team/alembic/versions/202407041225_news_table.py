"""add news table

Revision ID: 202407041225
Revises: 3245c3370f2f
Create Date: 2024-07-04 12:25:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "202407041225"
down_revision = "3245c3370f2f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("news")
