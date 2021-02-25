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
    populationData = pd.read_csv('./Data/populationbycountry2021lat_long.csv')
    
    # Get the most recent date for filtering
    freshDate = date.today() - timedelta(days=2)
    freshDate = date.strftime(freshDate,"%Y%m%d")
    freshDate = freshDate[0:4] + "-" + freshDate[4:6] + "-" + freshDate[6:8]
    
    # Vaccination data, for most recent date
    vaccinationData = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')
    vaccinationByLocation = vaccinationData.loc[(vaccinationData.date == freshDate)][["location", "people_vaccinated"]].reset_index(drop=True)
    
    # Vaccination and population data
    vaccinationAndPopulationByLocation = pd.merge(populationData, vaccinationByLocation, left_on='Entity',right_on='location').drop(columns="location").dropna(axis=0).reset_index(drop=True)
    
    # Calculate percentage vaccinated by country
    vaccinationAndPopulationByLocation["percent_vaccinated"] = vaccinationAndPopulationByLocation["people_vaccinated"] / vaccinationAndPopulationByLocation["Population"]
    
    return populationData, freshDate, vaccinationByLocation, vaccinationAndPopulationByLocation

def percent_maps():
    
    
    # Calculate the total percent vaccinated in the world
    percentageTotal = vaccinationAndPopulationByLocation["people_vaccinated"].sum() / vaccinationAndPopulationByLocation["Population"].sum()
    
    # Create the Marker map
    marker_map = folium.Map(location=[0,0], tiles='cartodbpositron', zoom_start=2) 

    # Add points to the map
    mc = MarkerCluster()
    for idx, row in vaccinationAndPopulationByLocation.iterrows(): 
        if not math.isnan(row['longitude']) and not math.isnan(row['latitude']):
            mc.add_child(Marker(location=[row['latitude'], row['longitude']],
                            tooltip=str(round(row['percent_vaccinated']*100, 2))+"%"))
    marker_map.add_child(mc)
    
    marker_map.save('MarkerWorld.html')
    
    # Create the Heatmap
    heat_map = folium.Map(location=[0,0], tiles='cartodbpositron', zoom_start=2) 

    # Add a heatmap to the base map
    HeatMap(data=vaccinationAndPopulationByLocation[['latitude', 'longitude']], radius=10).add_to(heat_map)
    
    heat_map.save('HeatWorld.html')
    
    return percentageTotal

if __name__ == '__main__':
    
    populationData, freshDate, vaccinationByLocation, vaccinationAndPopulationByLocation = load_data()
    percentageTotal = percent_maps()
    
    print('Percentage Vaccinated in the world: {}%'.format(round(percentageTotal*100, 2))) 
    
    time.sleep(5)
    
    webbrowser.open_new_tab('file:///Users/samuel/Documents/Projets/Geospatial_analysis/MarkerWorld.html')
    webbrowser.open_new_tab('file:///Users/samuel/Documents/Projets/Geospatial_analysis/HeatWorld.html')
