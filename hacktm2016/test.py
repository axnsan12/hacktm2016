import ratt
import requests

from time import time as clock
start = clock()
known_stations_csv = "Lines Stations and Junctions - Timisoara Public Transport - Denumiri-20152012.csv"
known_lines_csv = "Lines Stations and Junctions - Timisoara Public Transport - Sheet1.csv"
routes = ratt.get_route_info_from_infotraffic(known_lines_csv, known_stations_csv)
end = clock()
print("%f seconds" % (end - start))
print(routes)