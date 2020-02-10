# Geo-Localization-project

A new company in the Gaming industry is being created. The employees showed their preferences on where to place the new office. Bearing in mind this preferences, I tried to found a place that follows some of this requirements. 
- Executives like Starbucks A LOT. Ensure there's a starbucks not to far.
- Account managers need to travel a lot
- The CEO is Vegan
- Nobody in the company likes to have companies with more than 10 years in a radius of 2 KM.
- 30% of the company have at least 1 child.

## INPUT
-companies.csv: Includes a dataset with companies information including the location of its offices.

-airports.geojson: obtained from natural earth page. Includes a geojson with the corrdinates, names and more information about airports.

-directory.csv: Obtained from Kaggle. Includes all the location of all the starbucks around the worl.

## SRC
### Clean data companies, starbucks, airport files
Files used to filter the datasets and to obtain the coordinates in geojson format. 

### School_vegan_filter
In this file a first filter was done. Using the geoqueries in mongodb, the companies which do not have airports or starbucks near were discared. The remain companies were used to look for schools and vegan restaurants close to it using google Api. 

### Distances
The distances were calculated using the latitutes and longitudes of all coordinates (haversine distance). Finally, a rate was asked to the ponderate those distance. The location was obtained as a result. 

### Map
In order to visualize the result a initial and a final map was performed. 

## OUTPUT 
json files and htlm map

