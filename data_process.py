import pandas as pd
from geojson import loads
from shapely.geometry import shape

def main():
    # Read csv files
    charging_poles = pd.read_csv("oplaadpalen.csv", sep=";")
    parking_places = pd.read_csv("parkeerplaatsen.csv", sep=";")
    neighbourhoods = pd.read_csv("buurten.csv", sep=";")
    avg_income = pd.read_csv("Gemiddeld besteedbaar huishoudeninkomen (x1000 euro) - 2020 - Buurten.csv", sep=";")

    # Create neighborhood mapping
    neighborhood_mapping = {}
    for index_n, neighborhood in enumerate(neighbourhoods["geo_shape"]):
        neighbor_obj = loads(neighborhood)
        neighbor_location = shape(neighbor_obj)
        neighborhood_name = neighbourhoods['Buurtnaam '][index_n].replace("Buurt ", "")
        neighborhood_mapping[neighbor_location] = neighborhood_name

    # Add neighborhood to charging poles
    for index_cp, charging_pole in enumerate(charging_poles["geo_shape"]):
        charging_obj = loads(charging_pole)
        charging_location = shape(charging_obj)

        for neighbor_location, neighborhood_name in neighborhood_mapping.items():
            if neighbor_location.contains(charging_location):
                charging_poles.loc[index_cp, 'neighbourhood'] = neighborhood_name
                break

    # Add neighborhood to parking places
    for index_pp, parking_place in enumerate(parking_places["geo_shape"]):
        parking_obj = loads(parking_place)
        parking_location = shape(parking_obj)

        for neighbor_location, neighborhood_name in neighborhood_mapping.items():
            if neighbor_location.contains(parking_location):
                parking_places.loc[index_pp, 'neighbourhood'] = neighborhood_name
                break

    
    # check if avg_income has no values "." and replace with 0
    avg_income["Gemiddeld besteedbaar huishoudeninkomen (x1000 euro)|2020"] = avg_income["Gemiddeld besteedbaar huishoudeninkomen (x1000 euro)|2020"].replace(".", 0)
    # Create income mapping
    income_mapping = dict(zip(avg_income["Buurten"], avg_income["Gemiddeld besteedbaar huishoudeninkomen (x1000 euro)|2020"]))

    # Add avg_income to charging poles
    charging_poles['avg_income'] = charging_poles['neighbourhood'].map(income_mapping)

    # Add avg_income to parking places
    parking_places['avg_income'] = parking_places['neighbourhood'].map(income_mapping)
    
    # parking_places = parking_places[parking_places['Type_en_merk ']=='Parkeerplaats Electrisch opladen']

    # Save data to CSV files
    charging_poles.to_csv('charging_poles.csv', index=False)
    parking_places.to_csv('parking_places.csv', index=False)

    print(charging_poles.iloc[0])
    print(parking_places.iloc[0])

if __name__ == "__main__":
    main()