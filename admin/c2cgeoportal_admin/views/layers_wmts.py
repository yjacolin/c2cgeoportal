from functools import partial
from sqlalchemy import insert, delete, update
from zope.sqlalchemy import mark_changed
from pyramid.view import view_defaults
from pyramid.view import view_config

from sqlalchemy import inspect

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import ListField, ItemAction

from c2cgeoportal_admin import _
from c2cgeoportal_commons.models.main import LayerWMTS, LayerWMS, TreeItem
from c2cgeoportal_admin.schemas.dimensions import dimensions_schema_node
from c2cgeoportal_admin.schemas.metadata import metadatas_schema_node
from c2cgeoportal_admin.schemas.interfaces import interfaces_schema_node
from c2cgeoportal_admin.schemas.restrictionareas import restrictionareas_schema_node
from c2cgeoportal_admin.views.dimension_layers import DimensionLayerViews

_list_field = partial(ListField, LayerWMTS)

base_schema = GeoFormSchemaNode(LayerWMTS)
base_schema.add(dimensions_schema_node.clone())
base_schema.add(metadatas_schema_node.clone())
base_schema.add(interfaces_schema_node.clone())
base_schema.add(restrictionareas_schema_node.clone())
base_schema.add_unique_validator(LayerWMTS.name, LayerWMTS.id)


@view_defaults(match_param='table=layers_wmts')
class LayerWmtsViews(DimensionLayerViews):
    _list_fields = DimensionLayerViews._list_fields + [
        _list_field('url'),
        _list_field('layer'),
        _list_field('style'),
        _list_field('matrix_set'),
        _list_field('image_type'),
    ] + DimensionLayerViews._extra_list_fields
    _id_field = 'id'
    _model = LayerWMTS
    _base_schema = base_schema

    def _base_query(self, query=None):
        return super()._base_query(
            self._request.dbsession.query(LayerWMTS).distinct())

    @view_config(route_name='c2cgeoform_index',
                 renderer='../templates/index.jinja2')
    def index(self):
        return super().index()

    @view_config(route_name='c2cgeoform_grid',
                 renderer='json')
    def grid(self):
        return super().grid()

    def _item_actions(self, item, grid=False):
        actions = super()._item_actions(item, grid)
        if inspect(item).persistent:
            actions.insert(1, ItemAction(
                name='convert_to_wms',
                label=_('Convert to WMS'),
                icon='glyphicon icon-l_wmts',
                url=self._request.route_url(
                    'convert_to_wms',
                    id=getattr(item, self._id_field)),
                method='POST',
                confirmation=_('Are you sure you want to convert this layer to WMS ?')))
        return actions

    @view_config(route_name='c2cgeoform_item',
                 request_method='GET',
                 renderer='../templates/edit.jinja2')
    def view(self):
        return super().edit()

    @view_config(route_name='c2cgeoform_item',
                 request_method='POST',
                 renderer='../templates/edit.jinja2')
    def save(self):
        return super().save()

    @view_config(route_name='c2cgeoform_item',
                 request_method='DELETE',
                 renderer='json')
    def delete(self):
        return super().delete()

    @view_config(route_name='c2cgeoform_item_duplicate',
                 request_method='GET',
                 renderer='../templates/edit.jinja2')
    def duplicate(self):
        return super().duplicate()

    @view_config(route_name='convert_to_wms',
                 request_method='POST',
                 renderer='json')
    def convert_to_wms(self):
        src = self._get_object()
        dbsession = self._request.dbsession
        default_wms = dbsession.query(LayerWMS).filter(LayerWMS.name == 'wms-defaults').one()
        with dbsession.no_autoflush:
            d = delete(LayerWMTS.__table__)
            d = d.where(LayerWMTS.__table__.c.id == src.id)
            dbsession.execute(d)
            i = insert(LayerWMS.__table__)
            i = i.values({
                'id': src.id,
                'layer': src.layer,
                'style': src.style,
                'ogc_server_id': default_wms.ogc_server_id,
                'time_mode': default_wms.time_mode,
                'time_widget': default_wms.time_widget})
            dbsession.execute(i)
            u = update(TreeItem.__table__)
            u = u.where(TreeItem.__table__.c.id == src.id)
            u = u.values({'type': 'l_wms'})
            dbsession.execute(u)
            dbsession.expunge(src)

        dbsession.flush()
        mark_changed(dbsession)

        return {
            'success': True,
            'redirect': self._request.route_url(
                'c2cgeoform_item',
                table='layers_wms',
                id=self._request.matchdict['id'])
        }
