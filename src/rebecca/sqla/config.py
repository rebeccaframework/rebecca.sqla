from pyramid.interfaces import IRequest, PHASE1_CONFIG, PHASE2_CONFIG
from zope.interface import implementer, directlyProvides

from .components import _SAContextBase, MatchDictModelLoader
from .interfaces import IModelLoader, ISAContext, IDBSession

def create_sa_context(config):
    reg = config.registry
    loaders = dict(reg.utilities.lookupAll([], IModelLoader))
    dct = dict()
    dct.update(loaders)
    dct.update({'__loaders__': loaders})
    return type('$SAContext', (_SAContextBase,),
                dct)


def register_sa_context(config):
    reg = config.registry
    def register(intr):
        SAContext = create_sa_context(config)
        implementer(SAContext, ISAContext)
        reg.adapters.register([IRequest, IDBSession], ISAContext, '', SAContext)
        intr['loarders'] = SAContext.__loaders__

    intr = config.introspectable(category_name="rebecca.sqla.sacontext",
                                 discriminator="rebecca.sqla.register_sa_context",
                                 title="SAContext",
                                 type_name="$SAContext")

    config.action('rebecca.sqla.register_sa_context',
                  register,
                  introspectables=(intr,),
                  order=PHASE2_CONFIG,
                  args=(intr,),
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

    intr = config.introspectable(category_name="rebecca.sqla.modelloader",
                                 discriminator="rebecca.sqla.add_model_loader.{0}".format(name),
                                 title="Model Loader",
                                 type_name="MatchDictModelLoader")
    intr['name'] = name
    intr['param_map'] = param_map
    intr['route_name'] = route_name
    intr['model'] = model_cls.__name__

    config.action('rebecca.sqla.add_model_loader.{0}'.format(name),
                  register,
                  introspectables=(intr,),
                  order=PHASE1_CONFIG,
    )
