# Scope 3 accounting for transportation and distribution services of Pharma company

## Company Supply chain

<img src="./Assets/XYZ PHARMA (USA).png" width="150px" height="150px"/>

## Assumptions made for the data
1. The Transportation and distribution services are purchased by the reporting company in the reporting year.
2. Category 4 of Scope 9 standards to be considered, i.e. (Upstream transportation and distribution)
3. Destination location has been specified in the 'country' column. Since the city name has not been mentioned, I will assume the Air/Road transport to be in the Capital city and Ocean transport to be at the main port.
4. Source location has been mentioned in the 'Manufacturing Site' column, need to extract the city name and coordinates.

## TO-DO
- [x] Data Finding
- [x] EDA
- [ ] Data Cleaning
    - [x] Fixing weight column and converting the data in tonnes.
    - [x] Addition of coordinates for the source location
        - if mode is AIR then it should be the airport nearest to the manufacturing site. If ocean, then the nearest port of that city. If road then manufacturing place coordinates.
    - [ ] Addition of coordinates for the destination location
        - Get the appropriate location name, port/airport.
    - [ ] Addition of emission factors
    
## Packages used
1. Pandas 
2. Numpy
3. ArcGIS from Geopy