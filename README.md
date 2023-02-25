# Scope 3 accounting for transportation and distribution services of Pharma company

## Company Supply chain

<img src="./Assets/XYZ PHARMA (USA).png" width="350px" height="350px"/>

## Assumptions made for the data
1. The Transportation and distribution services are purchased by the reporting company in the reporting year.
2. Category 4 of Scope 9 standards to be considered, i.e. (Upstream transportation and distribution)
3. Destination location has been specified in the 'country' column. Since the city name has not been mentioned, I will assume:
    1. The Air/Road transport to be in the Capital city, so calculating the nearest airport to the capital city. 
    2. Ocean transport to be the nearest port to the capital city.
4. Source location has been mentioned in the 'Manufacturing Site' column, need to extract the city name and coordinates.
    1. Global data of airports and ports is used to find the nearest transport location to the manufacturing site.
    2. In the airports data, many different types of airports are mentioned. I have considered all the airports for calculating the nearest airport.
5. Emission factors for each transport mode is a generalised value taken from GHG.


## TO-DO
- [x] Data Finding
- [x] EDA
- [x] Data Cleaning
    - [x] Fixing weight column and converting the data in tonnes.
    - [x] Addition of coordinates for the source location
        - if mode is AIR then it should be the airport nearest to the manufacturing site. If ocean, then the nearest port of that city. If road then manufacturing place coordinates.
    - [x] Addition of coordinates for the destination location
        - Get the appropriate location name, port/airport.
    - [x] Finding distance between each coordinates.
    - [x] Addition of emission factors
    - [x] Calculating the emissions
- [ ] Analysis
    
## Packages used
1. Pandas 
2. Numpy
3. ArcGIS from Geopy

## TO:DO FOR OPTIMISATION
- [x] Finding out all the distinct manufacturing site along with it's mode of transport. Then applying getSourceLocation function on that df. Will prevent in calling a function from 1200 times to 80 times.
- [ ] Finding the airport/port even if the country and continent were not found for a location.
- [ ] Combining getSourceLocation and getDestinationCoordinates functions
- [ ] Using better API/Algorithm to calculate Road and Sea distance
- [ ] Optimizing the code and README.