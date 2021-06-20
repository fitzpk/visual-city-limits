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

"""
Data Dictionary for Broadband data
-----------------------------+---------------------------------------------------------------------
Field                        | Description
-----------------------------+---------------------------------------------------------------------
HEXuid_HEXidu                | Unique identifier for the hexagon
SumPop_2016_SommePop         | Estimated population within the hexagon in summing PHH related data
SumURD_2016_SommeRH          | Estimated private dwellings occupied by usual residents within the
                             |   hexagon in summing related PHH data
SumTD_2016_SommeTL           | Estimated total private dwellings within the hexagon in summing
                             |   related PHH data
Avail_5_1_75PctPlus_Dispo    | Where more than 75% of total private dwellings within the hexagon
                             |   have access to broadband services offering 5/1 Mbps or greater
Avail_50_10_Gradient_Dispo   | Percentage range assigned using Avail_50_10_Pct_Dispo in order to
                             |   assign mappable grades.
"""


#****************************************************************
# READ IN DATA AND PRE-PROCESS
#--------------------------------------

dir_path = os.path.dirname(os.path.realpath(__file__))

# Hex center nodes
hex_centers = pd.read_csv(dir_path+'/CHX_EXO.csv')
#hex_centers = hex_centers.head(10)
#print(hex_centers)

# Broadband internet data based on hexagons
hex_internet = pd.read_csv(dir_path+'/BROADBAND_HEX.csv')

for col in hex_internet:
    print(hex_internet[col].unique())
    print(hex_internet[col].value_counts())

#****************************************************************
# FUNCTION TO PROCESS DATA WITH OPTION TO CREATE SEPARATE FILES FOR EACH PROVINCE
#--------------------------------------

def create_json(output_path,hexs,hex_values,prov_slice):

    if prov_slice == True:
        hexs['province'] = hexs['HEXuid_HEXidu'].str[:2]
        provs = hexs['province'].unique()
    else:
        provs = ['allprovs']
        
    for p in provs:
        if prov_slice == True:
            prov_hex = hexs[hexs['province'] == p]
        else:
            prov_hex = hexs
        alldata=''
        for index,row in prov_hex.iterrows():

            hex_internet = hex_values[hex_values['HEXuid_HEXidu'] == row['HEXuid_HEXidu']]
            # If there is no data for a particular hexagon then simply do not create a row in the json
            # note: this is done to mitigate the size of the json file and improve amcharts performance

            if len(hex_internet) == 0:
                bbaccess = '0'
            else:
                popul = hex_internet['SumPop_2016_SommePop'].iat[0]
                dwell_ur = hex_internet['SumURD_2016_SommeRH'].iat[0]
                dwell = hex_internet['SumTD_2016_SommeTL'].iat[0]
                bbaccess = hex_internet['Avail_50_10_Gradient_Dispo'].iat[0]

            if bbaccess == '0':
                pass
            else:
                province = row['HEXuid_HEXidu'][:2]

                lat = row['latitude']
                lon = row['longitude']

                color_dict = {">0% - 25%":"#ffffb2",">25% - 50%":"#fecc5c",">50% - 75%":"#fd8d3c",">75% -  100%":"#e31a1c"}
                color = color_dict.get(bbaccess)
                
                # Create intial JSON structure for the current subject
                # Note: I have kept fields to only the necessary ones to limit file size
                with open(output_path+'/json/hex_data_points_'+p+'.json','w') as file:
                    dump = {"latitude": row['latitude'],
                            "longitude": row['longitude'],
                            "color": color}
                    json.dump(dump, file, indent=4)
                file.close()

                # Re-open each file in read mode and store all text in one variable
                reader = open(output_path+'/json/hex_data_points_'+p+'.json','r')
                text = reader.read()
                text = text.replace('NaN','null')
                # Combine text from all institutions that are ranked in the current subject
                alldata = alldata + text
                reader.close()

        # Write newly combined json file out
        alldata_file = open(output_path+'/json/hex_data_points_'+p+'.json', 'w')
        alldata = alldata.replace("}{","},{")
        #alldata = "hexs='["+alldata+"]';"
        alldata = '['+alldata+']'
        alldata_file.write(alldata)
        alldata_file.close()

create_json(dir_path,hex_centers,hex_internet,True)
create_json(dir_path,hex_centers,hex_internet,False)
