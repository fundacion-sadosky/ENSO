"""
App0Platform: App
"""
from typing import List, Optional

from bson.objectid import ObjectId  # type: ignore
from hopeit.dataobjects import dataclass, dataobject

from app0.admin import fd
from app0.admin.file import PlatformFile


@dataobject
@dataclass
class AppRole:
    """
    Application role
    """
    name: str = fd("Role name")
    description: str = fd("Description")
    id: Optional[str] = None
    enabled: bool = fd("Document enabled", default=True)
    application: Optional[str] = fd("Application", default=None)
    can_delete: bool = fd("Can be deleted?", default=True)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())


@dataobject
@dataclass
class AppDef:
    """
    Application definition
    """
    name: str = fd("Name")
    description: str = fd("Description")
    url: str = fd("Url Info")
    image: Optional[str] = fd("Principal app image", default=None)
    default_role: str = fd("Default App Role", default=None)
    roles: List[str] = fd("List of App Roles", default_factory=list)
    id: Optional[str] = None
    enabled: bool = fd("Document enabled", default=True)
    use_emulator: bool = fd("Use emulator", default=True)
    use_gams: bool = fd("Use GAMS", default=False)
    file_resource_gams_source: Optional[PlatformFile] = fd("File resource Gams Source", default=None)
    file_resource_input_sample: Optional[PlatformFile] = fd("File resource input sample", default=None)
    file_resource_output_sample: Optional[PlatformFile] = fd("File resource output sample", default=None)

    def __post_init__(self):
        if self.id is None:
            self.id = str(ObjectId())
