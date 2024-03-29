"""
CAPP 30122
Team: Tales of Second City
Author: Suchi Tailor and Fatima Irfan

Code for querying the U.S. Census' API

https://www.census.gov/data/developers/data-sets/acs-5year.html
"""

import variable_defs
from census import Census
from us import states
import pandas as pd
import requests


def extract_2012_ACS5_data(key="7afa3a5a9a46932f7041a1b98355987a68b69cbc"):
    """
    Suchi Tailor

    Use the Census python package to interact with Census API and collect race,
    income, age, home ownership and educational attainment data from all Census
    tracts in Cook County, IL that were published in 2012.

    Inputs: API Key

    Outputs: None - save data as CSV file
    """

    c = Census(key)
    variables_2012 = ("NAME",) + tuple(variable_defs.variables_2012.keys())

    # Cook county FIPS is '031'
    data_2012 = c.acs5dp.state_county_tract(
        variables_2012, states.IL.fips, "031", Census.ALL, year=2012)
    data_2012 = pd.DataFrame(data_2012)
    data_2012 = data_2012.rename(columns=variable_defs.variables_2012)

    data_2012.to_csv("../../data/original/acs5_data_2012.csv", index = False)


def extract_2017_ACS5_data(key="7afa3a5a9a46932f7041a1b98355987a68b69cbc"):
    """
    Suchi Tailor

    Use the Census python package to interact with Census API and collect race,
    income, age, home ownership and educational attainment data from all Census
    tracts in Cook County, IL that were published in 2017.

    Inputs: API Key

    Outputs: None - save data as CSV file
    """

    c = Census(key)
    variables_2017 = ("NAME",) + tuple(variable_defs.variables_2017.keys())

    # Cook county FIPS is '031'
    data_2017 = c.acs5dp.state_county_tract(
        variables_2017, states.IL.fips, "031", Census.ALL, year=2017
    )

    data_2017 = pd.DataFrame(data_2017)
    data_2017 = data_2017.rename(columns=variable_defs.variables_2017)

    data_2017.to_csv("../../data/original/acs5_data_2017.csv", index = False)


def extract_2022_ACS5_data(key="7afa3a5a9a46932f7041a1b98355987a68b69cbc"):
    """
    Suchi Tailor

    Create Census API query and collect race, income, age, home ownership and
    educational attainment data from all Census tracts in Cook County, IL that
    were published in 2012. -- this workaround function accomdates for
    the fact that the 2022 census data is not yet in the Census python package.

    Input: API Key

    Output: None - save data as CSV file
    """
    # code based loosely on Jennifer Yeaton's code (Snow Laughing Matter, 2023)

    # Build out API Query
    base_url = "https://api.census.gov/data/2021/acs/acs5/profile?get="
    variables_2022 = "NAME," + ",".join(variable_defs.variables_2022.keys())
    geo_string = "&for=tract:*&in=county:031&in=state:17"
    key_string = "&key=" + key

    full_2022_query = f"{base_url}{variables_2022}{geo_string}{key_string}"
    data_2022 = requests.get(full_2022_query)

    # Convert to panda df with column names
    col_names = (
        ["Name"]
        + list(variable_defs.variables_2022.values())
        + ["State code", "County code", "Tract Code"]
    )
    data_2022 = pd.DataFrame(data=data_2022.json()[1:], columns=col_names)

    data_2022.to_csv("../../data/original/acs5_data_2022.csv", index = False)

def merge_dfs():
    """
    Fatima Irfan

    Merge together census data in each year to create one consolidated 
    dataset.

    Inputs: 
        None

    Outputs: 
        merged_acs (pandas df): merged dataset
    """
    data_2012 = pd.read_csv("../../data/original/acs5_data_2012.csv", index_col = False)
    data_2017 = pd.read_csv("../../data/original/acs5_data_2017.csv", index_col = False)
    data_2017 = data_2017.iloc[:,1:]
    data_2022 = pd.read_csv("../../data/original/acs5_data_2022.csv", index_col = False)
    
    data_2012.drop(columns = ['state','county'],inplace=True)
    data_2017.drop(columns = ['NAME','state','county','Age: < 18'],inplace=True)
    data_2022.drop(columns = ['State code','County code',
                              'Name','Age: < 18'],inplace=True)
    data_2022 = data_2022.add_suffix("_2022")

    merged_acs = pd.merge(data_2012,data_2017,on="tract",suffixes=["_2012","_2017"])
    merged_acs = pd.merge(merged_acs,data_2022,left_on="tract",right_on = "Tract Code_2022")
    merged_acs.drop(columns= ['Tract Code_2022'],inplace=True)
    merged_acs["tract"] = merged_acs["tract"].astype(str)
    
    return merged_acs