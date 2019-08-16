#import pandas as pd
#import numpy as np
#import re
#import matplotlib.pyplot as plot
from flask import Flask
from flask import request,jsonify,Response
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
import json
import os
import datetime
from math_logic import *


global year_dfs
year_dfs= []

app = Flask(__name__)
api = Api(app,
          default="CEC Rest API",  # Default namespace
          title="CEC Tool Rest API by GSES",  # Documentation Title
          description="CEC Solar Data Tool. Description goes here"
          # Documentation Description
          )
if os.environ.get('HTTPS'):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        return url_for(self.endpoint('specs'), _external=True, _scheme='https')


 
    api.specs_url = specs_url


input_model = api.model('input_data', {
    'latitude': fields.Float,
    'longitude': fields.Float,
    'interval': fields.Float,
    'tilt_1': fields.Float,
    'azimuth_1': fields.Float,
    'tilt_2': fields.Float,
    'azimuth_2': fields.Float,
    'tilt_3': fields.Float,
    'azimuth_3': fields.Float,
    
})

@api.route('/data')
class SolarRadiationData(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Get the required data for all months for given params")
    @api.expect(input_model)
    #@api.marshal_with(day_data, as_list=True)
    def post(self):
        user_input = request.json
        print("User inputs")
        print(user_input)
        try:
            latitude = round(user_input['latitude'],1)
            longitude = round(user_input['longitude'],2)
            latitude_offset = round((abs(latitude) -10.1)*10)
            print(f"Data recieved: long: {longitude} lat: {latitude} recieved ")
            print(f"Data calculated: offset=> {latitude_offset}")
            months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            global_solar_irr_data =[]
            # global year_dfs
            for i in months:
                print(f"reading excel for solar data in month {i}")
                month_df = pd.read_excel(f"Datasets/Solar {i}.xlsx")
                print(f"file read: Datasets/Solar {i}.xlsx")            
                month_df.round(1)
                month_df.set_index('Unnamed: 0',inplace=True)
                print(f"fetched dataframe for the month {i}")
                #print(f"About to fetch data from long {longitude} and at offset {latitude_offset}")
                solar_data = month_df[longitude].iloc[latitude_offset]
                print(f"Solar data fetched is ==> { round(solar_data,2) }")
                global_solar_irr_data.append(round(solar_data,2))

            print(f" Computing Solar Radiation with data fetched....")
            test_data = getjsondata(global_irr_data=global_solar_irr_data,lat=latitude,time_int=int(user_input['interval']))
            #test_data = getjsondata() #default args
            test_data['Time interval'] = test_data['Time interval'].apply(lambda x: str(x)[-8:])
            resp = Response(response=test_data.to_json( orient='index'),status=200,mimetype="application/json")
            return (resp)
        except Exception as e:
            print(e)
            print("Ran into error. returning with default configs")
            test_data = getjsondata()
            resp = Response(response=test_data.to_json( orient='index'),status=200,mimetype="application/json")
            return (resp)

        


if __name__ == '__main__':
    # run the application

    port = int(os.environ.get('PORT', 33507)) 
    app.run(host='0.0.0.0', port=port)
    #app.run(debug=True, port='7000')

'''
#output model. not coming up on schema yet
day_data = api.model('day_data', {
    '6:00':'float',
    '7:00':'float',
    '8:00':'float',
    '9:00':'float',
    '10:00':'float',
    '11:00':'float',
    '12:00':'float',
    '13:00':'float',
    '14:00':'float',
    '15:00':'float',
    '16:00':'float',
    '17:00':'float',
    '18:00':'float'
})

month_data = day_data = api.model('month_data', {
    'required': ['day_data'],
    'Jan': {
            '$ref': '#/definitions/day_data',
    },
    'Feb': {
            '$ref': '#/definitions/day_data',
    },
    'Mar': {
            '$ref': '#/definitions/day_data',
    },
    'Apr': {
            '$ref': '#/definitions/day_data',
    },
    'May': {
            '$ref': '#/definitions/day_data',
    },
    'Jun': {
            '$ref': '#/definitions/day_data',
    },
    'Jul': {
            '$ref': '#/definitions/day_data',
    },
    'Aug': {
            '$ref': '#/definitions/day_data',
    },
    'Sep': {
            '$ref': '#/definitions/day_data',
    },
    'Oct': {
            '$ref': '#/definitions/day_data',
    },
    'Nov': {
            '$ref': '#/definitions/day_data',
    },
    'Dec': {
            '$ref': '#/definitions/day_data',
    }
})

'''