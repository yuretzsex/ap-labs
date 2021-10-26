"""models

Revision ID: 5192e95b1684
Revises: 
Create Date: 2021-10-26 00:04:55.944990

"""
from alembic import op
import sqlalchemy as sa
from models import base, engine

# revision identifiers, used by Alembic.
revision = '5192e95b1684'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('first_name', sa.String(30)),
                    sa.Column('last_name', sa.String(30)),
                    sa.Column('email', sa.String(30), unique=True),
                    sa.Column('password', sa.String(15)),
                    sa.Column('phone', sa.String(15), unique=True))

    op.create_table('notes',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('header', sa.String(30)),
                    sa.Column('text', sa.String(150))
                    )

    op.create_table('edits',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('note', sa.Integer, sa.ForeignKey('notes.id')),
                    sa.Column('editor', sa.Integer, sa.ForeignKey('users.id')),
                    sa.Column('old_text', sa.String(150)),
                    sa.Column('new_text', sa.String(150)),
                    sa.Column('when_created', sa.DateTime)
                    )

    op.create_table('stats',
                    sa.Column('id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True),
                    sa.Column('notes_created', sa.Integer)
                    )

    op.create_table('tags',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String(30))
                    )

    op.create_table('note_tag',
                    sa.Column('note', sa.Integer, sa.ForeignKey('notes.id'), primary_key=True),
                    sa.Column('tag', sa.Integer, sa.ForeignKey('tags.id'), primary_key=True)
                    )

    op.create_table('note_editor',
                    sa.Column('note', sa.Integer, sa.ForeignKey('notes.id'), primary_key=True),
                    sa.Column('editor', sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
                    )


def downgrade():
    op.drop_table('note_editor')
    op.drop_table('stats')
    op.drop_table('edits')
    op.drop_table('note_tag')
    op.drop_table('users')
    op.drop_table('notes')
    op.drop_table('tags')