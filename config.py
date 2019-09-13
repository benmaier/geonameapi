import os
import simplejson as json
from pathlib import Path

with (Path.home() / '.geonames' / 'db.json').open('r') as f:
    dbcfg = json.load(f)

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GEO_DB = dbcfg

if __name__ == "__main__":
    print(dbcfg)
