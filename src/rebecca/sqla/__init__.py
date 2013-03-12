from zope.interface import implementer, directlyProvides
from .interfaces import IModelLoader, ISAContext

@implementer(IModelLoader)
class ModelLoader(object):
    def __init__(self, model_cls, param_map, route_name=None):
        self.model_cls = model_cls
        self.param_map = param_map
        self.route_name = route_name

    def __get__(self, obj, type=None):
        request = obj.request
        if self.route_name is not None and request.matched_route.name != self.route_name:
            return None

        values = request.matchdict
        session = obj.dbsession

        query = session.query(self.model_cls)
        for param_name, attr_name in self.param_map:
            value = values.get(param_name)
            if value:
                query = query.filter_by(**{attr_name: value})
        return query.first()

@implementer(ISAContext)
class _SAContextBase(object):
    def __init__(self, request):
        self.request = request

def create_sa_context(config):
    reg = config.registry
    loaders = reg.utilities.lookupAll([], IModelLoader)

    return type('rebecca.sqla.$SAContext', (_SAContextBase,),
                dict(loaders))

def register_sa_context(config):
    reg = config.registry
    def register():
        SAContext = create_sa_context(config)
        directlyProvides(SAContext, ISAContext)
        reg.registerUtility(SAContext)

    config.action('rebecca.sqla.register_sa_context',
                  register)

def add_model_loader(config, name, model_cls, param_map, route_name=None):
    model_cls = config.maybe_dotted(model_cls)
    reg = config.registry
    def register():
        loader = ModelLoader(model_cls=model_cls,
                             param_map=param_map,
                             route_name=route_name)
        directlyProvides(loader, IModelLoader)
        reg.registerUtility(loader, name=name)

    config.action('rebecca.sqla.add_model_loader.{0}'.format(name),
                  register)
