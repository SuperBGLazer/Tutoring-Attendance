"""Add ondelete

Revision ID: 288da35a8768
Revises: 61df7927aa78
Create Date: 2024-10-29 23:15:41.679750

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '288da35a8768'
down_revision = '61df7927aa78'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_class', schema=None) as batch_op:
        batch_op.drop_constraint('student_class_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'student', ['student_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_class', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('student_class_ibfk_2', 'student', ['student_id'], ['id'])

    # ### end Alembic commands ###