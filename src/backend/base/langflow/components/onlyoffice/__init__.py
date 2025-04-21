from .docspace_auth_basic_auth import OnlyofficeDocspaceBasicAuthentication
from .docspace_files_create import OnlyofficeDocspaceCreateFile
from .docspace_files_delete_file import OnlyofficeDocspaceDeleteFile
from .docspace_files_download_as_text import OnlyofficeDocspaceDownloadAsText
from .docspace_files_get_file import OnlyofficeDocspaceGetFile
from .docspace_files_list_operations import OnlyofficeDocspaceListOperations
from .docspace_files_start_deleting_file import OnlyofficeDocspaceStartDeletingFile
from .docspace_files_update_file import OnlyofficeDocspaceUpdateFile
from .docspace_files_wait_operation import OnlyofficeDocspaceWaitOperation
from .docspace_folders_create_folder import OnlyofficeDocspaceCreateFolder
from .docspace_folders_delete_folder import OnlyofficeDocspaceDeleteFolder
from .docspace_folders_get_folder import OnlyofficeDocspaceGetFolder
from .docspace_folders_list_my import OnlyofficeDocspaceListMy
from .docspace_folders_list_subfolders import OnlyofficeDocspaceListSubfolders
from .docspace_folders_update_folder import OnlyofficeDocspaceUpdateFolder
from .docspace_http_request import OnlyofficeDocspaceHttpRequest
from .docspace_rooms_archive_room import OnlyofficeDocspaceArchiveRoom
from .docspace_rooms_create_room import OnlyofficeDocspaceCreateRoom
from .docspace_rooms_get_room import OnlyofficeDocspaceGetRoom
from .docspace_rooms_list_rooms import OnlyofficeDocspaceListRooms
from .docspace_rooms_update_room import OnlyofficeDocspaceUpdateRoom

__all__ = [
    "OnlyofficeDocspaceArchiveRoom",
    "OnlyofficeDocspaceBasicAuthentication",
    "OnlyofficeDocspaceCreateFile",
    "OnlyofficeDocspaceCreateFolder",
    "OnlyofficeDocspaceCreateRoom",
    "OnlyofficeDocspaceDeleteFile",
    "OnlyofficeDocspaceDeleteFolder",
    "OnlyofficeDocspaceDownloadAsText",
    "OnlyofficeDocspaceGetFile",
    "OnlyofficeDocspaceGetFolder",
    "OnlyofficeDocspaceGetRoom",
    "OnlyofficeDocspaceHttpRequest",
    "OnlyofficeDocspaceListMy",
    "OnlyofficeDocspaceListOperations",
    "OnlyofficeDocspaceListRooms",
    "OnlyofficeDocspaceListSubfolders",
    "OnlyofficeDocspaceStartDeletingFile",
    "OnlyofficeDocspaceUpdateFile",
    "OnlyofficeDocspaceUpdateFolder",
    "OnlyofficeDocspaceUpdateRoom",
    "OnlyofficeDocspaceWaitOperation",
]
