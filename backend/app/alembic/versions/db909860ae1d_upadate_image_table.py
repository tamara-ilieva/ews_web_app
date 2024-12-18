"""upadate image table

Revision ID: db909860ae1d
Revises: c675b4ce964b
Create Date: 2024-05-29 14:55:58.721467

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'db909860ae1d'
down_revision = 'c675b4ce964b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dynamic_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('disease', sa.Integer(), nullable=True),
    sa.Column('file_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('is_sick', sa.Boolean(), nullable=False),
    sa.Column('is_sick_confirmed', sa.Boolean(), nullable=False),
    sa.Column('predicted_disease', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('confirmed_disease', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['disease'], ['diseases.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dynamic_images_id'), 'dynamic_images', ['id'], unique=False)
    op.create_table('static_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('disease', sa.Integer(), nullable=True),
    sa.Column('file_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('is_sick', sa.Boolean(), nullable=False),
    sa.Column('is_sick_confirmed', sa.Boolean(), nullable=False),
    sa.Column('predicted_disease', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('confirmed_disease', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['disease'], ['diseases.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_static_images_id'), 'static_images', ['id'], unique=False)
    op.create_table('uploaded_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('disease', sa.Integer(), nullable=True),
    sa.Column('file_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('is_sick', sa.Boolean(), nullable=False),
    sa.Column('is_sick_confirmed', sa.Boolean(), nullable=False),
    sa.Column('predicted_disease', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('confirmed_disease', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['disease'], ['diseases.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_uploaded_images_id'), 'uploaded_images', ['id'], unique=False)
    op.add_column('images', sa.Column('predicted_disease', sa.Integer(), nullable=True))
    op.add_column('images', sa.Column('is_sick', sa.Boolean(), nullable=True))
    op.add_column('images', sa.Column('predicted_disease_human_input', sa.Integer(), nullable=True))
    op.add_column('images', sa.Column('is_sick_human_input', sa.Boolean(), nullable=True))
    op.drop_constraint('images_ibfk_1', 'images', type_='foreignkey')
    op.create_foreign_key(None, 'images', 'diseases', ['predicted_disease_human_input'], ['id'])
    op.create_foreign_key(None, 'images', 'diseases', ['predicted_disease'], ['id'])
    op.drop_column('images', 'disease')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('disease', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'images', type_='foreignkey')
    op.drop_constraint(None, 'images', type_='foreignkey')
    op.create_foreign_key('images_ibfk_1', 'images', 'diseases', ['disease'], ['id'])
    op.drop_column('images', 'is_sick_human_input')
    op.drop_column('images', 'predicted_disease_human_input')
    op.drop_column('images', 'is_sick')
    op.drop_column('images', 'predicted_disease')
    op.drop_index(op.f('ix_uploaded_images_id'), table_name='uploaded_images')
    op.drop_table('uploaded_images')
    op.drop_index(op.f('ix_static_images_id'), table_name='static_images')
    op.drop_table('static_images')
    op.drop_index(op.f('ix_dynamic_images_id'), table_name='dynamic_images')
    op.drop_table('dynamic_images')
    # ### end Alembic commands ###
