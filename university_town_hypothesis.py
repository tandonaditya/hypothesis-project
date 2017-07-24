import re
import pandas as pd
import numpy as np
from scipy import stats

def get_city_allhomes_data():
    czah = pd.read_csv('City_Zhvi_AllHomes.csv')
    states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
    czah.replace({'State' : states}, inplace =True)
    return czah


'''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list.'''
    
def get_list_of_university_towns():
    unitown = open('university_towns.txt', 'r')
    state_uni = list() 
    for line in unitown:
        state_change = 0
        if '[edit]' in line:
            st = line.split('[')
            state = st[0]
            state_change = 1
        else:
            reg = re.findall(r"^[^\(]+",line)
            region = reg[0].strip()
        
        if state_change == 1:
            continue
        else:
            state_uni.append([state,region])
    
    data = pd.DataFrame(data=state_uni, columns=["State", "RegionName"])
    
    return data


'''Returns the year and quarter of the recession start time as a 
    string value '''
    
def get_gdp_details():
    gdp = pd.read_excel('gdplev.xls')
    column = gdp.columns
    del gdp[column[3]]
    del gdp[column[7]]
    
    col1 = gdp['Unnamed: 1'][4]
    col2 = gdp['Unnamed: 2'][4]
    col3 = gdp['Unnamed: 4'][1]
    col4 = gdp['Unnamed: 5'][4]
    col5 = gdp['Unnamed: 6'][4]

    gdp.columns = [column[0], col1, col2, col3, 'Gdp', 'Change']
    gdp = gdp[['Quarterly','Gdp','Change']]
    location = gdp[gdp[col3] == '2000q1']
    
    gdp = gdp.loc[location.index[0]:]
    gdp = gdp[['Quarterly','Gdp','Change']]
    
    return gdp

def get_recession_start():
    gdp = get_gdp_details()
    recession_start = ''
    for i in range(len(gdp) - 2):
        if gdp['Gdp'].iloc[i] > gdp['Gdp'].iloc[i+1] and gdp['Gdp'].iloc[i+1] > gdp['Gdp'].iloc[i+2]:
            recession_start = gdp['Quarterly'].iloc[i]
            break
        else:
            continue
    
    return recession_start



'''Returns the year and quarter of the recession end time as a 
    string value'''
    
def get_recession_end():
    gdp = get_gdp_details()
    recession_start = get_recession_start()
    location = gdp[gdp['Quarterly'] == recession_start]
    gdp = gdp.loc[location.index[0]:]
    recession_end = ''
    for i in range(len(gdp) - 2):
        if gdp['Gdp'].iloc[i] < gdp['Gdp'].iloc[i+1] and gdp['Gdp'].iloc[i+1] < gdp['Gdp'].iloc[i+2]:
            recession_end = gdp['Quarterly'].iloc[i+2]
            break
        else:
            continue
    
    return recession_end

'''Returns the year and quarter of the recession bottom time as a 
    string value '''
    
def get_recession_bottom():
    gdp = get_gdp_details()
    recession_start = get_recession_start()
    recession_end = get_recession_end()
    
    location_start = gdp[gdp['Quarterly'] == recession_start]
    location_end = gdp[gdp['Quarterly'] == recession_end]
    
    gdp = gdp.loc[location_start.index[0]:location_end.index[0]+1]
    
    loc_min_gdp = gdp[gdp['Gdp'] == min(gdp['Gdp'])]
    
    recession_bottom = loc_min_gdp['Quarterly'].values[0] 
    
    return recession_bottom


'''Converts the housing data to quarters and returns it as mean 
    values in a dataframe.'''
    
def convert_housing_data_to_quarters():
    czah = get_city_allhomes_data()
    czah.drop(['Metro','CountyName','RegionID','SizeRank'],axis=1,inplace=1)
    
    czah_new = czah.loc[:,'2000-01':]                    
    
    for i in czah_new.columns:
        ar = i.split('-')
        year = ar[0]
        month = ar[1]

        if int(month) <= 3:
            czah_new.rename(columns = {i: year + 'q1'}, inplace=True)

        elif int(month) <= 6 and int(month) > 3:
            czah_new.rename(columns = {i: year + 'q2'}, inplace=True)

        elif int(month) <= 9 and int(month) > 6:
            czah_new.rename(columns = {i: year + 'q3'}, inplace=True)

        else:
            czah_new.rename(columns = {i: year + 'q4'}, inplace=True)

        
    df = czah[czah.columns[0:2].values]
    
    for i in czah_new.columns:
        year = i[:4]
        q_new_val = int(i[5])
        if q_new_val == 1:
            try:
                df[year+'q1'] = czah_new[year+'q1'].mean(axis=1)
            
            except:
                pass
                    
            try:
                df[year+'q2'] = czah_new[year+'q2'].mean(axis=1)    
            
            except:
                pass
                
            try:
                df[year+'q3'] = czah_new[year+'q3'].mean(axis=1)    
            
            except:
                pass
                
            try:
                df[year+'q4'] = czah_new[year+'q4'].mean(axis=1)    
            
            except:
                pass
                
        else:
            continue
    
    df.set_index(['State','RegionName'],inplace=True)
     
    return df



''' Returns the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The
    value for better will depend on whichever out of uni-town or non-uni-town has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
def run_ttest():
    df = convert_housing_data_to_quarters().copy()
    df = df.loc[:,'2008q3':'2009q2']
    df = df.reset_index()
    
    uni = get_list_of_university_towns()
    uniTown = set(uni['RegionName'])
    
    #Functions
    def check_uni_town(data):
        if data['RegionName'] in uniTown:
            return 1
        else:
            return 0
    
    def check_for_decline_and_growth(data):
        return (data['2008q3'] - data['2009q2'])/data['2008q3'] 
    
    def mean_price_ratio(uniData,nonUniData):
        if uniData.mean() > nonUniData.mean():
            return 'non-university town'
        else:
            return 'university town'
        
    
    df['newData'] = df.apply(check_for_decline_and_growth,axis=1)
    
    df['isUniTown'] = df.apply(check_uni_town,axis=1) 
    
    uniTown_data = df[df['isUniTown']==1].loc[:,'newData'].dropna()
    nonUniTown_data = df[df['isUniTown']==0].loc[:,'newData'].dropna()
    
    result = stats.ttest_ind(uniTown_data,nonUniTown_data).pvalue
    if result >= 0.01:
        return (False, result, mean_price_ratio(uniTown_data,nonUniTown_data))
    else:
        return (True, result, mean_price_ratio(uniTown_data,nonUniTown_data))




# List Of uni Towns, extraction From A Text File 
# Recession GDP, etraction from a excel File
# List of All Homes, extraction from a csv File

#A university town is a city which has a high percentage of university students compared to the total population of the city.
lstOfUniTowns = get_list_of_university_towns()
# Start of A recession Period According to the GDP details Provided by the Bureau of Economic Analysis, US Department of Commerce
# A recession is defined as starting with two consecutive quarters of GDP decline, 
startOfRecession = get_recession_start()

# A recession is defined as ending with two consecutive quarters of GDP growth.
endOfRecession = get_recession_end()

#A recession bottom is the quarter within a recession which had the lowest GDP.
bottomOfRecession = get_recession_bottom()

#From the Zillow research data site there is housing data for the United States. In particular the datafile for all homes at a city level, City_Zhvi_AllHomes.csv, has median home sale prices at a fine grained level
convert_housing_data_to_quarters()

# Hypothesis ttest
run_ttest()