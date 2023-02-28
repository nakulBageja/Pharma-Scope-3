# Steps taken to create the project

1. Searching for dataset
2. Understanding the dataset and making calculative assumptions
    - Assumptions made should have proper justification.
3. Listing down the data points required for calculations
4. Listing down the calculation formulaes
5. Filtering out the data columns required from main data
6. Exploratory Data Analysis
7. Choosing a single year for calculations
8. Data cleaning of Weight column and Mode column.
9. Getting Source & Destination location coordinates
    1. Got all airport and ports data to find the nearest transport location to the manufacturing site.
    2. Since the datasets of airports and ports are big, I have first tried to find all the airports/ports in the country, if no port/airport is there in the country then we look at the whole continent.
        1. If the mode of transport is Road then the source coordinates will be the manufacturing site. Thus number of modes of transport is 1
        2. If the mode of transport is Air/Ocean then the number of modes of transport will be 2.
            1. Firstly, the items will be transported by Road to the Airport/Port.
            2. Secondly, the items will be transported by Plane/Ship to the destination location.
            3. Thirdly, if the airport/port is located outside the country, the items will still be transported by Road from the manufacturing site
        3. For some manufacturing site, the country or continent was not found. Thus it would be very expensive to run 40000 rows to find nearest port/airport. Can be optimized in next iteration of the project.
    3. Merged the source location df and main df
    4. To get the destination location coordinates, I have first found out the capital of the country given.
    5. Then finding out the airports/ports near to the capital inside the country given.
    6. If no port/airport is there in the country then we look at the whole continent, in this case there 2 modes of transport involved in reaching to the destination.
        1. Firstly, we locate a port or airport outside of the main destination country.
        2. Secondly, we find the coordinates of the capital where the items will be transported through road from the port/airport located outside the country.
10. Finding distance between each coordinates
    1. For calculating the distance through road - openrouteservice api has been used
    2. For calculating the distance through air - great_circle api from geopy has been used
    3. For calculating the distance through sea - searoute api has been used
11. Collecting emission factors (https://www.epa.gov/sites/default/files/2020-04/ghg-emission-factors-hub.xlsx) 
    1. For Road transport the emission factors is => 0.211 Kg CO2e /tonne-mile
    2. For Air transport the emission factors is => 1.165 Kg CO2e/tonne-mile
    3. For Sea transport the emission factors is => 0.041 Kg CO2e/tonne-mile
    - NOTE: These emission factors are general values for each transport type.
12. Performing analysis using PowerBI for following questions:
    1. Which destination has led to maximum emissions
    2. Monthly emissions of the year
    3. Which mode has led to highest emission.
    4. Maximum number of weights being tranferred from which manufacturing site.
    5. Weight carried per mode of transport