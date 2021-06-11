import pandas as pd
import numpy as np
import xlrd
import xlsxwriter
import warnings
import json
import os
warnings.filterwarnings("ignore")

#pd.set_option('display.max_columns',None)

#****************************************************************
# READ IN DATA AND PRE-PROCESS
#--------------------------------------

dir_path = os.path.dirname(os.path.realpath(__file__))
#writer = pd.ExcelWriter(dir_path+'/JSONDATA.xlsx', engine='xlsxwriter')
golf = pd.read_excel(dir_path+'/score_golf_output.xlsx',
                     sheet_name="Courses",dtype=str)


golf['Rating'] = golf['Rating'].replace('No Info','7777777')
golf['Rating'] = round(golf['Rating'].astype(float),2)
golf['Rating'] = golf['Rating'].replace(7777777,np.nan)
golf['Slope'] = golf['Slope'].replace('No Info','7777777')
golf['Slope'] = golf['Slope'].astype(int)
golf['Slope'] = golf['Slope'].replace(7777777,np.nan)
golf['Holes'] = golf['Holes'].replace('No Info','7777777')
golf['Holes'] = round(golf['Holes'].astype(int),0)
golf['Holes'] = golf['Holes'].replace(7777777,np.nan)
golf['Q1 2021 Population'] = golf['Q1 2021 Population'].astype(int)
golf['Land Area (km2)'] = golf['Land Area (km2)'].astype(int)



#*************************************************************************
# CREATE DATA FOR MAP SHOWING VARIOUS METRICS
#---------------------------------------------------

prov_stats = golf.groupby('Province Short').agg({'Rating': ['mean'],'Slope': ['mean'],'Course': ['count'],'Holes': ['sum'],'Q1 2021 Population': ['median'],'Land Area (km2)':['median']}).reset_index()
prov_stats = prov_stats.droplevel(1,axis=1)

prov_stats['Courses per Person'] = prov_stats['Course']/prov_stats['Q1 2021 Population']
prov_stats['Holes per Person'] = prov_stats['Holes']/prov_stats['Q1 2021 Population']
prov_stats['Courses per km2'] = prov_stats['Course']/prov_stats['Land Area (km2)']
prov_stats['Holes per km2'] = prov_stats['Holes']/prov_stats['Land Area (km2)']
print(prov_stats)

alldata = ''
for index,row in prov_stats.iterrows():

    prov_short = row['Province Short']
    temp = golf[golf['Province Short'] == prov_short]
    prov = temp['Province'].iat[0]
    map_id = temp['Map ID'].iat[0]
    rating = row['Rating']
    slope = row['Slope']
    course_count = row['Course']
    hole_count = row['Holes']
    popn = row['Q1 2021 Population']
    area = row['Land Area (km2)']
    crs_p_person = row['Courses per Person']
    hls_p_person = row['Holes per Person']
    crs_p_km2 = row['Courses per km2']
    hls_p_km2 = row['Holes per km2']

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
            "population": popn,
            "area": area,
            "crs_p_person": crs_p_person,
            "hls_p_person": hls_p_person,
            "crs_p_km2": crs_p_km2,
            "hls_p_km2": hls_p_km2
        }, file, indent=4)
    file.close()

    # Re-open each file in read mode and store all text in one variable
    reader = open(dir_path+'/json/map_data.json','r')
    text = reader.read()
    # Combine text from all institutions that are ranked in the current subject
    alldata = alldata + text
    reader.close()

# Write newly combined json file out
alldata_file = open(dir_path+'/json/map_data.json', 'w')
alldata = alldata.replace("}{","},{")
alldata = '['+alldata+']'
alldata_file.write(alldata)
alldata_file.close()
     

        
#*************************************************************************
# CREATE DATA FOR DOT GRAPH AND TABLE SHOWING ALL COURSES IN EACH PROVINCE
#---------------------------------------------------

prov_dict = {"AB":1,"BC":2,"MB":3,"NB":4,"NL":5,"NT":6,"NS":7,"NU":8,"ON":9,"PE":10,"QC":11,"SK":12,"YT":13}
prov_dict_r = {"AB":13,"BC":12,"MB":11,"NB":10,"NL":9,"NT":8,"NS":7,"NU":6,"ON":5,"PE":4,"QC":3,"SK":2,"YT":1}

alldata = ''
for index,row in golf.iterrows():

    course = row['Course']
    prov = row['Province']
    prov_short = row['Province Short']
    prov_code = prov_dict_r.get(prov_short)
    region = row['Region']
    access = row['Access']
    par = row['Par']
    yards = row['Yards']
    access = row['Access']
    rating = row['Rating']
    slope = row['Slope']
    stars = row['Star Rating']
            
    # Create intial JSON structure for the current subject
    with open(dir_path+'/json/bubble_data.json','w') as file:
        json.dump({
            "course": course,
            "province": prov,
            "region": region,
            "p_id": prov_code,
            "access": access,
            "par": par,
            "yards": yards,
            "slope": slope,
            "rating": rating,
            "stars": stars,
        }, file, indent=4)
    file.close()

    # Re-open each file in read mode and store all text in one variable
    reader = open(dir_path+'/json/bubble_data.json','r')
    text = reader.read()
    # Combine text from all institutions that are ranked in the current subject
    alldata = alldata + text
    reader.close()

# Write newly combined json file out
alldata_file = open(dir_path+'/json/bubble_data.json', 'w')
alldata = alldata.replace("}{","},{")
alldata = '['+alldata+']'
alldata_file.write(alldata)
alldata_file.close()


