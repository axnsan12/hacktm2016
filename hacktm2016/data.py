from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import importer
import ratt

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': 'cache/data',
    'cache.lock_dir': 'cache/lock'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))

known_stations_csv = "Lines Stations and Junctions - Timisoara Public Transport - Denumiri-20152012.csv"
known_lines_csv = "Lines Stations and Junctions - Timisoara Public Transport - Sheet1.csv"


@cache.cache('all_stations', expire=3600*24)
def get_stations():
	return importer.parse_stations_from_csv(known_stations_csv)


@cache.cache('all_lines', expire=3600*24)
def get_lines():
	return importer.parse_lines_from_csv(known_lines_csv)


@cache.cache('all_routes', expire=3600*24)
def get_routes():
	return ratt.get_route_info_from_infotraffic(known_lines_csv, known_stations_csv)