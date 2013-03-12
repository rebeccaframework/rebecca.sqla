from zope.interface import Interface, Attribute

class IModelLoader(Interface):
    def __get__(obj, type):
        """ IModelLoader is descriptor provides only getter.
        """

class ISAContext(Interface):
    request = Attribute(u"request for this context")
    dbsession = Attribute(u"DBSession of SQLAlchemy")
