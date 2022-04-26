#!/bin/python3
import os
import re
import json
import pandas as pd
import requests
import sqlite3
import time
import numpy as np
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify,send_file
import urllib.parse
from app_secrets import *
import voyages_geo_to_geojson_points_dict as vd

app = Flask(__name__,template_folder='./templates/')
app.config.from_object(__name__)

def sum_of_embarked_by_region():
	r=requests.options(base_url+'voyage/?hierarchical=False',headers=headers)
	md=json.loads(r.text)
	gd=vd.main()
	
	groupby_fields=[
		'voyage_itinerary__imp_principal_place_of_slave_purchase__region__value',
		'voyage_itinerary__imp_principal_port_slave_dis__region__value'
	]
	
	data={
		'groupby_fields':groupby_fields,
		'value_field_tuple':['voyage_slaves_numbers__imp_total_num_slaves_embarked','sum'],
		'cachename':['voyage_maps']
	}
	
	r=requests.post(url=base_url+'voyage/groupby',headers=headers,data=data)
	j=json.loads(r.text)
	
	featurecollection={"type":"FeatureCollection","features":[]}
	for source in j:
		for target in j[source]:
			#print(source,target,j[source][target])
			tv=int(eval(target))
			sv=int(eval(source))
			v=j[source][target]
			if pd.isna(v):
				v=0
		
			if v!=0:
				s_lon,s_lat=gd[sv]['geometry']['coordinates']
				t_lon,t_lat=gd[tv]['geometry']['coordinates']
				featurecollection['features'].append({
					"type":"Feature",
					"geometry":{
						"type":"LineString",
						"coordinates":[[s_lon,s_lat],[t_lon,t_lat]]
					},
					"properties":{"Value":np.log(v)}
				})
	
	return featurecollection

@app.route('/', methods=['GET'])
def login():
	return render_template('index.html')

@app.route('/get_map/')
def get_map():
	linestrings=sum_of_embarked_by_region()
	return jsonify(linestrings)

if __name__ == "__main__":
	app.run(host='0.0.0.0')
