# geonameapi

A small webserver that searches for populated places on earth by sending requests to a geoname database.

![example](https://raw.githubusercontent.com/benmaier/geonameapi/master/img/example.png)


## Prerequisites

First, you need to copy the geoname database to your own mysql-server. Clone this [adapted GeonameSQL-Importer](https://github.com/benmaier/GeoNames-MySQL-DataImport) and follow the instructions therein.

Afterwards, add a config-file containing information about the database to your home directory. It must have the path

```
~/.geonames/db.json
```

and a structure equivalent to

```json
{
    "host": "serveraddress",
    "port": 3306,
    "user": "your_user",
    "passwd": "your_password_string",
    "dbname": "geonames"
}
```

## Install

Activate the environment first

```bash
source env/bin/activate
```

Then run

```bash
pip install -r requirements.text
```

## Run

Activate the environment first

```bash
source env/bin/activate
```

Then run the app

```bash
FLASK_APP=geonameapi.py flask run
```


