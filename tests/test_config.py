import pytest
from pyramid import testing


@pytest.fixture
def config(request):
    config = testing.setUp()
    def fin():
        testing.tearDown()

    request.addfinalizer(fin)
    return config




class TestCreateSAContext(object):
    @pytest.fixture
    def target(self):
        from rebecca.sqla.config import create_sa_context
        return create_sa_context

    def test_no_member(self, target, config):
        result = target(config)

        assert result.__name__ == '$SAContext'


    def test_one(self, target, config):
        from zope.interface import directlyProvides
        from rebecca.sqla.interfaces import IModelLoader
        loader = testing.DummyModel()
        directlyProvides(loader, IModelLoader)
        config.registry.registerUtility(loader, name="testing")

        result = target(config)

        assert result.__name__ == '$SAContext'
        assert result.testing == loader



class TestAddModelLoader(object):
    @pytest.fixture
    def target(self):
        from rebecca.sqla.config import add_model_loader
        return add_model_loader

    def test_it(self, config, target):
        from rebecca.sqla.interfaces import IModelLoader
        target(config, "testing",
               testing.DummyModel,
               [('value1', 'value1')],
               route_name='testing.route')
        result = config.registry.queryUtility(IModelLoader, name='testing')

        assert result.model_cls == testing.DummyModel


class TestRegisterSAContext(object):
    @pytest.fixture
    def target(self):
        from rebecca.sqla.config import register_sa_context
        return register_sa_context

    def test_it(self, config, target):
        from zope.interface import directlyProvides
        from rebecca.sqla.interfaces import ISAContext, IDBSession
        
        request = testing.DummyRequest()
        dbsession = testing.DummyResource()
        directlyProvides(dbsession, IDBSession)
        target(config)
        result = config.registry.queryMultiAdapter([request, dbsession], ISAContext)
        assert result is not None
        assert ISAContext.providedBy(result)

