import pydoc
from datetime import datetime
from config import *

def get_metadata(conn):
    cursor = conn.cursor()
    