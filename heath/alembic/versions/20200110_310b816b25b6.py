"""Add accounts

Revision ID: 310b816b25b6
Revises: d8793bbcd821
Create Date: 2020-01-10 17:33:26.074880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '310b816b25b6'
down_revision = 'd8793bbcd821'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_accounts'))
    )
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_accounts_id'), ['id'], unique=False)

    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_transactions_account_id_accounts'), 'accounts', ['account_id'], ['id'])

    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_transactions_account_id_accounts'), type_='foreignkey')
        batch_op.drop_column('account_id')

    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_accounts_id'))

    op.drop_table('accounts')
    # ### end Alembic commands ###
