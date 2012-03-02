from sqlalchemy import MetaData, Table, Column, types

from c2cgeoportal import schema

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)

    layer = Table('layer', meta, schema=schema, autoload=True)
    Column('editTable', types.Unicode, default=u'').create(layer)

    restrictionarea = Table('restrictionarea', meta, schema=schema, autoload=True)
    allow = types.Enum("read", "write", "booth", 
            name=schema+".restrictionallow", 
            native_enum=False,
            metadata=meta)
    Column('allow', allow, default='read').create(restrictionarea)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)

    layer = Table('layer', meta, schema=schema, autoload=True)
    layer.c.editTable.drop()

    restrictionarea = Table('restrictionarea', meta, schema=schema, autoload=True)
    restrictionarea.c.allow.drop()
