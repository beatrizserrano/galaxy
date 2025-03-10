"""add workflow.source_metadata column

Revision ID: b182f655505f
Revises: e7b6dcb09efd
Create Date: 2022-03-14 12:56:57.067748

"""
from alembic import op
from sqlalchemy import Column

from galaxy.model.custom_types import JSONType
from galaxy.model.migrations.util import (
    drop_column,
    ignore_add_column_error,
)

# revision identifiers, used by Alembic.
revision = "b182f655505f"
down_revision = "e7b6dcb09efd"
branch_labels = None
depends_on = None


def upgrade():
    table, column = "workflow", "source_metadata"
    with ignore_add_column_error(table, column):
        op.add_column(table, Column(column, JSONType))


def downgrade():
    drop_column("workflow", "source_metadata")
