import pandas as pd
import numpy as np
import xlrd
import xlsxwriter
import warnings
import json
import os
import math
warnings.filterwarnings("ignore")
#pd.set_option('display.max_columns',None)

    

#****************************************************************
# READ IN DATA AND PRE-PROCESS
#--------------------------------------

dir_path = os.path.dirname(os.path.realpath(__file__))
hex_centers = pd.read_csv(dir_path+'/CHX_EXO.csv')
hex_centers = hex_centers.head(10)
print(hex_centers)

alldata=''
for index,row in hex_centers.iterrows():

    province = row['HEXuid_HEXidu'][:2]

    top_v_lat = row['latitude']+0.05156499999999653
    top_v_lon = row['longitude']

    topR_v_lat = row['latitude']+0.025996999999996717
    topR_v_lon = row['longitude']+0.060279999999991674

    botR_v_lat = row['latitude']-0.025996999999996717
    botR_v_lon = row['longitude']+0.060279999999991674

    bot_v_lat = row['latitude']-0.05156499999999653
    bot_v_lon = row['longitude']

    botL_v_lat = row['latitude']-0.025996999999996717
    botL_v_lon = row['longitude']-0.060279999999991674

    topL_v_lat = row['latitude']+0.025996999999996717
    topL_v_lon = row['longitude']-0.060279999999991674

    # Create intial JSON structure for the current subject
    with open(dir_path+'/json/hex_data.json','w') as file:
        dump = {"province":province,
                "hex_id": row['HEXuid_HEXidu'],
                "geoPolygon":[[{"latitude":top_v_lat,"longitude":top_v_lon},
                {"latitude":topR_v_lat,"longitude":topR_v_lon},
                {"latitude":botR_v_lat,"longitude":botR_v_lon},
                {"latitude":bot_v_lat,"longitude":bot_v_lon},
                {"latitude":botL_v_lat,"longitude":botL_v_lon},
                {"latitude":topL_v_lat,"longitude":topL_v_lon},
                {"latitude":top_v_lat,"longitude":top_v_lon}]]}
        json.dump(dump, file, indent=4)
    file.close()

    # Re-open each file in read mode and store all text in one variable
    reader = open(dir_path+'/json/hex_data.json','r')
    text = reader.read()
    # Combine text from all institutions that are ranked in the current subject
    alldata = alldata + text
    reader.close()

# Write newly combined json file out
alldata_file = open(dir_path+'/json/hex_data.json', 'w')
alldata = alldata.replace("}{","},{")
alldata = '['+alldata+']'
alldata_file.write(alldata)
alldata_file.close()



"""
print("Top Vertice","Lat.",top_v_lat,"Long.",top_v_lon)
print("Top Right Vertice","Lat.",topR_v_lat,"Long.",topR_v_lon)
print("Bottom Right Vertice","Lat.",botR_v_lat,"Long.",botR_v_lon)
print("Bottom Vertice","Lat.",bot_v_lat,"Long.",bot_v_lon)
print("Bottom Left Vertice","Lat.",botL_v_lat,"Long.",botL_v_lon)
print("Top Left Vertice","Lat.",topL_v_lat,"Long.",topL_v_lon)

# Pre-sort data by rating because this is the default field in the dashboard app
prov_stats = prov_stats.sort_values(by='Rating')

print(prov_stats)

alldata = ''
for index,row in prov_stats.iterrows():

    prov_short = row['Province Short']
    if prov_short == 'NU':
        prov = 'Nunavut'
        map_id = 'CA-NU'
        
    else:
        temp = golf[golf['Province Short'] == prov_short]
        prov = temp['Province'].iat[0]
        map_id = temp['Map ID'].iat[0]
        
    rating = round(row['Rating'],1)
    slope = nanCheck(row['Slope'])
    course_count = nanCheck(row['Course'])
    hole_count = nanCheck(row['Holes'])
    yards = nanCheck(row['Yards'])
    popn = row['Q1 2021 Population']
    area = row['Land Area (km2)']
    crs_p_cap = round(row['Courses per Person']*100000,2)
    hls_p_cap = round(row['Holes per Person']*100000,2)
    crs_p_thouskm2 = round(row['Courses per km2']*1000,2)
    hls_p_thouskm2 = round(row['Holes per km2']*1000,2)
    access = row['Access Label']

    # Create intial JSON structure for the current subject
    with open(dir_path+'/json/map_data.json','w') as file:
        json.dump({
            "id": map_id,
            "province": prov,
            "prov_short": prov_short,
            "slope": slope,
            "rating": rating,
            "course_count": course_count,
            "hole_count": hole_count,
            "yards": yards,
            "population": popn,
            "area": area,
            "crs_p_person": crs_p_cap,
            "hls_p_person": hls_p_cap,
            "crs_p_km2": crs_p_thouskm2,
            "hls_p_km2": hls_p_thouskm2,
            "access": access,
        }, file, indent=4)
    file.close()

    # Re-open each file in read mode and store all text in one variable
    reader = open(dir_path+'/json/map_data.json','r')
    text = reader.read()
    text = text.replace('NaN','null')
    # Combine text from all institutions that are ranked in the current subject
    alldata = alldata + text
    reader.close()

# Write newly combined json file out
alldata_file = open(dir_path+'/json/map_data.json', 'w')
alldata = alldata.replace("}{","},{")
alldata = '['+alldata+']'
alldata_file.write(alldata)
alldata_file.close()
"""
     
