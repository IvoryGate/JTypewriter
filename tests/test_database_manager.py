import os
from core import DatabaseManager as DM

def test_is_path_exist():
    path = DM.DatabaseManger.DATABASE_PATH
    assert os.path.exists(path) == True