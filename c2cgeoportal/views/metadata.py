from geoalchemy import Geometry
from papyrus.renderers import XSD
from pyramid.httpexceptions import HTTPInternalServerError, HTTPNotFound
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from c2cgeoportal.lib.dbreflection import get_class
from c2cgeoportal.models import DBSession, Layer


def get_class_for_request(request):
    layer_id = int(request.matchdict['layer_id'])
    try:
        table_name, = DBSession.query(Layer.geoTable).filter(Layer.id == layer_id).one()
    except NoResultFound:
        raise HTTPNotFound("Layer not found")
    except MultipleResultsFound:
        raise HTTPInternalServerError()
    # FIXME add DBSession as argument to get_class to avoid deadlock
    return get_class(str(table_name))


def get_geom_attr_for_mapped_class(mapped_class):
    # FIXME check this logic
    for columns in mapped_class.__table__.columns:
        if isinstance(column, Geometry):
            return column.name
    raise HTTPInternalServerError()


@view_config(route_name='generic_read_many', renderer='geojson')
def generic_read_many(request):
    mapped_class = get_class_for_request(request)
    geom_attr = get_geom_attr_for_mapped_class(mapped_class)
    protocol = Protocol(lambda: DBSession, mapped_class, geom_attr)
    return protocol.read(request)


@view_config(route_name='generic_read_one', renderer='geojson')
def generic_read_many(request):
    mapped_class = get_class_for_request(request)
    geom_attr = get_geom_attr_for_mapped_class(mapped_class)
    protocol = Protocol(lambda: DBSession, mapped_class, geom_attr)
    feature_id = int(request.matchdict['feature_id'])
    return protocol.read(request, id=feature_id)


@view_config(route_name='generic_count', renderer='string')
def generic_read_many(request):
    mapped_class = get_class_for_request(request)
    geom_attr = get_geom_attr_for_mapped_class(mapped_class)
    protocol = Protocol(lambda: DBSession, mapped_class, geom_attr)
    return protocol.count(request)


@view_config(route_name='generic_create', renderer='geojson')
def generic_read_many(request):
    mapped_class = get_class_for_request(request)
    geom_attr = get_geom_attr_for_mapped_class(mapped_class)
    protocol = Protocol(lambda: DBSession, mapped_class, geom_attr)
    return protocol.create(request)


@view_config(route_name='generic_update', renderer='geojson')
def generic_read_many(request):
    mapped_class = get_class_for_request(request)
    geom_attr = get_geom_attr_for_mapped_class(mapped_class)
    protocol = Protocol(lambda: DBSession, mapped_class, geom_attr)
    feature_id = int(request.matchdict['feature_id'])
    return protocol.update(request, feature_id)


@view_config(route_name='generic_delete')
def generic_read_many(request):
    mapped_class = get_class_for_request(request)
    geom_attr = get_geom_attr_for_mapped_class(mapped_class)
    protocol = Protocol(lambda: DBSession, mapped_class, geom_attr)
    feature_id = int(request.matchdict['feature_id'])
    return protocol.delete(request, feature_id)


@view_config(route_name='generic_md', renderer='xsd')
def metadata(request):
    mapped_class = get_class_for_request(request)
    return mapped_class.__table__
