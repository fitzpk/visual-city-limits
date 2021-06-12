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

def nanCheck(in_data):
    if math.isnan(in_data) == True:
        output = in_data
    else:
        output = int(in_data)
    return output
    

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
golf['Yards'] = golf['Yards'].replace('No Info','7777777')
golf['Yards'] = round(golf['Yards'].astype(int),0)
golf['Yards'] = golf['Yards'].replace(7777777,np.nan)
golf['Q1 2021 Population'] = golf['Q1 2021 Population'].astype(int)
golf['Land Area (km2)'] = golf['Land Area (km2)'].astype(int)



#*************************************************************************
# CREATE DATA FOR MAP SHOWING VARIOUS METRICS
#---------------------------------------------------

# Calculate summary stats from source data
prov_stats = golf.groupby('Province Short').agg({'Rating': ['mean'],'Slope': ['mean'],'Course': ['count'],'Holes': ['sum'],'Yards': ['sum'],'Q1 2021 Population': ['median'],'Land Area (km2)':['median']}).reset_index()
prov_stats = prov_stats.droplevel(1,axis=1)

# Calculate extra provincial stats using population and land area
prov_stats['Courses per Person'] = prov_stats['Course']/prov_stats['Q1 2021 Population']
prov_stats['Holes per Person'] = prov_stats['Holes']/prov_stats['Q1 2021 Population']
prov_stats['Courses per km2'] = prov_stats['Course']/prov_stats['Land Area (km2)']
prov_stats['Holes per km2'] = prov_stats['Holes']/prov_stats['Land Area (km2)']

# Calculate accessibility proportions for each province
access_perc = round(golf.groupby('Province Short')['Access'].value_counts(normalize=True) * 100,1)
access_perc = pd.DataFrame(access_perc.reset_index(name='%'))
# Make things a bit easier by finding the % of private courses and then have the remainder represent public courses
private = access_perc[access_perc['Access'] == 'Private']
private['Public %'] = 100-private['%']
provs = ["AB","BC","MB","NB","NL","NT","NS","ON","PE","QC","SK","YT"]
for p in provs:
    if p not in private['Province Short'].unique():
        private = private.append(pd.DataFrame({"Province Short":[p],"Access":["Private"],"%":[0],"Public %":[100]}))
private['Access Label'] = private['%'].map(str)+'% Private | '+private['Public %'].map(str)+'% Public'
access_dict = dict(zip(private['Province Short'],private['Access Label']))
prov_stats["Access Label"] = prov_stats['Province Short'].map(access_dict)

print(private)

# Add in a nunavut because it had no data
nunavut = pd.DataFrame({
    'Province Short': ['NU'],
    'Rating': [np.nan],
    'Slope': [np.nan],
    'Course': [np.nan],
    'Holes': [np.nan],
    'Yards': [np.nan],
    'Q1 2021 Population': [39407],
    'Land Area (km2)': [1936113],
    'Courses per Person': [np.nan],
    'Holes per Person': [np.nan],
    'Courses per km2': [np.nan],
    'Holes per km2': [np.nan],
    'Access Label': ['No Courses'],
    })
prov_stats = prov_stats.append(nunavut)

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
     

        
#*************************************************************************
# CREATE DATA FOR DOT GRAPH AND TABLE SHOWING ALL COURSES IN EACH PROVINCE
#---------------------------------------------------

prov_dict_r = {"AB":13,"BC":12,"MB":11,"NB":10,"NL":9,"NS":8,"NT":7,"NU":6,"ON":5,"PE":4,"QC":3,"SK":2,"YT":1}

def jitterbug(in_data):
    jitter = np.random.uniform(-0.15,0.15)
    output = in_data+jitter
    return output


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
    y_jitter = jitterbug(prov_code)
            
    # Create intial JSON structure for the current subject
    with open(dir_path+'/json/bubble_data.json','w') as file:
        json.dump({
            "course": course,
            "province": prov,
            "prov_short": prov_short,
            "region": region,
            "p_id": prov_code,
            "y_jitter": y_jitter,
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
    text = text.replace('NaN','null')
    # Combine text from all institutions that are ranked in the current subject
    alldata = alldata + text
    reader.close()

# Write newly combined json file out
alldata_file = open(dir_path+'/json/bubble_data.json', 'w')
alldata = alldata.replace("}{","},{")
alldata = '['+alldata+']'
alldata_file.write(alldata)
alldata_file.close()


