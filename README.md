# Final_project_si507
## Design an interactive query program about Boston restaurants and weather, and the usage of shared bicycles.

### Final_project_document.pdf: contains the github link, demo video link and necessary explanation and presentation.



**API**
1. National Centers for Environmental Information(weather_data): Get daily weather information in
Boston for the past six years through API key.

**A brief description of how to interact with the program**
1. There are three options for users to choose overall: ask users if they want to search for restaurants information, weather information and bike-sharing 
information in Boston.

**data collection**
1. restaurant_boston.json : contains the six types of restaurants information in Boston
2. weather_boston.json: contains the past six years(2015-2020) weather information in Boston
3. bike_usage_boston.csv: contains the past six years(2015-2020) weather information in Boston
4. weather_bike_boston.json: using date as key to combine the weather data and bike usage data
5. tree_restaurants.json: tree data structure about resaurants information in Boston

**python files**
1. final_main.py: contains the main code about data scrapling/collection, visualization and interaction
2. noaa_api_v2.py: special package for NOAA API
3. Tree_structure.py: tree structure code about resaurants data 
4. print_tree: visualization about tree structure

