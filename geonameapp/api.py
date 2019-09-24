# -*- coding: utf-8 -*-
from flask import Flask, request, json, Response
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask_jsonpify import jsonify 

from geonameapp import app 

from itertools import groupby

from copy import deepcopy


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

        response = json.dumps(suggestions,ensure_ascii=False,separators=(",",":"))
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

        response = json.dumps(suggestions,ensure_ascii=False,separators=(",",":"))
        response = Response(response,content_type="application/json; charset=utf-8" )

        return response

class CountryShapes(Resource):
    def get(self):

        conn = geo_db_connect.connect()
        query = conn.execute("""
            SELECT 
                  iso_alpha2
                , iso_numeric 
            FROM 
                geonames.countryinfo
        """)
        numeric_to_alpha = { a[1]: a[0] for a in query.cursor.fetchall() }
        shapes = deepcopy(app.config['COUNTRY_SHAPES'])
        for f in shapes['features']:
            try:
                f['id'] = numeric_to_alpha[int(f['id'])]
            except KeyError as e:
                if f['properties']['name'] == 'Kosovo':
                    f['id'] = 'XK'
                elif f['properties']['name'] == 'Indian Ocean Ter.':
                    f['id'] = 'IO'
                else:
                    del f

        response = json.dumps(shapes,ensure_ascii=False,separators=(",",":"))
        response = Response(response,content_type="application/json; charset=utf-8" )

        return response

class RegionTree(Resource):
    def get(self):

        conn = geo_db_connect.connect()
        query = conn.execute("""
        SELECT 
              parent.geonameid
            , parent.name
            , parent.fcode
            , child.geonameid
            , child.name
            , child.country
            , child.fcode
            , child.latitude
            , child.longitude
        FROM
	    geonames.hierarchy
        JOIN 
            geonames.geoname AS parent ON parent.geonameid = geonames.hierarchy.parentid
        JOIN 
            geonames.geoname AS child ON child.geonameid = geonames.hierarchy.childid
        WHERE 
                child.fcode IN ('RGN','PCLI','TERR','PCLD','PCLX')
            AND parent.fcode IN ('CONT', 'RGN') 
            AND child.fcode != parent.fcode
        ORDER BY 
              parent.name
            , child.name
        """)

        all_stuff = list(query.cursor.fetchall())

        region_to_country = []
        cont_to_region = []
        cont_to_country = []
        for parent in groupby(all_stuff,key=lambda x:x[0]):
            prnt = list(parent)
            children = list(prnt[1])

            this_region_entry = {}
            this_region_entry['geonameid'] = children[0][0]
            this_region_entry['name'] = children[0][1]
            this_country_entry = deepcopy(this_region_entry)

            these_region_children = []
            these_country_children = []
            for child in children:
                if child[6] in ('PCLI','TERR','PCLD','PCLX'):
                    this_child = {
                                'geonameid': child[3],
                                'name': child[4],
                                'country': child[5],
                                'lat': child[7],
                                'lon': child[8],
                            }
                    these_country_children.append(this_child)
                elif child[6] == 'RGN':
                    this_child = {
                                'geonameid': child[3],
                                'name': child[4],
                                }
                    these_region_children.append(this_child)

            this_region_entry['children'] = these_region_children
            this_country_entry['children'] = these_country_children

            if children[0][2] == 'CONT':
                cont_to_country.append(this_country_entry)
                cont_to_region.append(this_region_entry)
            elif children[0][2] == 'RGN':
                region_to_country.append(this_country_entry)

        place_info = {}

        # comment the following part in if you want to return the info to
        # those places too

        #parent_ids = set([ _[0] for _ in all_stuff ])
        #child_ids = set([ _[3] for _ in all_stuff ])

        #all_ids = list(parent_ids | child_ids)

        #conn = geo_db_connect.connect()
        #query = conn.execute("""
        #SELECT DISTINCT 
        #    geoname.geonameid, 
        #    geoname.name, 
        #    country,
        #    countryinfo.name,
        #    geoname.fcode,
        #    featureCodes.name, 
        #    featureCodes.description, 
        #    geoname.population,  
        #    alternatename.alternatename,
        #    alternatename.isoLanguage,
        #    alternatename.isShortName,
        #    alternatename.isPreferredName
        #FROM
        #    geoname
        #JOIN
        #    alternatename ON alternatename.geonameid = geoname.geonameid
        #JOIN 
        #    featureCodes ON featureCodes.code = CONCAT(geoname.fclass,'.',geoname.fcode)
        #LEFT JOIN
        #    countryinfo ON countryinfo.iso_alpha2 = geoname.country
        #WHERE 
        #        geoname.geonameid IN ("""+','.join([str(i) for i in all_ids])+""")
        #    AND
        #        alternatename.isColloquial != 1 # prefer non-colloquial names
        #    AND 
        #        # only show alternatenames in German, English, or original entry
        #        (alternatename.isoLanguage = 'de' OR  alternatename.isoLanguage = 'en' OR alternatename.isoLanguage = '')
        #    # sort 1) for featurecode
        #    #      2) for population
        #    #      3) prefer German then English, then Original
        #    #      4) prefer short names
        #    #      5) Prefer preferred names
        #ORDER BY
	#	  case
	#		when alternatename.isoLanguage = '"""+app.config['ISO_LANGUAGE']+"""' then 0
	#		when alternatename.isoLanguage = 'en' then 1
	#		when alternatename.isoLanguage = '' then 2
	#	  end
	#	, alternatename.isShortName DESC
	#	, alternatename.isPreferredName DESC
        #                     """)

        #    
        #place_info = { i[0]: list(list(i[1])[0]) for i in groupby(query.cursor.fetchall(),key=lambda x:x[0]) }

        response = json.dumps({
                            'regionToCountry': region_to_country,
                            'contToRegion': cont_to_region,
                            'contToCountry': cont_to_country,
                            'placeInfo': place_info,
                        },ensure_ascii=False,separators=(",",":"))

        response = Response(response,content_type="application/json; charset=utf-8" )

        return response

api.add_resource(SearchPlace, '/api/searchplaces')
api.add_resource(SearchCountryOrContinent, '/api/searchcountryregioncontinent')
api.add_resource(CountryShapes, '/api/countryshapes')
api.add_resource(RegionTree, '/api/regiontree')

if __name__ == '__main__':
     #app.run(port='5002')
     a = RegionTree()
     a.get()
