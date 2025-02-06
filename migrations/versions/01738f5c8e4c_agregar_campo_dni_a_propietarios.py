"""Agregar campo DNI a propietarios

Revision ID: 01738f5c8e4c
Revises: 45e1fa727b61
Create Date: 2025-02-06 13:26:13.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01738f5c8e4c'
down_revision = '45e1fa727b61'
branch_labels = None
depends_on = None


def upgrade():
    # Crear una tabla temporal con la nueva estructura
    op.execute('''
        CREATE TABLE propietarios_new (
            id INTEGER NOT NULL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            dni VARCHAR(20) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            telefono VARCHAR(20) NOT NULL,
            created_at DATETIME,
            updated_at DATETIME
        )
    ''')
    
    # Copiar los datos existentes a la nueva tabla con un valor por defecto para dni
    op.execute('''
        INSERT INTO propietarios_new (id, nombre, dni, email, telefono, created_at, updated_at)
        SELECT id, nombre, 'Por completar', email, telefono, created_at, updated_at
        FROM propietarios
    ''')
    
    # Eliminar la tabla vieja
    op.execute('DROP TABLE propietarios')
    
    # Renombrar la tabla nueva
    op.execute('ALTER TABLE propietarios_new RENAME TO propietarios')


def downgrade():
    # Crear una tabla temporal sin la columna dni
    op.execute('''
        CREATE TABLE propietarios_new (
            id INTEGER NOT NULL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL,
            telefono VARCHAR(20),
            created_at DATETIME,
            updated_at DATETIME
        )
    ''')
    
    # Copiar los datos sin la columna dni
    op.execute('''
        INSERT INTO propietarios_new (id, nombre, email, telefono, created_at, updated_at)
        SELECT id, nombre, email, telefono, created_at, updated_at
        FROM propietarios
    ''')
    
    # Eliminar la tabla vieja
    op.execute('DROP TABLE propietarios')
    
    # Renombrar la tabla nueva
    op.execute('ALTER TABLE propietarios_new RENAME TO propietarios')
    
    # Recrear el índice original
    op.execute('CREATE INDEX ix_propietarios_email ON propietarios (email)')
