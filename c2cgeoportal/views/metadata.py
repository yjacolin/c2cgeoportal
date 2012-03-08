from papyrus.renderers import XSD
from pyramid.httpexceptions import HTTPInternalServerError, HTTPNotFound
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from c2cgeoportal.lib.dbreflection import get_class
from c2cgeoportal.models import DBSession, Layer


@view_config(route_name='metadata', renderer='xsd')
def metadata(request):
    layer_id = int(request.matchdict.get('layer_id'))
    try:
        table_name, = DBSession.query(Layer.geoTable).filter(Layer.id == layer_id).one()
    except NoResultFound:
        return HTTPNotFound()
    except MultipleResultsFound:
        return HTTPInternalServerError()
    # FIXME add DBSession as argument to get_class to avoid deadlock
    return get_class(str(table_name)).__table__
