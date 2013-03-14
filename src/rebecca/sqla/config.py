from pyramid.interfaces import IRequest, PHASE1_CONFIG, PHASE2_CONFIG
from zope.interface import implementer, directlyProvides

from .components import _SAContextBase, MatchDictModelLoader
from .interfaces import IModelLoader, ISAContext

def create_sa_context(config):
    reg = config.registry
    loaders = reg.utilities.lookupAll([], IModelLoader)

    return type('$SAContext', (_SAContextBase,),
                dict(loaders))


def register_sa_context(config):
    reg = config.registry
    def register():
        SAContext = create_sa_context(config)
        implementer(SAContext, ISAContext)
        reg.adapters.register([IRequest], ISAContext, '', SAContext)

    config.action('rebecca.sqla.register_sa_context',
                  register,
                  order=PHASE2_CONFIG,
    )


def add_model_loader(config, name, model_cls, param_map, route_name=None):
    model_cls = config.maybe_dotted(model_cls)
    reg = config.registry
    def register():
        loader = MatchDictModelLoader(model_cls=model_cls,
                             param_map=param_map,
                             route_name=route_name)
        directlyProvides(loader, IModelLoader)
        reg.registerUtility(loader, name=name)

    config.action('rebecca.sqla.add_model_loader.{0}'.format(name),
                  register,
                  order=PHASE1_CONFIG,
    )
