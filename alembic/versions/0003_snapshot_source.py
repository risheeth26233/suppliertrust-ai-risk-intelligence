"""Record the provenance of each screening snapshot"""
from alembic import op
import sqlalchemy as sa

revision='0003_snapshot_source'
down_revision='0002_performance_audit'
branch_labels=None
depends_on=None

def upgrade():
    op.add_column('ofac_snapshot',sa.Column('source',sa.String(40),nullable=False,server_default='OFAC SDN'))

def downgrade():
    op.drop_column('ofac_snapshot','source')
