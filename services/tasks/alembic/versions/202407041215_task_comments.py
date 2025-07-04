"""add task_comments table

Revision ID: 202407041215
Revises: 2c8bc081497c
Create Date: 2024-07-04 12:15:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "202407041215"
down_revision = "2c8bc081497c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "task_comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("task_comments")
