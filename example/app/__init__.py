from pyramid.config import Configurator
from wsgiref.simple_server import make_server
from sqlalchemy import (
    Column,
    Integer,
    Unicode,
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
Base = declarative_base()
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))

def hello(context, request):
    request.response.text = u"<html><head></head><body>{0}</body></html>".format(context.sa)

    return request.response

def person_view(context, request):
    request.response.text = u"person1 {0.id} {0.name} person2 {1.id} {1.name}".format(
        context.sa.person1,
        context.sa.person2,
    )
    return request.response

settings = {
    "sqlalchemy.url": "sqlite:///",
    "rebecca.sqla.session": DBSession,
}

config = Configurator(settings=settings)
config.include('pyramid_tm')
config.include('pyramid_debugtoolbar')
config.include('rebecca.sqla')
Base.metadata.create_all(bind=DBSession.bind)
for i in range(10):
    p = Person(name=u"person {0}".format(i))
    DBSession.add(p)
import transaction
transaction.commit()

config.add_model_loader('person1', Person, [('person1_id', 'id')])
config.add_model_loader('person2', Person, [('person2_id', 'id')])
config.add_route('person', '/person/{person1_id}/{person2_id}')
config.add_view(person_view, route_name='person')
config.add_view(hello)
app = config.make_wsgi_app()

httpd = make_server('', 8080, app)
httpd.serve_forever()
