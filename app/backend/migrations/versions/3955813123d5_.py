"""empty message

Revision ID: 3955813123d5
Revises: 21d31c89a5d7
Create Date: 2026-08-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3955813123d5'
down_revision = '21d31c89a5d7'
branch_labels = None
depends_on = None

invitation_status_enum = sa.Enum('send', 'accepted', 'rejected', name='invitationstatus')


def upgrade() -> None:
    invitation_status_enum.create(op.get_bind())
    op.add_column('invitations', sa.Column('status', invitation_status_enum, server_default='send', nullable=False))


def downgrade() -> None:
    op.drop_column('invitations', 'status')
    invitation_status_enum.drop(op.get_bind())