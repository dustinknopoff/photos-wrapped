"""Added queue table

Revision ID: 520fdc02788e
Revises: 
Create Date: 2024-11-24 10:31:26.320805

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '520fdc02788e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "queue", 
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payload", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("response", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("status", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("queue")
