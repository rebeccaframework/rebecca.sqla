from pyramid.events import subscriber, ContextFound
from pyramid.interfaces import IRequest
from sqlalchemy import engine_from_config
from zope.interface import directlyProvides
from .interfaces import IDBSession, ISAContext



@subscriber(ContextFound)
def add_sa_context_attr(event):
    request = event.request
    reg = request.registry
    dbsession = reg.queryUtility(IDBSession)
    context = request.context

    factory = reg.adapters.lookup([IRequest, IDBSession], ISAContext, "")
    context.sa = factory(request)
    context.sa.dbsession = dbsession


def setup_db(config):
    engine = engine_from_config(config.registry.settings)
    dbsession = config.registry.settings['rebecca.sqla.session']
    dbsession = config.maybe_dotted(dbsession)
    dbsession.remove()
    dbsession.configure(bind=engine)
    directlyProvides(dbsession, IDBSession)
    config.registry.registerUtility(dbsession, IDBSession)


def includeme(config):
    setup_db(config)
    config.add_directive("add_model_loader", '.config.add_model_loader')
    config.add_directive("register_sa_context", '.config.register_sa_context')
    config.register_sa_context()
    config.scan(".")
