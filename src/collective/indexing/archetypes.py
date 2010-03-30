try:
    from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
    from Products.Archetypes.BaseBTreeFolder import BaseBTreeFolder
    CatalogMultiplex, BaseBTreeFolder   # keep pyflakes happy
except ImportError:
    CatalogMultiplex = None
    BaseBTreeFolder = None
