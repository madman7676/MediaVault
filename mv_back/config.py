import os
import platform

MOVIES_PATHS = ["E:\\Media\\Movies", "D:\\KiHoXa\\Movies", "F:\\Movies"]
SERIES_PATHS = ["E:\\Media\\Serials", "D:\\KiHoXa\\Serials", "F:\\Serials"]
METADATA_FILE = "metadata.json"
BASE_URL = "http://localhost:5000"
THUMBNAILS_DIR = "thumbnails"
DB_CONNECTION_STRING = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\MSSQLSERVER06;DATABASE=MediaVault;Trusted_Connection=yes'

def to_long_path(p: str) -> str:
    if not p:
        return p
    if platform.system() != "Windows":
        return p
    p_abs = os.path.abspath(p)
    if p_abs.startswith(r'\\\\?\\') or p_abs.startswith(r'\\\\.\\'):
        return p_abs
    if p_abs.startswith(r'\\\\'):
        return r'\\\\?\\UNC\\' + p_abs.lstrip(r'\\')
    return r'\\\\?\\' + p_abs