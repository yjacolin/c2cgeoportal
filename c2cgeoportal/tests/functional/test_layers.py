from nose.plugins.attrib import attr
from pyramid import testing
from unittest import TestCase
import transaction

from c2cgeoportal.tests.functional import tearDownModule, setUpModule


@attr(functional=True)
class TestLayers(TestCase):

    def setUp(self):
        import sqlahelper
        engine = sqlahelper.get_engine()

        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base(bind=engine)

        from c2cgeoportal.lib.dbreflection import init
        init(engine)

        # FIXME drop (or don't create) table if it exists
        from sqlalchemy import Column, Table, MetaData, types
        from geoalchemy import GeometryDDL, GeometryExtensionColumn, Point
        table = Table('spots', Base.metadata,
                Column('id', types.Integer, primary_key=True),
                Column('name', types.Unicode),
                GeometryExtensionColumn('geom', Point),
                schema='public')
        GeometryDDL(table)
        table.create()
        self.table = table

        from c2cgeoportal.models import DBSession, Layer
        layer = Layer()
        layer.id = 1
        layer.geoTable = 'spots'
        DBSession.add(layer)
        transaction.commit()

    def tearDown(self):
        import transaction
        from c2cgeoportal.models import DBSession, Layer, TreeItem

        if self.table is not None:
            self.table.drop()

        treeitem = DBSession.query(TreeItem).get(1)
        DBSession.delete(treeitem)

        layer = DBSession.query(Layer).get(1)
        DBSession.delete(layer)
        transaction.commit()

    def test_metadata(self):
        from c2cgeoportal.views.layers import metadata
        request = testing.DummyRequest()
        # FIXME use routes rather than mocking
        request.matchdict = {'layer_id': 1}
        table = metadata(request)

        self.assertEquals(table.name, 'spots')

        import transaction
        transaction.commit()
