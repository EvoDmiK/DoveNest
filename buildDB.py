from imutils.paths import list_files
from gamedb.models import *
import os

ROOT_PATH = os.getcwd()
json_paths = sorted(list_files(f'{ROOT_PATH}/steam/jsons'))

for json_path in json_paths:

    print(json_path)
    appid = json_path.split(os.path.sep)[-2]
    json_path = f'{ROOT_PATH}/steam/{json_path}'
    db = SteamDB(
            appid     = appid,
            json_path = json_path
        )
    db.save()