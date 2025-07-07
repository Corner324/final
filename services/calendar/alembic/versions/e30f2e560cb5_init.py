"""init

Revision ID: e30f2e560cb5
Revises:
Create Date: 2025-06-30 14:28:52.681316

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e30f2e560cb5"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # создаём основную таблицу календаря
    op.create_table(
        "calendar_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("is_team_event", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
    )

    # пример пользовательской таблицы (если нужна). Удалите, если не требуется
    # op.create_table(
    #     'users',
    #     sa.Column('id', sa.Integer(), primary_key=True),
    #     sa.Column('email', sa.String(), nullable=False, unique=True),
    # )


def downgrade() -> None:
    op.drop_table("calendar_events")
