from nose.plugins.attrib import attr
from pyramid import testing
from unittest import TestCase

from c2cgeoportal.tests.functional import tearDownModule, setUpModule


@attr(functional=True)
class TestLayers(TestCase):

    def setUp(self):
        import sqlahelper
        from c2cgeoportal.lib.dbreflection import init

        engine = sqlahelper.get_engine()
        init(engine)

    def tearDown(self):
        import transaction
        from c2cgeoportal.models import DBSession, Layer, TreeItem

        transaction.commit()

        if self.table is not None:
            self.table.drop()

        treeitem = DBSession.query(TreeItem).get(1)
        DBSession.delete(treeitem)

        layer = DBSession.query(Layer).get(1)
        DBSession.delete(layer)

        transaction.commit()

    def _create_layer(self, tablename):
        import transaction
        import sqlahelper
        from sqlalchemy import Column, Table, MetaData, types
        from sqlalchemy.ext.declarative import declarative_base
        from geoalchemy import GeometryDDL, GeometryExtensionColumn
        from geoalchemy import Point

        engine = sqlahelper.get_engine()
        Base = declarative_base(bind=engine)

        table = Table(tablename, Base.metadata,
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
        layer.geoTable = tablename
        DBSession.add(layer)

        transaction.commit()

    def _get_request(self, layerid):
        request = testing.DummyRequest()
        # FIXME there may be a better way
        request.matchdict = {'layer_id': layerid}
        return request

    def test_read_many(self):
        from geojson.feature import FeatureCollection
        from c2cgeoportal.views.layers import read_many

        self._create_layer('layer_a')
        request = self._get_request(1)

        collection = read_many(request)
        self.assertTrue(isinstance(collection, FeatureCollection))

    def test_read_one(self):
        from pyramid.httpexceptions import HTTPNotFound
        from c2cgeoportal.views.layers import read_one

        self._create_layer('layer_b')
        request = self._get_request(1)
        request.matchdict['feature_id'] = 2

        response = read_one(request)
        self.assertTrue(isinstance(response, HTTPNotFound))

    def test_count(self):
        from c2cgeoportal.views.layers import count

        self._create_layer('layer_c')
        request = self._get_request(1)

        response = count(request)
        self.assertEquals(response, 0)

    def test_metadata(self):
        from c2cgeoportal.views.layers import metadata

        self._create_layer('layer_d')
        request = self._get_request(1)

        table = metadata(request)
        self.assertEquals(table.name, 'layer_d')
