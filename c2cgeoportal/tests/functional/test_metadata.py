from nose.plugins.attrib import attr
from pyramid import testing
from unittest import TestCase
import transaction

from c2cgeoportal.tests.functional import tearDownModule, setUpModule


@attr(functional=True)
class TestMetadata(TestCase):

    def setUp(self):
        self.config = testing.setUp()

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
        layer.editTable = 'spots'
        DBSession.add(layer)
        transaction.commit()

    def tearDown(self):
        testing.tearDown()
        if self.table is not None:
            table.drop()

    def test_metadata(self):
        from c2cgeoportal.views.metadata import metadata
        request = testing.DummyRequest()
        # FIXME use routes rather than mocking
        request.matchdict = {'layer_id': 1}
        table = metadata(request)
        # FIXME install renderer in setUp instead of invoking it directly here
        from papyrus.renderers import XSD
        response = XSD()(None)(table, {'request': request})
        self.assertEquals(response.content_type, 'text/xml')
