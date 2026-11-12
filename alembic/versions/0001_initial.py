"""Initial SupplierTrust schema"""
from alembic import op
import sqlalchemy as sa
revision='0001_initial'
down_revision=None
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('suppliers',sa.Column('id',sa.Integer,primary_key=True),sa.Column('name',sa.String(160),nullable=False),sa.Column('country',sa.String(80),nullable=False),sa.Column('category',sa.String(80),nullable=False),sa.Column('identifier',sa.String(40),nullable=False,server_default=''),sa.Column('contact',sa.String(160),nullable=False,server_default=''),sa.Column('website',sa.String(300),nullable=False,server_default=''),sa.Column('created_at',sa.String(10),nullable=False))
    op.create_index('ix_suppliers_name','suppliers',['name'])
    op.create_table('evidence',sa.Column('id',sa.Integer,primary_key=True),sa.Column('supplier_id',sa.Integer,sa.ForeignKey('suppliers.id',ondelete='CASCADE'),nullable=False),sa.Column('source_url',sa.String(500),nullable=False),sa.Column('reviewer',sa.String(120),nullable=False),sa.Column('verified_on',sa.String(10),nullable=False),sa.Column('status',sa.String(20),nullable=False),sa.Column('notes',sa.Text,nullable=False))
    op.create_table('screenings',sa.Column('id',sa.Integer,primary_key=True),sa.Column('supplier_id',sa.Integer,sa.ForeignKey('suppliers.id',ondelete='CASCADE'),nullable=False),sa.Column('checked_at',sa.String(40),nullable=False),sa.Column('candidate',sa.String(300),nullable=False),sa.Column('similarity',sa.Float,nullable=False),sa.Column('decision',sa.String(20),nullable=False,server_default='pending'),sa.Column('reviewer',sa.String(120),nullable=False,server_default=''),sa.Column('note',sa.Text,nullable=False,server_default=''),sa.Column('source',sa.String(30),nullable=False,server_default='synthetic'),sa.Column('source_ref',sa.String(120),nullable=False,server_default=''))
    op.create_table('documents',sa.Column('id',sa.Integer,primary_key=True),sa.Column('supplier_id',sa.Integer,sa.ForeignKey('suppliers.id',ondelete='CASCADE'),nullable=False),sa.Column('filename',sa.String(200),nullable=False),sa.Column('stored_name',sa.String(80),nullable=False),sa.Column('uploaded_at',sa.String(40),nullable=False),sa.Column('extracted_name',sa.String(160),nullable=False,server_default=''),sa.Column('extracted_identifier',sa.String(40),nullable=False,server_default=''),sa.Column('extraction_status',sa.String(40),nullable=False),sa.Column('discrepancies',sa.Text,nullable=False,server_default='[]'))
    op.create_table('ofac_snapshot',sa.Column('id',sa.Integer,primary_key=True),sa.Column('retrieved_at',sa.String(40),nullable=False),sa.Column('sha256',sa.String(64),nullable=False),sa.Column('records',sa.Text,nullable=False),sa.CheckConstraint('id=1'))
def downgrade():
    op.drop_table('ofac_snapshot'); op.drop_table('documents'); op.drop_table('screenings'); op.drop_table('evidence'); op.drop_index('ix_suppliers_name'); op.drop_table('suppliers')
