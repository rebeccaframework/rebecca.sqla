import pytest
from pyramid import testing
from pyramid.compat import text_

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


class TestSAContextBase(object):
    @pytest.fixture
    def target(self):
        from rebecca.sqla.components import _SAContextBase
        return _SAContextBase

    def test_it(self, target):
        request = testing.DummyRequest()
        dbsession = testing.DummyResource()
        result = target(request, dbsession)

        assert result.request == request
        assert result.dbsession == dbsession


class TestMatchDictModelLoader(object):
    @pytest.fixture
    def target(self):
        from rebecca.sqla.components import MatchDictModelLoader
        return MatchDictModelLoader

    @pytest.fixture
    def person10(self, dbsession, models):
        person10 = []
        for i in range(10):
            p = models.Person(name=text_('testing {0}').format(i))
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

        assert result == person

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

