# -*- coding: utf-8 -*-
import geopandas as gpd
import fiona
import pandas as pd
import urllib.request
import warnings
import zipfile
from datetime import date
from os.path import exists
import os
warnings.simplefilter("ignore")

fiona.drvsupport.supported_drivers['kml'] = 'rw' # enable KML support which is disabled by default
fiona.drvsupport.supported_drivers['KML'] = 'rw' # enable KML support which is disabled by default

os.chdir("docs/data")
# https://grandicarnivori.provincia.tn.it/Comunicazione/MAPPA-ORSI-RADIOCOLLARATI
url_kmz = "https://www.google.com/maps/d/u/0/kml?mid=1I2AwqVdHwkiRrQeFHHf5A1IoCioVd9TQ&lid=sAvnhrZ7S-0&nl=1"
geojson_grid = "griglia3km.geojson"
kmz = "dati_orsi.kmz"
doc = "doc.kml"
datafile = "spostamenti_orsi.csv"
today = date.today()
today = today.strftime("%Y%m%d")
df_orsi = pd.read_csv(datafile)

def getIdArea(p):
    idarea = p.split("id: ")[1].split("<br>")[0]
    return(idarea)

if str(df_orsi.day.max()) != today:
    out = urllib.request.urlretrieve(url_kmz, kmz)
    z = zipfile.ZipFile(kmz)
    z.extractall()
    lines = []
    with open(doc) as f:
        lines = f.readlines()
    url_kml = ""
    for line in lines:
        if line.find("CDATA") > 0:
            url_kml = line.split("[")[2].split("]")[0]
    kml = gpd.read_file(url_kml)
    kml['idarea'] = kml.Description.apply(getIdArea)
    file_exists = exists(geojson_grid)
    if file_exists == False:
        kml[['geometry', 'idarea']].to_file(geojson_grid, driver='GeoJSON')
    orsi = []
    for name in kml.Name.unique():
        if len(name) > 0:
            idarea = kml[kml.Name == name].idarea.values[0]
            orso = {'idarea': idarea, 'name': name, 'day': today}
            orsi.append(orso)
    orsi_df = pd.DataFrame(orsi)
    df_orsi = df_orsi.append(orsi_df)
    df_orsi.to_csv(datafile, index=False)
