# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 23:51:24 2021

@author: Elaine
"""

import noaa_api_v2
from time import sleep
import requests
from bs4 import BeautifulSoup
import secret_final 
import json
import csv
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.renderers.default='browser'
import Tree_structure
import print_tree
import pandas as pd
# =============================================================================
# Step1: obtain data, cache and store them in json files
# 1. Yelp(restaurant_data): Web scraping Yelp restaurant in Boston listings using Requests, BeautifulSoup and Pandas. Accessing data efficiently and responsibly using caching.
# 2. NOAA[National Centers for Environmental Information(weather_data)]: Get daily weather information in Boston for the past six years through API key.
# 3. Blue Bikes: the data is publicly available from Umich’s phpMyAdmin. I save it as csv file 
# ============================================================================= 
# Some basic functions for caching and storing data 
# cache funcations
def load_cache():
    ''' opens the cache file if it exists and loads the JSON into
    a dictionary, which it then returns.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    ''' saves the current state of the cache to disk
   Parameters
   ----------
   cache_dict: dict
       The dictionary to save
   Returns
   -------
   None
   '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    '''
    If the url in cache, retrieve the corresponding values from cache. If not, connect again and save the url in cache.
    Return: url
    '''
    if (url in cache.keys()): # the url is our unique key
        # print("Using cache")
        return cache[url]
    else:
        # print("Fetching")
        sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

# Load the cache, save in global variable 
CACHE_FILE_NAME = 'restaurant_scrape.json'
CACHE_DICT = load_cache()

# store data in json file
def write_json(filepath, data):
    with open(filepath, 'w', encoding="utf-8") as f_out:
        json.dump(data, f_out, ensure_ascii=False, indent=2)   

def read_json(filepath, encoding='utf-8'):
    with open(filepath, 'r', encoding=encoding) as file_obj:
        return json.load(file_obj)

def read_csv_to_dicts(filepath, encoding='utf-8', newline='', delimiter=','):
    """Accepts a file path, creates a file object, and returns a list of dictionaries that
    represent the row values using the cvs.DictReader().

    Parameters:
        filepath (str): path to file
        encoding (str): name of encoding used to decode the file
        newline (str): specifies replacement value for newline '\n'
                       or '\r\n' (Windows) character sequences
        delimiter (str): delimiter that separates the row values

    Returns:
        list: nested dictionaries representing the file contents
     """

    with open(filepath, 'r', newline=newline, encoding=encoding) as file_obj:
        data = []
        reader = csv.DictReader(file_obj, delimiter=delimiter)
        for line in reader:
            data.append(line) # OrderedDict()
            # data.append(dict(line)) # convert OrderedDict() to dict
        return data
    

# =============================================================================
# 1. YELP
'''
# There are six types of restaurants listed on yelp: Burgers, Japanese, Chinese, Mexican, Italian, Thai. Thai restaurants has 14 pages, all other types of restaurants have 24 pages to scrap. 
'''
def request_url(restaurant_type):
    '''
    Parameters: restaurant types(eg:burger, Chinese, Mexican etc)
    scraping multiple pages
                                
    Return: a dictionary about all restaurant information of a type
    '''
    rank_total = []
    name_total = []
    rating_total = []
    review_total = []
    second_type_total = []
    if restaurant_type.lower() == "thai":
        num = 14
    else:
        num = 24    
    # nn=0
    for k in range(num):
        base_url = "https://www.yelp.com/search?cflt=" + str(restaurant_type.lower()) + "&find_loc=Boston%2C%20MA%2C%20United%20States&start="+str(k)+"0"
        response = make_url_request_using_cache(base_url,CACHE_DICT)
        soup = BeautifulSoup(response, 'html.parser')
        restaurant_list = soup.find_all('h4',class_="css-uvzfg9") 
        # restaurant_list contains restaurants' rank and name
        rating_list = soup.find_all('div',class_="attribute__09f24__hqUj7 display--inline-block__09f24__fEDiJ margin-r1__09f24__rN_ga border-color--default__09f24__NPAKY")
        # rating_list contains restaurants' star(rating)
        review_list = soup.find_all('div',class_="attribute__09f24__hqUj7 display--inline-block__09f24__fEDiJ border-color--default__09f24__NPAKY")
        # review_list contains restaurants' number of reviews
        type_list = soup.find_all('span',class_="css-epvm6 display--inline__09f24__c6N_k border-color--default__09f24__NPAKY")
        # type_list contains more characteristic labels for restaurants 
        for i,each in enumerate(restaurant_list):  
            rank = list(each.stripped_strings)[0]
            name = list(each.stripped_strings)[-1]
            # print(rank_name)
            rank_total.append(rank)
            name_total.append(name)
        for i,each in enumerate(rating_list):
            star = float(each.find('div').attrs['aria-label'][:-12])
            rating_total.append(star)
        for i,each in enumerate(review_list):
            review = int(list(each.stripped_strings)[0])
            review_total.append(review)
            # print(review)
        for i,each in enumerate(type_list):
            second_type = each.find_all('p')
            type_des =[]
            for j in second_type:
                des = list(j.stripped_strings)[0]
                type_des.append(des)
            second_type_total.append(type_des)
        # nn += 1
        # print(nn)
    restaurant_total = []
    # Information for each restaurant is presented in the form of a dictionary
    for rank,name,star,review,des in zip(rank_total,name_total,rating_total,review_total,second_type_total):
        restaurant_total.append({
            "rank": rank,
            "name": name,
            "rating": star,
            "reviews_number": review,
            "more description": des})
    return restaurant_total

# A combination of all types of restaurants
def populate_restaurant_info(type_list):
    '''
    Parameters: a list of restaurant types 
    '''
    rests_info = {}   
    for i in type_list:
        rests_info[i] = request_url(i)
    return rests_info

'''
# store restaurants information in json file
type_list = ['Burger','Chinese','Japanese','Mexican','Italian','Thai']
rests_all = populate_restaurant_info(type_list)
write_json("restaurant_boston.json", rests_all)
'''
# =============================================================================
# 2. NOAA
# use another data source: National Centers for Environmental Information 
# The seven core elements are:
    
# date = eg:2015-01-01
# PRCP = Precipitation (tenths of mm)
# SNOW = Snowfall (mm)
# AWND = Average daily wind speed (tenths of meters per second))
# TMAX = Maximum temperature (tenths of degrees C)
# TMIN = Minimum temperature (tenths of degrees C)
# TAVG = Average temperature (tenths of degrees C)
   
# Processed data:
# Date: from 2015-01-01 to 2020-12-31
# Min_temp:  Minimum temperature (degrees C)
# Max_temp:  Maximum temperature (degrees C)
# Avg_temp:  Average temperature (degrees C) 
# PRCP = Precipitation (mm)  
# SNOW = Snowfall (mm)
# AWND = Average daily wind speed (tenths of meters per second)

# =============================================================================
'''
'noaa_api_v2' is the python code officially released by NOAA on github, which is used to publicly query the weather conditions of a specific place in a specific time period in the past

Using API to obtain the Boston's weather information. Because this data acquisition is a one-time, from 2015 to 2020 every day of Boston weather data, therefore, there is no need to use the cache method. Write directly to json file, search during interaction
'''

def noaa_data():
    
    # To search the specific period weather in Boston,GHCND:USW00014739
    client = noaa_api_v2.NOAAData(secret_final.API_key)
    sid = "GHCND:USW00014739"
    total_dates = []
    total_min = []
    total_max = []
    total_avg = []
    total_prcp = []
    total_snow = []
    total_awnd = []
    # count = 0
    
    for j in range(6):
        for i in range(12):
            sleep(2) 
            start = 1+i
            end = 2+i
            if end == 2:
                s = "20" + str(j+15) + "-0" + str(1+i) + "-01"
                e = "20" + str(j+15) + "-0" + str(2+i) + "-01"
            if end > 2 and end < 10:        
                s = "20" + str(j+15) + "-0" + str(1+i) + "-02"
                e = "20" + str(j+15) + "-0" + str(2+i) + "-01"
            if end == 10:
                s = "20" + str(j+15) + "-0" + str(1+i) + "-02"
                e = "20" + str(j+15) + "-" + str(2+i) + "-01"
            if end > 10 and end < 13:
                s = "20" + str(j+15) + "-" + str(1+i) + "-02"
                e = "20" + str(j+15) + "-" + str(2+i) + "-01"
            if end == 13:
                s = "20" + str(j+15) + "-" + str(1+i) + "-02"
                e = "20" + str(j+15) + "-" + str(1+i) + "-31" 
                
            dat = client.fetch_data(datasetid="GHCND", stationid=sid, startdate=s, enddate=e, limit=1000)    
            
            dates = []
            currdate = None
            dailyMin = []
            dailyMax = []
            dailyAvg = []
            dailyPrcp = []
            dailySnow = []
            dailyawnd = []
            for x in dat:
                if x["date"] != currdate:
                    dates.append(x["date"])
                    currdate = x["date"]
                if x["datatype"] == "TMIN":
                    dailyMin.append(x["value"]/10)
                if x["datatype"] == "TMAX":
                    dailyMax.append(x["value"]/10)
                if x["datatype"] == "TAVG":
                    dailyAvg.append(x["value"]/10)
                if x["datatype"] == "PRCP":
                    dailyPrcp.append(x["value"]/10)
                if x["datatype"] == "SNOW":
                    dailySnow.append(x["value"])
                if x["datatype"] == "AWND":
                    dailyawnd.append(x["value"])
            total_dates += dates
            total_min += dailyMin
            total_max += dailyMax
            total_avg += dailyAvg
            total_prcp += dailyPrcp
            total_snow += dailySnow
            total_awnd += dailyawnd
            # count += 1    
            # print(count)
    
    weather_data = []
    for d,mint,maxt,avgt,prcp,snow,awnd in zip(total_dates,total_min,total_max,total_avg,total_prcp,total_snow,total_awnd):
        weather_data.append({
            "date":d[0:10],
            "min_temp":mint,
            "max_temp":maxt,
            "avg_temp":avgt,
            "prcp":prcp,
            "snow":snow,
            "awnd":awnd}
            )
    # store data in json file
    write_json("weather_boston.json", weather_data)
# noaa_data()
 
# Done: Successfully collecting, caching and storing all relevant data from data sources.


# 3. combine weather_data with bike_usage data
def combine_data_weather_usage(weather_data, bike_usage):
    new_data = []
    for i in weather_data:
        for j in bike_usage:
            if i['date'] == j['date']:
                i['bike_usage'] = j['bike_usage']
                new_data.append(i)
    return new_data

# weather_bike_boston = combine_data_weather_usage(weather_data, bike_usage)
# write_json("weather_bike_boston.json", weather_bike_boston)

# =============================================================================
# Step2: Data structure -- Tree_structure.py & print_tree.py
# =============================================================================
'''
tree_rest_all = Tree_structure.tree_type(rests_all,Tree_structure.tree_rest)
write_json("tree_restaurants.json",tree_rest_all)

'''
# rests_all = read_json("restaurant_boston.json")
# weather_data = read_json("weather_boston.json")
# bike_usage = read_csv_to_dicts("bike_usage_boston.csv")
# weather_bike_boston = read_json("weather_bike_boston.json")
# tree_rest_all = read_json("tree_restaurants.json")
# print_tree.print_tree(tree_rest_all)

# =============================================================================
# Step3: Visualization
# =============================================================================
def printData(array):
    pd.set_option('display.max_columns', None)
    print_data = pd.DataFrame(array) 
    print(print_data)

def search_rests_rating(data, rest_type, rating):
    '''
    Parameters:     
        data: List of dictionaries, restaurants data for the specific category the user wants to search for
        rest_type: the type of restaurants the user wants to search for
        rating: the lowest star rating for the restaurant the user wants to search fors
    
    Return:
        list: list of dictionaries meet specific type and rating requirements 
    '''
    rest_type = str(rest_type)
    for key,val in data.items():
        if key.lower() == rest_type.lower():
            rest_info = val
    rest_results = []
    for i in rest_info:
        if i['rating'] >= float(rating):
            rest_results.append(i)
    return rest_results
        

def restaurant_rating_bar_chart(rest_results):
    '''
    Parameters:
        rest_results: List of dictionaries, the restaurants that need to visual by rating
    Return:
        Display the rating distribution of eligible restaurants through a bar chart
    
    '''
    rating_count = {}
    rating_list = [i['rating'] for i in rest_results]
    for i in rating_list:
        rating_count[i] = rating_count.get(i,0) + 1
    xlab = list(rating_count.keys())
    xlab = [str(i) for i in xlab]
    ylab = list(rating_count.values())
    bar_data = go.Bar(x=xlab,y=ylab)
    basic_layout = go.Layout(title = "Rating distribution of eligible restaurants")
    fig = go.Figure(data=bar_data, layout=basic_layout)
    # iplot(fig)
    return fig.show()
    
# test 
# mexican_data = search_rests_rating(rests_all, 'Mexican', 4)  
# bar_mexican = restaurant_rating_bar_chart(mexican_data)  
 
    
def restaurant_reviews_histogram(rest_results):
    '''
    Parameters:
        rest_results: List of dictionaries, the restaurants that need to visual by reviews number
    Return: 
        Display the distribution of the number of reviews of eligible restaurants through a histogram
    '''
    reviews_list = [i['reviews_number'] for i in rest_results]
    fig = px.histogram(reviews_list, title = "Distribution of the number of reviews of eligible restaurants", labels="reviews number")
    return fig.show()
# test
# hist_mexican = restaurant_reviews_histogram(mexican_data)

def temperature_line_chart(weather_bike_boston,start_date,type_temp,end_date=None):
    '''
    Parameters
    ----------
    weather_bike_boston : list of dictionaries, the weather and bike usage data that users want to search for 
    start_date(str) : The (start) date the user wants to query
    type_temp(str) : the type of temperature(average/max/min) the user wants to query
    end_date(str) : optional， the end date the users wants to query

    Returns
    -------
    Display the change in average/max/min temperature over a certain period of 
time through a line chart (if the user enters a date, then show the change of the month that the date belongs to)

    '''
    if type_temp.lower().startswith("av"):
        key = 'avg_temp'
    elif type_temp.lower().startswith("max"):
        key = 'max_temp'
    elif type_temp.lower().startswith("min"):
        key = 'min_temp'
        
    if end_date == None:
        year_mon = start_date[0:7]
        date_list = [i['date'] for i in weather_bike_boston if i['date'][0:7] == year_mon] 
        temp_list = [i[key] for i in weather_bike_boston if i['date'][0:7] == year_mon]
        line_data = go.Line(x=date_list, y=temp_list)
        title = f"The change in {key} during {start_date[0:7]}"
        basic_layout = go.Layout(title = title)
        fig = go.Figure(data=line_data, layout=basic_layout)
        return fig.show()
    else:       
       date_list = [i['date'] for i in weather_bike_boston if i['date'] >= str(start_date) and i['date'] <= str(end_date)]
       temp_list = [i[key] for i in weather_bike_boston if i['date'] >= str(start_date) and i['date'] <= str(end_date)]      
       line_data = go.Line(x=date_list, y=temp_list)
       title = f"The change in {key} between {start_date} and {end_date}"
       basic_layout = go.Layout(title = title)
       fig = go.Figure(data=line_data, layout=basic_layout)
       return fig.show()
        

# test
# date20200820=temperature_line_chart(weather_bike_boston,'2020-08-20','average',end_date=None)
    
def prcp_snow_pie_chart(weather_bike_boston,start_date,type_ps,end_date=None):
    '''
    Parameters:
        weather_bike_boston : list of dictionaries, the weather and bike usage data that users want to search for 
        start_date(str) : The (start) date the user wants to query
        type_ps(str) : the type of precipitation or snowfall the user wants to query
        end_date(str) : optional， the end date the users wants to query
    Return:
        Display the percentage of precipitation or snowfall over a certain period of time through a pie chart (if the user enters a date, then show the percentage of the month that the date belongs to)
    '''
    
    
    if type_ps.lower().startswith("p"):
        key = 'prcp'
    elif type_ps.lower().startswith("s"):
        key = 'snow'
    
    if end_date == None:
        type_yes = [i[key] for i in weather_bike_boston if i['date'][0:7] == start_date[0:7] and i[key] >0]
        type_no = [i[key] for i in weather_bike_boston if i['date'][0:7] == start_date[0:7] and i[key] == 0] 
        labs = [f"{key}", f"no {key}"]
        vals = [len(type_yes),len(type_no)]        
        pie_data = go.Pie(labels = labs, values = vals)
        title = f"The percentage of {key} during {start_date[0:7]}"
        basic_layout = go.Layout(title = title)
        fig = go.Figure(data=pie_data, layout=basic_layout)
        return fig.show()
    else:
        type_yes = [i[key] for i in weather_bike_boston if i['date'] >= start_date and i['date'] <= end_date and i[key] >0]
        type_no = [i[key] for i in weather_bike_boston if i['date'] >= start_date and i['date'] <= end_date and i[key] == 0] 
        labs = [f"{key}", f"no {key}"]
        vals = [len(type_yes),len(type_no)]        
        pie_data = go.Pie(labels = labs, values = vals)   
        title = f"The percentage of {key} between {start_date} and {end_date}"
        basic_layout = go.Layout(title = title)
        fig = go.Figure(data=pie_data, layout=basic_layout)
        return fig.show()
        
# test
# snow_12 = prcp_snow_pie_chart(weather_bike_boston,'2020-12-01','snow','2020-12-30') 

def bike_usage_line_chart(weather_bike_boston,start_date,end_date=None):
    '''
    Parameters:
        weather_bike_boston : list of dictionaries, the weather and bike usage data that users want to search for 
        start_date(str) : The (start) date the user wants to query
        end_date(str) : optional， the end date the users wants to query
    Return:
        Display the change in usage of bicycles over a certain period of time through a line chart (if the user enters a date, then show the percentage of the month that the date belongs to)
    '''
    
    if end_date == None:
        date_list = [i['date'] for i in weather_bike_boston if i['date'][0:7] == start_date[0:7]] 
        usage_list = [int(i['bike_usage']) for i in weather_bike_boston if i['date'][0:7] == start_date[0:7]]
        line_data = go.Line(x=date_list, y=usage_list)
        title = f"The change in bike usage during {start_date[0:7]}"
        basic_layout = go.Layout(title = title)
        fig = go.Figure(data=line_data, layout=basic_layout)
        return fig.show()
    else:       
       date_list = [i['date'] for i in weather_bike_boston if i['date'] >= str(start_date) and i['date'] <= str(end_date)]
       usage_list = [int(i['bike_usage']) for i in weather_bike_boston if i['date'] >= str(start_date) and i['date'] <= str(end_date)]      
       line_data = go.Line(x=date_list, y=usage_list)
       title = f"The change in bike usage between {start_date} and {end_date}"
       basic_layout = go.Layout(title = title)
       fig = go.Figure(data=line_data, layout=basic_layout)
       return fig.show()
    
# test
# usage_2007 = bike_usage_line_chart(weather_bike_boston,start_date='2020-07-01',end_date='2020-08-21')
    
# =============================================================================
# Step4: Interaction    
# =============================================================================
def main():
    
    rests_all = read_json("restaurant_boston.json")
    weather_bike_boston = read_json("weather_bike_boston.json")
    tree_rest_all = read_json("tree_restaurants.json")
    # time = 0
    while True:            
        query = input('Please select the content you want to query. (1)Boston restaurant information: enter A; (2)Boston weather information: enter B; (3)Boston shared bike usage: enter C, or "exit" to quit:\n')
        if query == 'A':
            print("This is a summary of information about the restaurant in Boston: ")
            print_tree.print_tree(tree_rest_all)
            while True:                
                query_rest = input("Please enter the type of restaurant you want to query. There are a couple of options: Burger, Chinese, Japanese, Mexican, Italian, Thai:\n")
                if query_rest.lower() not in ['burger','chinese','japanese','mexican','italian','thai']:
                    print("Invalid input, please enter the following types of restaurants: Burger/Chinese/Japanese/Mexican/Italian/Thai:\n")
                else:                    
                    break
            while True:             
                query_rating = input("Please enter the lowest star rating for restaurants you want to query.(the full score is 5):\n")
                if float(query_rating) < 0 or float(query_rating) > 5:
                    print("Invalid input, please enter the star rating between 0 and 5.\n")
                else:                   
                    rest_results = search_rests_rating(rests_all, query_rest, query_rating)
                    break           
            while True:               
                type_visual = input("Please select the results you want to visualize: (1)the rating distribution: enter a; (2)the reivews number distribution: enter b\n")
                if type_visual == 'a':
                    printData(rest_results)
                    restaurant_rating_bar_chart(rest_results)
                    break
                elif type_visual == 'b':
                    printData(rest_results)
                    restaurant_reviews_histogram(rest_results)
                    break
                else:
                    print("Invalid input, please enter 'a' or 'b' to visual the results you want to display.")
        elif query == 'B':               
            query_start_date = input("Please enter the date(or a period of time, start date and end date) you want to query. Enter the date(or start date) first, and the available query period is from 2015-01-01 to 2020-12-31. input format:2018-08-08\n")
            query_end_date = input("please enter the end date, if you just want to query the weather information for a particular day, please enter: no\n")
                
            if query_end_date == 'no':
                end_date = None
            else:
                end_date = query_end_date
                
            query_type_weather = input("Please select the type of weather results you want to visualize: (1)average/max/min temperature: enter average/min/max; (2) the percentage of precipitation: enter prcp; (3)the percentage of snowfall: enter snow\n")
            while True:
                
                if query_type_weather == 'average' or query_type_weather == 'min' or query_type_weather== 'max':
                    temperature_line_chart(weather_bike_boston,query_start_date,query_type_weather,end_date=end_date)
                    break
                elif query_type_weather == 'prcp' or query_type_weather == 'snow':
                    prcp_snow_pie_chart(weather_bike_boston,query_start_date,query_type_weather,end_date=end_date)
                    break
                else:
                    print("Invalid input, please enter average/min/max/prcp/snow")
        elif query == 'C':
            query_start_date = input("Please enter the date(or a period of time, start date and end date) you want to query. Enter the date(or start date) first, and the available query period is from 2015-01-01 to 2020-12-31. input format:2018-08-08\n")
            query_end_date = input("please enter the end date, if you just want to query the weather information for a particular day, please enter: no\n")
            if query_end_date == 'no':
                end_date = None
            else:
                end_date = query_end_date
            bike_usage_line_chart(weather_bike_boston,query_start_date,end_date=end_date)
        elif query == 'exit':
            break   
        else:
            print("Invalid input.\n")
    
if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    










