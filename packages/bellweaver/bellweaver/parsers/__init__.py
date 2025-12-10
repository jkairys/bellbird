"""Parser modules for transforming raw API responses into validated domain models.

CompassParser is now provided by the compass_client package. Import it from there:

    from compass_client import CompassParser
"""

# Re-export compass_client parser for backward compatibility
from compass_client import CompassParser

__all__ = ["CompassParser"]
