.. contents::

rebecca.sqla
===============

``rebecca.sqla`` is utility to load model made on SQLAlchemy.


INSTALL
-----------------

Install using pip or easy_install::

  $ pip install rebecca.sqla
  $ easy_install rebeca.sqla


USAGE
--------------------

``rebecca.sql`` needs ``sqlalchemy.orm.scoped_session``.

specify session object and dsn string in settings::

  sqlalchemy.url = 'sqlite:///'
  rebecca.sqla.session = your.app.models.DBSession


``rebecca.sqla`` has include hook::

  config.include("rebecca.sqla")


this hook sets up the ``bind`` configuration of DBSession to ``sqlalchemy.url``.


``ModelLoader`` and ``SAContext``
---------------------------------------------

``rebecca.sqla`` creates attribute named "sa"  to ``request.context``.
``context.sa`` is ``SAContext`` to load models from ``ModelLoader`` registered by ``config.add_model_loader``.

here is example models::

  class Person(Base):
      __tablename__ = 'person'
      id = Column(Integer, primary_key=True)
      name = Column(Unicode(255))

and example route::

   config.add_route('person', '/person/{person1_id}/{person2_id}')

register model loaders::

   config.add_model_loader('person1', Person, [('person1_id', 'id')])
   config.add_model_loader('person2', Person, [('person2_id', 'id')])


``add_model_loader`` takes 3 arguments.
first is attr name of ``SAContext``,
second is a model loaded from ``ModelLoader`` and last is mappings that matchdict param to model attribute.

second argument can be dotted name.


in view, context has ``SAContext`` named "sa" attribute, that has properties of registered models.
``ModelLoader`` s load model with query using matchdict parameters.

::

   def person(context, request):
       person1 = context.sa.person1
       person2 = context.sa.person2



