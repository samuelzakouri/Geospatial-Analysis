import pandas as pd
from datetime import date, timedelta
import folium
from folium import Marker
from folium.plugins import MarkerCluster, HeatMap
import math
import time
import webbrowser



def load_data():
    
    # Population Data
    populationData = pd.read_csv('./Data/2019_Census_US_Population_Data_By_State_Lat_Long.csv')
    
    # Get the most recent date for filtering
    freshDate = date.today() - timedelta(days=1)
    freshDate = date.strftime(freshDate,"%Y%m%d")
    freshDate = freshDate[0:4] + "-" + freshDate[4:6] + "-" + freshDate[6:8]
    
    # Vaccination data, for most recent date
    vaccinationData = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv')
    vaccinationByLocation = vaccinationData.loc[(vaccinationData.date == freshDate)][["location", "people_vaccinated"]]
    
    # Vaccination and population data
    vaccinationAndPopulationByLocation = pd.merge(populationData, vaccinationByLocation, left_on='STATE',right_on='location').drop(columns="location")
    
    # Calculate percentage vaccinated by state
    vaccinationAndPopulationByLocation["percent_vaccinated"] = vaccinationAndPopulationByLocation["people_vaccinated"] / vaccinationAndPopulationByLocation["POPESTIMATE2019"]
    
    return populationData, freshDate, vaccinationByLocation, vaccinationAndPopulationByLocation

def percent_maps():
    
    
    # Calculate the total percent vaccinated in the US
    percentageTotal = vaccinationAndPopulationByLocation["people_vaccinated"].sum() / vaccinationAndPopulationByLocation["POPESTIMATE2019"].sum()
    
    # Create the Marker map
    marker_map = folium.Map(location=[42.32,-71.0589], tiles='cartodbpositron', zoom_start=4) 
    
    # Add points to the map
    mc = MarkerCluster()
    for idx, row in vaccinationAndPopulationByLocation.iterrows(): 
        if not math.isnan(row['long']) and not math.isnan(row['lat']):
            mc.add_child(Marker(location=[row['lat'], row['long']],
                                tooltip=str(round(row['percent_vaccinated']*100, 2))+"%"))
    marker_map.add_child(mc)
    
    marker_map.save('Marker.html')
    
    # Create the Heatmap
    heat_map = folium.Map(location=[42.32,-71.0589], tiles='cartodbpositron', zoom_start=4) 
    
    # Add a heatmap to the base map
    HeatMap(data=vaccinationAndPopulationByLocation[['lat', 'long']], radius=10).add_to(heat_map)
    
    heat_map.save('Heat.html')
    
    return percentageTotal

if __name__ == '__main__':
    
    populationData, freshDate, vaccinationByLocation, vaccinationAndPopulationByLocation = load_data()
    percentageTotal = percent_maps()
    
    print(f'\n Percentage Vaccinated in the US: {round(percentageTotal*100, 2)}%') 
    
    time.sleep(5)
    
    webbrowser.open_new_tab('file:///Users/samuel/Documents/Projets/Geospatial_analysis/Marker.html')
    webbrowser.open_new_tab('file:///Users/samuel/Documents/Projets/Geospatial_analysis/Heat.html')
