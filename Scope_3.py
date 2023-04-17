# Import libraries
import pandas as pd
import numpy as np
import geopandas as gpd

# For point datatype of locations
from shapely.geometry import Point
# For geolocation
from geopy.geocoders import ArcGIS
# Importing the great_circle module for calculation of distance for air transport
from geopy.distance import great_circle
# For calculation of distance for road transport
import openrouteservice
# For calculation of distance for ocean transport
import searoute as sr
# For calculation of source location airport/port
from math import radians, sin, cos, sqrt, atan2, isnan
# For converting country name to iso_2 codes
import country_converter as coco

# Initialising geolocation object
nom = ArcGIS()
cc = coco.CountryConverter()
# Emission Factors

aircraft_EF = 1.165
waterborne_EF = 0.041
truck_EF = 0.211


def mapWeights(weight):
    """
   Function to resolve "See DN-2947 (ID#:83642)" given in weight column and adding the weight
    """
    try:
        if weight.isnumeric() == False:
            ID = weight[-6:-1]
            weight_returned = filtered_df[filtered_df['ID'] == int(
                ID)]['Weight'].iloc[0]
            if weight_returned == 'Weight Captured Separately':
                return None


#             print(f'{ID} -- {weight_returned}')
            return float(weight_returned)
        return float(weight)
    except Exception as e:
        print(
            f'Error == {e} \n {weight[-6:-1]} --- {filtered_df[filtered_df["ID"] == int(weight[-6:-1])]["Weight"].iloc[0]}'
        )


def distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.    

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(
        dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km


def minDistance(transport_df, location, iso2_country, continent):
    """
    Function to find the minimum distance.
    """
    min_distance = float('inf')
    min_latitude = float('inf')
    min_longitude = float('inf')
    """
    Getting all airports/ports lying inside the country. If no airports/ports are found inside the country then, 
    we check for all the airport/ports in the continent.
    """
    transport_df_country = transport_df[transport_df['iso_country'] ==
                                        iso2_country]
    if len(transport_df_country) == 0:
        transport_df_country = transport_df[transport_df['continent'] ==
                                            continent]
        print('Looking at continent now', len(transport_df_country))

    for index, row in transport_df_country.iterrows():
        dist = distance(location.latitude, location.longitude,
                        row['latitude_deg'], row['longitude_deg'])
        if dist <= min_distance:
            min_distance = dist
            min_latitude = row['latitude_deg']
            min_longitude = row['longitude_deg']

    return min_latitude, min_longitude


def getSourceLocation(data):
    """
    Function to get the coordinates of the location
    """
    place = data['Manufacturing_site']
    departure_mode = data['Mode']
    try:
        number_of_transport = 1
        location = nom.geocode(place)
        min_latitude = location.latitude
        min_longitude = location.longitude
        country = nom.reverse(
            str(location.latitude) + ',' +
            str(location.longitude)).address.split(',')[-1].replace(" ", "")
        source_mode = 'Road'

        # Getting iso_2 code for the country
        iso2_country = cc.convert(country, to='ISO2', not_found=None)
        continent = cc.convert(iso2_country,
                               src='ISO2',
                               to='continent',
                               not_found=None)

        # Now that we have location of the manufacturing site. We need to get the Airport/Port location from which the item was transported
        if departure_mode == 'Air':
            number_of_transport = number_of_transport + 1
            min_latitude, min_longitude = minDistance(final_airport_df,
                                                      location, iso2_country,
                                                      continent)
        elif departure_mode == 'Ocean':
            number_of_transport = number_of_transport + 1
            min_latitude, min_longitude = minDistance(final_ports_df, location,
                                                      iso2_country, continent)

        source_locations.loc[len(source_locations.index)] = [
            place,
            Point(location.latitude, location.longitude),
            Point(min_latitude, min_longitude), source_mode, departure_mode,
            number_of_transport, country
        ]

    except Exception as e:
        print(e, place)
        source_locations.loc[len(source_locations.index)] = [
            place, None, None, None, departure_mode, number_of_transport, None
        ]


def getDestinationCoordinates(df):
    '''
    Function to look up the airport and port df to find coordinates of destination location
    '''

    iso_country = df['iso_country']
    arrival_mode = df['Mode']
    destination_mode = 'Road'
    try:
        capital = df['capital']
        continent = df['continent']
        location = nom.geocode(capital)
        min_latitude = location.latitude
        min_longitude = location.longitude
        number_of_transport = 1

        if arrival_mode == 'Air':
            # Check if airport is available for this capital
            number_of_transport = number_of_transport + 1
            min_latitude, min_longitude = minDistance(final_airport_df,
                                                      location, iso_country,
                                                      continent)
        elif arrival_mode == 'Ocean':
            number_of_transport = number_of_transport + 1
            min_latitude, min_longitude = minDistance(final_ports_df, location,
                                                      iso_country, continent)

        destination_result.loc[len(destination_result.index)] = [
            iso_country,
            Point(min_latitude, min_longitude),
            Point(location.latitude, location.longitude), arrival_mode,
            destination_mode, number_of_transport
        ]

    except Exception as e:
        print(e, '==', iso_country, arrival_mode)
        destination_result.loc[len(destination_result.index)] = [
            iso_country,
            Point(min_latitude, min_longitude),
            Point(location.latitude, location.longitude), arrival_mode,
            destination_mode, number_of_transport
        ]


def calculateDistance(data):
    """
    Function to find the distance between coordinates for each transportation mode 'Road', 'Ocean', 'Air'
    """

    source_loc = data['source']
    departure_loc = data['departure']
    arrival_loc = data['arrival']
    destination_loc = data['destination']
    source_mode = data['source_mode']
    destination_mode = data['destination_mode']
    main_mode = data['Mode']
    num_of_transports = data['total_num_of_transports']
    try:
        # Finding road distance
        # This service is free.
        API_KEY = '5b3ce3597851110001cf6248de01212ad45649ddbb4031ce99837efa'
        client = openrouteservice.Client(key=API_KEY)
        #         print(num_of_transports)

        if num_of_transports == 1:
            data['dist_source_to_departure'] = 0
            data['dist_arrival_to_destination'] = 0
            try:
                #                 print(num_of_transports)
                # Complete road travel
                coords = ((source_loc.y, source_loc.x), (destination_loc.y,
                                                         destination_loc.x))
                res = client.directions(coords)
                distance = res['routes'][0]['summary']['distance'] / 1000
                data['dist_departure_to_arrival'] = distance / 1.60934


#                 print('Transportation from source to destination in km', distance)
            except Exception as e:
                print(e, data['source'])
                data['dist_departure_to_arrival'] = None

        else:
            # Transportation from source to departure
            if source_mode == 'Road':
                try:
                    coords = ((source_loc.y, source_loc.x), (departure_loc.y,
                                                             departure_loc.x))
                    res = client.directions(coords)
                    distance = res['routes'][0]['summary']['distance'] / 1000
                    #                     print('Transportation from source to departure distance in km', distance)
                    data['dist_source_to_departure'] = distance / 1.60934
                except Exception as e:
                    #                     print(e, data['source'])
                    data['dist_source_to_departure'] = None

            # Transportation from departure to arrival
            if main_mode == 'Air':
                coords = ((departure_loc.y, departure_loc.x), (arrival_loc.y,
                                                               arrival_loc.x))
                distance = great_circle((departure_loc.x, departure_loc.y),
                                        (arrival_loc.x, arrival_loc.y)).km
                #                 print("Aerial Distance", distance)
                data['dist_departure_to_arrival'] = distance / 1.60934
            else:
                origin = [departure_loc.y, departure_loc.x]
                destination = [arrival_loc.y, arrival_loc.x]
                route = sr.searoute(origin, destination)
                distance = route.properties['length'] / 1.60934
                #                 print("Ocean Distance {:.1f} {}".format(route.properties['length'], route.properties['units']))
                data['dist_departure_to_arrival'] = distance

            # Transportation from arrival to destination
            if source_mode == 'Road':
                try:
                    coords = ((arrival_loc.y, arrival_loc.x),
                              (destination_loc.y, destination_loc.x))
                    res = client.directions(coords)
                    distance = res['routes'][0]['summary']['distance'] / 1000
                    #                     print('Transportation from source to departure distance in km', distance)
                    data['dist_arrival_to_destination'] = distance / 1.60934
                except Exception as e:
                    #                     print(e, data['source'])
                    data['dist_arrival_to_destination'] = None
        return data
    except Exception as e:
        #         print(e, data['source'])
        data['dist_source_to_departure'] = None
        data['dist_arrival_to_destination'] = None
        data['dist_departure_to_arrival'] = None
        return data


def calculateEmissions(data):
    """
    Function to calculated emissions for each distributions
    """

    weight = data['Weight']
    source_mode = data['source_mode']
    destination_mode = data['destination_mode']
    main_mode = data['Mode']
    distance_leg1 = data['dist_source_to_departure']
    distance_leg2 = data['dist_departure_to_arrival']
    distance_leg3 = data['dist_arrival_to_destination']
    total_emissions = 0

    if isnan(distance_leg1):
        data['emissions_source_to_departure'] = None
    else:
        if source_mode == 'Road':
            data['emissions_source_to_departure'] = weight * \
                distance_leg1 * truck_EF
        total_emissions = total_emissions + \
            data['emissions_source_to_departure']

    if isnan(distance_leg2):
        data['emissions_departure_to_arrival'] = None
    else:
        if source_mode == 'Air':
            data['emissions_departure_to_arrival'] = weight * \
                distance_leg2 * aircraft_EF
        else:
            data['emissions_departure_to_arrival'] = weight * \
                distance_leg2 * waterborne_EF
        total_emissions = total_emissions + \
            data['emissions_departure_to_arrival']

    if isnan(distance_leg3):
        data['emissions_arrival_to_destination'] = None
    else:
        if source_mode == 'Road':
            data['emissions_arrival_to_destination'] = weight * \
                distance_leg3 * truck_EF
            total_emissions = total_emissions + \
                data['emissions_arrival_to_destination']

    if total_emissions == 0:
        total_emission = None
    data['total_emissions'] = total_emissions

    return data


if __name__ == "__main__":

    # Collecting Data
    raw_df = pd.read_csv("./Data/SCMS_Delivery_History_Dataset_20150929.csv")

    # Filtering out required columns from the main data.

    filtered_df = raw_df[[
        'ID', 'Country', 'Shipment Mode', 'Manufacturing Site',
        'Weight (Kilograms)', 'Delivery Recorded Date', 'Item Description'
    ]].copy()
    filtered_df.rename(columns={
        "Shipment Mode": "Mode",
        "Weight (Kilograms)": "Weight",
        "Delivery Recorded Date": "Delivery_Date",
        'Manufacturing Site': 'Manufacturing_site',
        'Country': 'Destination_Country'
    },
                       inplace=True)

    # Converting Delivery Date to datetime datatype
    filtered_df.loc[:, 'Delivery_Date'] = pd.to_datetime(
        filtered_df['Delivery_Date'])

    # Cleaning Data
    # Fixing Weight column

    # Filtering out 'Weight Captured Separately' rows from Final dataset
    final_df = filtered_df[(filtered_df['Delivery_Date'].dt.year == 2012) & (
        filtered_df['Weight'] != 'Weight Captured Separately')].copy()
    final_df.reset_index(inplace=True, drop=True)

    weights = final_df['Weight'].apply(mapWeights)

    # Adding weights list to the df
    final_df.loc[:, 'Weight'] = weights

    # Removing None value rows for weight
    final_df = final_df[final_df['Weight'].isna() == False]

    # Converting Weights from KG to Tonnes
    # 1 kilogram = 0.001 tonne

    final_df['Weight'] = final_df['Weight'] * 0.001

    # Fixing Mode column

    final_df.loc[final_df['Mode'] == 'Air Charter', 'Mode'] = 'Air'
    final_df.loc[final_df['Mode'] == 'Truck', 'Mode'] = 'Road'

    # Read airports data
    raw_airport_df = pd.read_csv('Data/airports.csv')
    # Read ports data
    raw_ports_df = gpd.read_file('Data/attributed_ports.geojson')

    # Data cleaning for airports and ports data
    df = raw_airport_df[[
        'type', 'latitude_deg', 'longitude_deg', 'name', 'iso_country',
        'municipality'
    ]]
    final_airport_df = df[df['type'].str.lower().str.contains(
        'airport')].copy()
    final_airport_df['continent'] = coco.convert(
        final_airport_df['iso_country'],
        src='ISO2',
        to='continent',
        not_found=None)

    final_ports_df = raw_ports_df[['Country', 'Name', 'geometry']].copy()
    final_ports_df['latitude_deg'] = final_ports_df.geometry.apply(
        lambda p: p.y)
    final_ports_df['longitude_deg'] = final_ports_df.geometry.apply(
        lambda p: p.x)
    final_ports_df.drop(['geometry'], axis=1, inplace=True)
    final_ports_df['iso_country'] = coco.convert(final_ports_df['Country'],
                                                 to='ISO2',
                                                 not_found=None)
    final_ports_df['continent'] = coco.convert(final_ports_df['iso_country'],
                                               src='ISO2',
                                               to='continent',
                                               not_found=None)

    # Finding source location coordinates
    source_df = final_df[['Manufacturing_site', 'Mode']].copy()

    # Dropping duplicates
    source_df.drop_duplicates(inplace=True)

    # Creating geopandas DF to append Source location
    data = {
        'Manufacturing_site': [],
        'source': [],
        'departure': [],
        'source_mode': [],
        'departure_mode': [],
        'src_num_transport': [],
        'src_country': []
    }
    source_locations = gpd.GeoDataFrame(data)

    # Adding source_latitude and source_longitude columns
    source_df.apply(getSourceLocation, axis=1)

    # Merging the source_location_df to the final_df
    final_df = final_df.merge(
        source_locations,
        how='outer',
        left_on=['Manufacturing_site', 'Mode'],
        right_on=['Manufacturing_site', 'departure_mode'])

    # Checking for any NONE or INF values in source and departure columns
    indexes = final_df.loc[(final_df['source'].apply(
        lambda p: p == None or p.x == float('inf') or p.y == float('inf'))) | (
            final_df['departure'].apply(lambda p: p == None or p.x == float(
                'inf') or p.y == float('inf')))].index

    # Since coordinates of these manufacturing sites were not found, I will drop these.
    final_df.drop(index=indexes, axis=1, inplace=True)

    # Getting ISO_2 codes for each country
    final_df['destination_iso_country'] = coco.convert(
        final_df['Destination_Country'], to='ISO2', not_found=None)

    # Uploading country capital list and cleaning the data
    country_capital = pd.read_csv('Data/country-capital-list.csv')
    country_capital.drop(columns=['type'], axis=1, inplace=True)
    country_capital['iso_country'] = coco.convert(country_capital['country'],
                                                  to='ISO2',
                                                  not_found=None)

    # Merging the main_df and country capital df to get the required capital cities.
    destination_locations = country_capital.merge(
        final_df[['Mode', 'destination_iso_country']],
        right_on='destination_iso_country',
        left_on='iso_country').drop(columns=['destination_iso_country'])

    # Dropping duplicate rows
    destination_locations.drop_duplicates(inplace=True)

    # Adding continents name to destination_locations df
    destination_locations['continent'] = coco.convert(
        destination_locations['country'], to='continent', not_found=None)

    # DF to append Destination location
    data = {
        'iso_country': [],
        'arrival': [],
        'destination': [],
        'arrival_mode': [],
        'destination_mode': [],
        'des_num_transport': []
    }

    destination_result = gpd.GeoDataFrame(data)

    destination_locations.apply(getDestinationCoordinates, axis=1)

    # Check if any inf or none values in arrival and destination columns

    destination_result.loc[(destination_result['arrival'].apply(
        lambda p: p == None or p.x == float('inf') or p.y == float('inf')
    )) | (destination_result['destination'].apply(
        lambda p: p == None or p.x == float('inf') or p.y == float('inf')))]

    # Since no inf or None values, we can merge the destination result with the final_df
    final_df = final_df.merge(destination_result,
                              left_on=['destination_iso_country', 'Mode'],
                              right_on=['iso_country', 'arrival_mode'])

    # Finding out the total number of transports used.

    final_df['total_num_of_transports'] = final_df['src_num_transport'] + \
        final_df['des_num_transport'] - 1

    final_df.drop(columns=[
        'arrival_mode', 'departure_mode', 'iso_country', 'src_num_transport',
        'des_num_transport'
    ],
                  inplace=True)

    # Rearranging the columns in the DF
    final_df = final_df[[
        'ID', 'Item Description', 'Weight', 'Delivery_Date',
        'Destination_Country', 'destination_iso_country', 'Manufacturing_site',
        'Mode', 'source', 'departure', 'source_mode', 'arrival', 'destination',
        'destination_mode', 'total_num_of_transports'
    ]]

    # Getting all the required values and removing duplicated for computations
    distance_df = final_df[[
        'Destination_Country', 'Manufacturing_site', 'Mode', 'source',
        'departure', 'source_mode', 'arrival', 'destination',
        'destination_mode', 'total_num_of_transports'
    ]]

    # Since Point datatype is unhashable, I can't perform drop_duplicates function.
    # Workaround is to convert all the data in str, perform drop duplicates and get the index of the unique values. Then get the rows on those indexes from main df

    indexes = distance_df.loc[distance_df.astype(
        str).drop_duplicates().index].index

    distance_df = distance_df.iloc[indexes]

    results = distance_df.apply(calculateDistance, axis=1)
    # Merging result of distance calculation with the final_df

    # Creating an array of columns to use for merging to avoid duplicate columns
    cols_to_use = [
        'Destination_Country',
        'Manufacturing_site',
        'Mode',
        'dist_arrival_to_destination',
        'dist_departure_to_arrival',
        'dist_source_to_departure',
    ]

    final_df = final_df.merge(
        results[cols_to_use],
        on=['Destination_Country', 'Manufacturing_site', 'Mode'])

    final_df = final_df.apply(calculateEmissions, axis=1)

    final_df.to_csv('./Output/pharma_scope3_category9_emissions.csv')
