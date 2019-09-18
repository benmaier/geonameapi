# -*- coding: utf-8 -*-
from flask import Flask, request, json, Response
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask_jsonpify import jsonify 

from geonameapp import app 

from itertools import groupby


geo_db_connect = create_engine('mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(
                                app.config['GEO_DB']['user'],
                                app.config['GEO_DB']['password'],
                                app.config['GEO_DB']['host'],
                                app.config['GEO_DB']['port'],
                                app.config['GEO_DB']['db'],
                            ),
                            )

api = Api(app)

class SearchPlace(Resource):
    def get(self):
        conn = geo_db_connect.connect()
        query = conn.execute("""
        SELECT DISTINCT 
            geoname.geonameid, 
            geoname.name, 
            country,
            countryinfo.name,
            geoname.fcode,
            featureCodes.name, 
            featureCodes.description, 
            geoname.population,  
            alternatename.alternatename,
            alternatename.isoLanguage,
            alternatename.isShortName,
            alternatename.isPreferredName
        FROM
	    (SELECT * FROM alternatename WHERE alternatename LIKE '"""+request.args['string']+"""%%')
	    AS 
                searchresult
        JOIN
            geoname ON searchresult.geonameid = geoname.geonameid
        JOIN
            alternatename ON alternatename.geonameid = geoname.geonameid
        JOIN 
            featureCodes ON featureCodes.code = CONCAT(geoname.fclass,'.',geoname.fcode)
        LEFT JOIN
            countryinfo ON countryinfo.iso_alpha2 = geoname.country
        WHERE 
                alternatename.isColloquial != 1 # prefer non-colloquial names
            AND 
                # only show alternatenames in German, English, or original entry
                (alternatename.isoLanguage = 'de' OR  alternatename.isoLanguage = 'en' OR alternatename.isoLanguage = '')
            # sort 1) for featurecode
            #      2) for population
            #      3) prefer German then English, then Original
            #      4) prefer short names
            #      5) Prefer preferred names
        ORDER BY  case
			when geoname.fcode = 'CONT' then 0.25
			when geoname.fcode = 'PCLI' then 0.5
			when geoname.fcode = 'PPLC' then 1
			when geoname.fcode = 'PPLA' then 1.2
			when geoname.fcode = 'ADM1' then 2
			when geoname.fcode = 'ADM2' then 3
			when geoname.fcode = 'ADM3' then 4
			when geoname.fcode = 'ADM4' then 5
			when geoname.fcode = 'ADM5' then 6
			when geoname.fcode = 'ADM5' then 7
			when geoname.fcode = 'PPL' then 1.5
			else 8
		  end
		, population DESC
		, case
			when alternatename.isoLanguage = '"""+app.config['ISO_LANGUAGE']+"""' then 0
			when alternatename.isoLanguage = 'en' then 1
			when alternatename.isoLanguage = '' then 2
		  end
		, alternatename.isShortName DESC
		, alternatename.isPreferredName DESC
        LIMIT 300
                             """)

        suggestions = [ list(list(i[1])[0]) for i in groupby(query.cursor.fetchall(),key=lambda x:x[0]) ]

        response = json.dumps(suggestions,ensure_ascii=False)
        response = Response(response,content_type="application/json; charset=utf-8" )

        return response

class SearchCountryOrContinent(Resource):
    def get(self):
        conn = geo_db_connect.connect()
        query = conn.execute("""
        SELECT DISTINCT 
            geoname.geonameid, 
            geoname.name, 
            country,
            countryinfo.name,
            geoname.fcode,
            featureCodes.name, 
            featureCodes.description, 
            geoname.population,  
            alternatename.alternatename,
            alternatename.isoLanguage,
            alternatename.isShortName,
            alternatename.isPreferredName
        FROM
	    (SELECT * FROM alternatename WHERE alternatename LIKE '"""+request.args['string']+"""%%')
	    AS 
                searchresult
        JOIN
            geoname ON searchresult.geonameid = geoname.geonameid
        JOIN
            alternatename ON alternatename.geonameid = geoname.geonameid
        JOIN 
            featureCodes ON featureCodes.code = CONCAT(geoname.fclass,'.',geoname.fcode)
        LEFT JOIN
            countryinfo ON countryinfo.iso_alpha2 = geoname.country
        WHERE 
                alternatename.isColloquial != 1
            AND 
                (alternatename.isoLanguage = 'de' OR  alternatename.isoLanguage = 'en' OR alternatename.isoLanguage = '')
            AND
                ( geoname.fcode = 'CONT' OR geoname.fcode = 'PCLI' OR geoname.fcode = 'RGN')
        ORDER BY  
		population DESC
		, case
			when alternatename.isoLanguage = '"""+app.config['ISO_LANGUAGE']+"""' then 0
			when alternatename.isoLanguage = 'en' then 1
			when alternatename.isoLanguage = '' then 2
		  end
		, alternatename.isShortName DESC
		, alternatename.isPreferredName DESC
        LIMIT 300
                             """)

        suggestions = [ list(list(i[1])[0]) for i in groupby(query.cursor.fetchall(),key=lambda x:x[0]) ]

        response = json.dumps(suggestions,ensure_ascii=False)
        response = Response(response,content_type="application/json; charset=utf-8" )

        return response


api.add_resource(SearchPlace, '/api/searchplaces')
api.add_resource(SearchCountryOrContinent, '/api/searchcountryregioncontinent')

if __name__ == '__main__':
     app.run(port='5002')
