# Tool for generating a population weighted average road transport distance from Australian Local Government areas

Created by Stephen Northey, University of Technology Sydney

### How to install:

Install python

Install google-maps-python-services via 

$ pip install -U googlemaps

See here if additional instructions necessary - https://github.com/googlemaps/google-maps-services-python

Alternatively, install via

$ pip install -r path/to/requirements.txt

### How to use:
Modify config.ini using a text editor:
- Add your Google Maps API key
- Free API keys are rate limited, so keep batch_size to 25.
- Set your destination coordinates (longitude and latitude in decimal format)
- Set your state filter for origin LGAs. Acceptable values: Australia, New South Wales, Victoria, Tasmania, Queensland, South Australia, Western Australia, Other Territories, Northern Territory, Australian Capital Territory

Run generate_population_weighted_distance_from_LGAs.py. This can be done via the command prompt.

python.exe generate_population_weighted_distance_from_LGAs.py

Two output files will be generated. One containing the population and distance to the destination coordinate for each LGA. Another with just the overall population weighted average road distance.

### How it works
Local Government Area (LGA) Estimated Residence Population (ERP) spatial data was sourced from the Australian Burea of Statistics (ABS).

The centroid of every LGA was computed using qGIS.

This tool then estimates the road transport distance from every LGA centroid to the destination location, using Google Maps API for driving routes.

Weighted road transport distance = sum(distance * population for all LGAs)/total population

### Data Citation:
Australian Bureau of Statistics. (2023-24). Regional population. ABS. https://www.abs.gov.au/statistics/people/population/regional-population/latest-release.
