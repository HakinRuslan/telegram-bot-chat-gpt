"""пару изменений

Revision ID: 853d25e4e96f
Revises: 7dd81e8e607f
Create Date: 2025-04-01 17:50:25.741194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '853d25e4e96f'
down_revision: Union[str, None] = '7dd81e8e607f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'number',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'number',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
