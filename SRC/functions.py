import pandas as pd
import requests
import math
from pymongo import MongoClient
import os
from geopandas import GeoDataFrame, points_from_xy
from dotenv import load_dotenv
load_dotenv()

'''Conect to Mongo database and collection'''
def connectMongo(collection):
    client = MongoClient("mongodb://localhost/companies")
    db = client.get_database()
    coll = db[collection]
    return db, coll

def CleanDataFrame(df, col):
    df = df.explode(col)
    dfexpandedData = df[[col]].apply(lambda r: r[col], result_type="expand", axis=1)
    cleanData = pd.concat([df,dfexpandedData], axis=1)
    return cleanData

'''creates locations in geojson format'''
def asGeoJSON(long,lat):
    try:
        location = {'type':'Point',
            'coordinates':[float(long), float(lat)]}
        return location
    except:
        return None 

''' replace the location (geoson format) in a collection '''
def insertGeoLocation(long,lat,collection,i):
    geocode = {"$set": {'location':asGeoJSON(long,lat)}}
    collection.update_one(i,geocode)

''' Creates the geoquery '''
def WithgeoQuery(location, maxDistance=10000, minDistance=0, field="location"):
    return {
       field: {
         "$near": {
           "$geometry": location,
           "$maxDistance": maxDistance,
           "$minDistance": minDistance
         }
       }
    }
def geoQuery(collection, location):
    query = WithgeoQuery(location)
    result = collection.find(query).limit(1)
    return list(result)

''' Make a request to google API and return it in a json fomat ''' 
def authotization():
    token = os.getenv("API_KEY")
    if not token:
        raise ValueError("You must set an APIKEY token")
    return token

def googleApi(query, pagetoken=None):
    google_api_key = authotization()
    url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?{query}'
    print(url)
    if pagetoken:
        url += f'&pagetoken={pagetoken}'
        print('pagetoken')
    res = requests.get(url+f'&key={google_api_key}')
    return res

''' Remove rows which does not fullfil the requirements ''' 
def nonempty(df):
    return len(df)>0


def near_place(df, radius, keyword,coll,lista): 
    for e,row in df.iterrows():
        dic = {}
        location = f"{row['location']['coordinates'][1]},{row['location']['coordinates'][0]}"
        query = f"location={location}&radius={radius}&keyword={keyword}"
        data = googleApi(query).json()
        if data['status']=='OK':
            dic['id']=row['_id']
            lat=data['results'][0]['geometry']['location']['lat']
            long=data['results'][0]['geometry']['location']['lng']
            dic['location']= asGeoJSON(long,lat)
            dic['name']= data['results'][0]['name']
            lista.append(dic)
            coll.insert_one(dic)
    return lista

''' Haversine distance ''' 
def haversine(lat1, lon1, lat2, lon2):
    rad=math.pi/180
    dlat=lat2 -lat1
    dlon=lon2-lon1
    R=6372.795477598
    a=(math.sin(rad*dlat/2))**2 + math.cos(rad*lat1)*math.cos(rad*lat2)*(math.sin(rad*dlon/2))**2
    distancia=2*R*math.asin(math.sqrt(a))
    return distancia 

''' Ponderate the distances accordying to the company preferences '''
def ponderation(rate,distance):
    return round(distance*5/rate,2)

''' Obtain coordinates in each collection to map it ''' 
def checkcoordinates(collection):
    return list(collection.find({"location.coordinates":{"$exists":True}}))

def createGeo(collection):
    c = checkcoordinates(collection)
    df= pd.DataFrame(c)
    df = df[['location']].apply(lambda r: r['location'], result_type="expand", axis=1)
    df['lng'] = df.apply(lambda row: row['coordinates'][0], axis=1)
    df['lat'] = df.apply(lambda row: row['coordinates'][1], axis=1)
    layer = GeoDataFrame(df, geometry=points_from_xy(df['lng'], df['lat']))
    return layer

def map(collection, col):
    c =list(collection.find({f"{col}.coordinates":{"$exists":True}}))
    df= pd.DataFrame(c)
    df = df[[col]].apply(lambda r: r[col], result_type="expand", axis=1)
    df['lng'] = df.apply(lambda row: row['coordinates'][0], axis=1)
    df['lat'] = df.apply(lambda row: row['coordinates'][1], axis=1)
    return df 
