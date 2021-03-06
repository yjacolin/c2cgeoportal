# pylint: disable=no-self-use

import re
import pytest

from . import AbstractViewsTests


@pytest.fixture(scope='class')
@pytest.mark.usefixtures('dbsession')
def layer_wmts_test_data(dbsession):
    from c2cgeoportal_commons.models.main import \
        LayerWMTS, RestrictionArea, Interface

    dbsession.begin_nested()

    restrictionareas = [RestrictionArea(name='restrictionarea_{}'.format(i))
                        for i in range(0, 5)]

    interfaces = [Interface(name) for name in ['desktop', 'mobile', 'edit', 'routing']]

    layers = []
    for i in range(0, 25):
        name = 'layer_wmts_{}'.format(i)
        layer = LayerWMTS(name=name)
        layer.layer = name
        layer.url = 'https://server{}.net/wmts'.format(i)
        layer.restrictionareas = [restrictionareas[i % 5],
                                  restrictionareas[(i + 2) % 5]]
        if i % 10 != 1:
            layer.interfaces = [interfaces[i % 4], interfaces[(i + 2) % 4]]
        layer.public = 1 == i % 2
        layer.image_type = 'image/jpeg'
        dbsession.add(layer)
        layers.append(layer)

    dbsession.flush()
    yield {
        'layers': layers,
        'restrictionareas': restrictionareas,
        'interfaces': interfaces
    }

    dbsession.rollback()


@pytest.mark.usefixtures('layer_wmts_test_data', 'transact', 'test_app')
class TestLayerWMTS(AbstractViewsTests):

    _prefix = '/layers_wmts'

    def test_index_rendering(self, test_app):
        resp = self.get(test_app)

        self.check_left_menu(resp, 'WMTS Layers')

        expected = [('_id_', '', 'false'),
                    ('name', 'Name', 'true'),
                    ('metadata_url', 'Metadata URL', 'true'),
                    ('description', 'Description', 'true'),
                    ('public', 'Public', 'true'),
                    ('geo_table', 'Geo table', 'true'),
                    ('exclude_properties', 'Exclude properties', 'true'),
                    ('url', 'GetCapabilities URL', 'true'),
                    ('layer', 'WMTS layer name', 'true'),
                    ('style', 'Style', 'true'),
                    ('matrix_set', 'Matrix set', 'true'),
                    ('image_type', 'Image type', 'true'),
                    ('dimensions', 'Dimensions', 'false'),
                    ('interfaces', 'Interfaces', 'true'),
                    ('restrictionareas', 'Restriction areas', 'false'),
                    ('parents_relation', 'Parents', 'false'),
                    ('metadatas', 'Metadatas', 'false')]
        self.check_grid_headers(resp, expected)

    def test_grid_complex_column_val(self, test_app, layer_wmts_test_data):
        json = test_app.post(
            '/layers_wmts/grid.json',
            params={
                'current': 1,
                'rowCount': 10,
                'sort[name]': 'asc'
            },
            status=200
        ).json
        row = json['rows'][0]

        layer = layer_wmts_test_data['layers'][0]

        assert layer.id == int(row['_id_'])
        assert layer.name == row['name']

    def test_edit(self, test_app, layer_wmts_test_data, dbsession):
        layer = layer_wmts_test_data['layers'][0]

        form = self.get_item(test_app, layer.id).form

        assert str(layer.id) == self.get_first_field_named(form, 'id').value
        assert 'hidden' == self.get_first_field_named(form, 'id').attrs['type']
        assert layer.name == self.get_first_field_named(form, 'name').value
        assert str(layer.description or '') == self.get_first_field_named(form, 'description').value
        assert str(layer.metadata_url or '') == form['metadata_url'].value
        assert layer.public is False
        assert layer.public == form['public'].checked
        assert str(layer.geo_table or '') == form['geo_table'].value
        assert str(layer.exclude_properties or '') == form['exclude_properties'].value
        assert str(layer.url or '') == form['url'].value
        assert str(layer.layer or '') == form['layer'].value
        assert str(layer.style or '') == form['style'].value
        assert str(layer.matrix_set or '') == form['matrix_set'].value
        assert str(layer.image_type or '') == form['image_type'].value

        interfaces = layer_wmts_test_data['interfaces']
        assert set((interfaces[0].id, interfaces[2].id)) == set(i.id for i in layer.interfaces)
        self._check_interfaces(form, interfaces, layer)

        ras = layer_wmts_test_data['restrictionareas']
        assert set((ras[0].id, ras[2].id)) == set(i.id for i in layer.restrictionareas)
        self._check_restrictionsareas(form, ras, layer)

        new_values = {
            'name': 'new_name',
            'metadata_url': 'https://new_metadata_url',
            'description': 'new description',
            'public': True,
            'geo_table': 'new_geo_table',
            'exclude_properties': 'property1,property2',
            'url': 'new_url',
            'layer': 'new_wmslayername',
            'style': 'new_style',
            'matrix_set': 'new_matrix_set',
            'image_type': 'image/png'
        }

        for key, value in new_values.items():
            self.set_first_field_named(form, key, value)
        form['interfaces'] = [interfaces[1].id, interfaces[3].id]
        form['restrictionareas'] = [ras[1].id, ras[3].id]

        resp = form.submit('submit')
        assert str(layer.id) == re.match(
            'http://localhost{}/(.*)'.format(self._prefix),
            resp.location).group(1)

        dbsession.expire(layer)
        for key, value in new_values.items():
            if isinstance(value, bool):
                assert value == getattr(layer, key)
            else:
                assert str(value or '') == str(getattr(layer, key) or '')
        assert set([interfaces[1].id, interfaces[3].id]) == set(
            [interface.id for interface in layer.interfaces])
        assert set([ras[1].id, ras[3].id]) == set([ra.id for ra in layer.restrictionareas])

    def test_duplicate(self, layer_wmts_test_data, test_app, dbsession):
        from c2cgeoportal_commons.models.main import LayerWMTS
        layer = layer_wmts_test_data['layers'][3]

        resp = test_app.get("/layers_wmts/{}/duplicate".format(layer.id), status=200)
        form = resp.form

        assert '' == self.get_first_field_named(form, 'id').value
        assert layer.name == self.get_first_field_named(form, 'name').value
        assert str(layer.metadata_url or '') == form['metadata_url'].value
        assert str(layer.description or '') == self.get_first_field_named(form, 'description').value
        assert layer.public is True
        assert layer.public == form['public'].checked
        assert str(layer.geo_table or '') == form['geo_table'].value
        assert str(layer.exclude_properties or '') == form['exclude_properties'].value
        assert str(layer.layer or '') == form['layer'].value
        assert str(layer.style or '') == form['style'].value

        ras = layer_wmts_test_data['restrictionareas']
        self._check_restrictionsareas(form, ras, layer)

        self.set_first_field_named(form, 'name', 'clone')
        resp = form.submit('submit')

        layer = dbsession.query(LayerWMTS). \
            filter(LayerWMTS.name == 'clone'). \
            one()
        assert str(layer.id) == re.match('http://localhost/layers_wmts/(.*)', resp.location).group(1)
