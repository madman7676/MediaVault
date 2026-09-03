from pathlib import Path
BASE_DIR = Path(__file__).parent

MOVIES_PATHS = ["E:\\Media\\Movies", "D:\\KiHoXa\\Movies", "F:\\Movies"]
SERIES_PATHS = ["E:\\Media\\Serials", "D:\\KiHoXa\\Serials", "F:\\Serials"]
BASE_URL = "http://localhost:5000"
DB_CONNECTION_STRING = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\MSSQLSERVER06;DATABASE=MediaVault;Trusted_Connection=yes'

METADATA_FILE = BASE_DIR / "metadata.json"
THUMBNAILS_DIR = BASE_DIR / "thumbnails"