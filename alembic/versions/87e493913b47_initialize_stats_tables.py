"""initialize stats tables

Revision ID: 87e493913b47
Revises: 520fdc02788e
Create Date: 2024-11-24 11:02:22.065894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = '87e493913b47'
down_revision: Union[str, None] = '520fdc02788e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stats",
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("selfies", sa.Integer(), nullable=False),
        sa.Column("burst", sa.Integer(), nullable=False),
        sa.Column("panorama", sa.Integer(), nullable=False),
        sa.Column("favorite", sa.Integer(), nullable=False),
        sa.Column("slow_mo", sa.Integer(), nullable=False),
        sa.Column("time_lapse", sa.Integer(), nullable=False),
        sa.Column("photo", sa.Integer(), nullable=False),
        sa.Column("movie", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("year"),
    )
    op.create_table(
        "camera",
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("camera", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("year"),
    )
    op.create_table(
        "camera_model",
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("model", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("year"),
    )
    op.create_table(
        "location",
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("location", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("year"),
    )
    op.create_table(
        "month",
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("year"),
    )
    op.create_table(
        "person",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile", sa.BLOB(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "person_stats",
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("year", "person_id"),
    )
    op.create_table(
        "highlight",
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("photo", sa.BLOB(), nullable=False),
        sa.PrimaryKeyConstraint("year"),
    )


def downgrade() -> None:
    op.drop_table("stats")
    op.drop_table("camera")
    op.drop_table("camera_model")
    op.drop_table("location")
    op.drop_table("month")
    op.drop_table("person")
    op.drop_table("person_stats")
    op.drop_table("highlight")
