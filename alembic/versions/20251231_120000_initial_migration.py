"""Initial migration - Create RFQ tables

Revision ID: 001_initial
Revises:
Create Date: 2025-12-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create rfq_documents table
    op.create_table(
        'rfq_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rfq_number', sa.String(length=100), nullable=True),
        sa.Column('rfq_title', sa.String(length=500), nullable=True),
        sa.Column('project_name', sa.String(length=200), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('buyer_name', sa.String(length=200), nullable=True),
        sa.Column('buyer_organization', sa.String(length=200), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rfq_number', name='uq_rfq_number')
    )
    op.create_index('ix_rfq_documents_rfq_number', 'rfq_documents', ['rfq_number'])
    op.create_index('ix_rfq_documents_status', 'rfq_documents', ['status'])

    # Create parse_results table
    op.create_table(
        'parse_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_file', sa.String(length=512), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('rfq_document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['rfq_document_id'], ['rfq_documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_parse_results_source_file', 'parse_results', ['source_file'])
    op.create_index('ix_parse_results_created_at', 'parse_results', ['created_at'])

    # Create vendor_quotes table
    op.create_table(
        'vendor_quotes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rfq_document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_name', sa.String(length=200), nullable=False),
        sa.Column('vendor_code', sa.String(length=50), nullable=True),
        sa.Column('contact_person', sa.String(length=200), nullable=True),
        sa.Column('contact_email', sa.String(length=254), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),
        sa.Column('quote_reference', sa.String(length=100), nullable=True),
        sa.Column('quote_date', sa.Date(), nullable=True),
        sa.Column('validity_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='received'),
        sa.Column('payment_terms', sa.String(length=200), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('country_of_origin', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['rfq_document_id'], ['rfq_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vendor_quotes_vendor_name', 'vendor_quotes', ['vendor_name'])
    op.create_index('ix_vendor_quotes_status', 'vendor_quotes', ['status'])

    # Create equipment_items table
    op.create_table(
        'equipment_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_quote_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('model_number', sa.String(length=100), nullable=True),
        sa.Column('manufacturer', sa.String(length=200), nullable=True),
        sa.Column('country_of_origin', sa.String(length=100), nullable=True),
        sa.Column('warranty_period', sa.String(length=100), nullable=True),
        sa.Column('certifications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['vendor_quote_id'], ['vendor_quotes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_equipment_items_name', 'equipment_items', ['name'])
    op.create_index('ix_equipment_items_model_number', 'equipment_items', ['model_number'])

    # Create price_breakdowns table
    op.create_table(
        'price_breakdowns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('equipment_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('total_price', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('discount_percent', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('tax_percent', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('shipping_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('installation_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('warranty_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('grand_total', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['equipment_item_id'], ['equipment_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create technical_specs table
    op.create_table(
        'technical_specs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('equipment_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parameter', sa.String(length=200), nullable=False),
        sa.Column('value', sa.String(length=500), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('is_compliant', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['equipment_item_id'], ['equipment_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_technical_specs_parameter', 'technical_specs', ['parameter'])

    # Create delivery_terms table
    op.create_table(
        'delivery_terms',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_quote_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('equipment_item_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('incoterm', sa.String(length=10), nullable=True),
        sa.Column('delivery_time_days', sa.Integer(), nullable=True),
        sa.Column('delivery_time_text', sa.String(length=200), nullable=True),
        sa.Column('delivery_location', sa.String(length=300), nullable=True),
        sa.Column('shipping_method', sa.String(length=100), nullable=True),
        sa.Column('partial_shipment_allowed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['vendor_quote_id'], ['vendor_quotes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['equipment_item_id'], ['equipment_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_delivery_terms_incoterm', 'delivery_terms', ['incoterm'])


def downgrade() -> None:
    op.drop_table('delivery_terms')
    op.drop_table('technical_specs')
    op.drop_table('price_breakdowns')
    op.drop_table('equipment_items')
    op.drop_table('vendor_quotes')
    op.drop_table('parse_results')
    op.drop_table('rfq_documents')
