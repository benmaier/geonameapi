import os
import simplejson as json
from pathlib import Path

with (Path.home() / '.geonames' / 'db.json').open('r') as f:
    dbcfg = json.load(f)

with (Path.home() / '.geonames' / 'countries-geo.json').open('r') as f:
    country_shapes = json.load(f)

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GEO_DB = dbcfg
    ISO_LANGUAGE = 'de'
    COUNTRY_SHAPES = country_shapes

if __name__ == "__main__":
    print(dbcfg)
