"""Add supplier performance observations and review audit events"""
from alembic import op
import sqlalchemy as sa
revision='0002_performance_audit'
down_revision='0001_initial'
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('performance',sa.Column('id',sa.Integer,primary_key=True),sa.Column('supplier_id',sa.Integer,sa.ForeignKey('suppliers.id',ondelete='CASCADE'),nullable=False),sa.Column('observed_on',sa.String(10),nullable=False),sa.Column('on_time_rate',sa.Float,nullable=False),sa.Column('defect_rate',sa.Float,nullable=False),sa.Column('source_url',sa.String(500),nullable=False),sa.Column('reviewer',sa.String(120),nullable=False),sa.Column('notes',sa.String(1000),nullable=False))
    op.create_table('audit_events',sa.Column('id',sa.Integer,primary_key=True),sa.Column('supplier_id',sa.Integer,sa.ForeignKey('suppliers.id',ondelete='SET NULL')),sa.Column('occurred_at',sa.String(40),nullable=False),sa.Column('actor',sa.String(120),nullable=False),sa.Column('action',sa.String(80),nullable=False),sa.Column('detail',sa.String(1000),nullable=False))
def downgrade():
    op.drop_table('audit_events'); op.drop_table('performance')
