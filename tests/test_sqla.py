import pytest
from pyramid import testing
from testfixtures import compare
import mock

@pytest.fixture
def config(request):
    config = testing.setUp()
    def fin():
        testing.tearDown()

    request.addfinalizer(fin)
    return config


@pytest.fixture
def dbsession(request):
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///")
    from sqlalchemy.orm import (
        sessionmaker,
        scoped_session,
    )
    DBSession = scoped_session(sessionmaker())
    DBSession.configure(bind=engine)
    def fin():
        DBSession.remove()
    request.addfinalizer(fin)

    return DBSession

@pytest.fixture
def models(dbsession):
    from sqlalchemy import (
        Column,
        Integer,
        Unicode,
    )
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

    class Person(Base):
        __tablename__ = 'persons'
        id = Column(Integer, primary_key=True)
        name = Column(Unicode(255))

    Base.metadata.create_all(bind=dbsession.bind)
    class models(object):
        pass
    models.Person = Person
    return models


class TestModelLoader(object):
    @pytest.fixture
    def target(self):
        from rebecca.sqla import ModelLoader
        return ModelLoader

    @pytest.fixture
    def person10(self, dbsession, models):
        person10 = []
        for i in range(10):
            p = models.Person(name=u'testing {0}'.format(i))
            dbsession.add(p)
            person10.append(p)
        dbsession.flush()
        return person10

    def test_it(self, target, dbsession, person10, models):
        person = person10[3]
        person_id = person.id

        loader = target(models.Person, [('person_id', 'id')])
        request = testing.DummyRequest(
            matchdict={
                "person_id": str(person_id),
            }
        )
        context = testing.DummyResource(
            request=request,
            dbsession=dbsession,
        )
        request.context = context

        result = loader.__get__(context)

        compare(result, person)

    def test_none(self, target, dbsession, models):
        loader = target(models.Person, [('person_id', 'id')])
        request = testing.DummyRequest(
            matchdict={
                "person_id": "-1",
            }
        )
        context = testing.DummyResource(
            request=request,
            dbsession=dbsession,
        )
        request.context = context

        result = loader.__get__(context)

        assert result is None

    def test_no_matched_route(self, target, dbsession, person10, models):
        person = person10[3]
        person_id = person.id
        loader = target(models.Person, [('person_id', 'id')], 'test.route')
        request = testing.DummyRequest(
            matchdict={
                "person_id": str(person_id),
            },
            matched_route=testing.DummyResource(
                name="other.route"
            ),
        )
        context = testing.DummyResource(
            request=request,
            dbsession=dbsession,
        )
        request.context = context

        result = loader.__get__(context)

        assert result is None

    def test_matched_route(self, target, dbsession, person10, models):
        person = person10[4]
        person_id = person.id
        loader = target(models.Person, [('person_id', 'id')], 'test.route')
        request = testing.DummyRequest(
            matchdict={
                "person_id": str(person_id),
            },
            matched_route=testing.DummyResource(
                name="test.route"
            ),
        )
        context = testing.DummyResource(
            request=request,
            dbsession=dbsession,
        )
        request.context = context

        result = loader.__get__(context)

        assert result == person


class TestCreateSAContext(object):
    @pytest.fixture
    def target(self):
        from rebecca.sqla import create_sa_context
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
        from rebecca.sqla import add_model_loader
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
        from rebecca.sqla import register_sa_context
        return register_sa_context

    def test_it(self, config, target):
        from rebecca.sqla.interfaces import ISAContext
        request = testing.DummyRequest()
        target(config)
        result = config.registry.queryAdapter(request, ISAContext)
        assert result is not None
        assert ISAContext.providedBy(result)

class TestSAContextBase(object):
    @pytest.fixture
    def target(self):
        from rebecca.sqla import _SAContextBase
        return _SAContextBase

    def test_it(self, target):
        request = testing.DummyRequest()
        result = target(request)

        assert result.request == request
