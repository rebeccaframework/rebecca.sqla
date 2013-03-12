from zope.interface import Interface, Attribute
from pyramid.compat import text_

class IModelLoader(Interface):
    def __get__(obj, type):
        """ IModelLoader is descriptor provides only getter.
        """

class ISAContext(Interface):
    request = Attribute(text_("request for this context"))
    dbsession = Attribute(text_("DBSession of SQLAlchemy"))

class IDBSession(Interface):
    pass
