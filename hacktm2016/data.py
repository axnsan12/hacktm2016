from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import importer

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': 'cache/data',
    'cache.lock_dir': 'cache/lock'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))


@cache.cache('all_stations', expire=3600*24)
def get_stations():
	known_stations_csv = "Lines Stations and Junctions - Timisoara Public Transport - Denumiri-20152012.csv"
	return importer.parse_stations_from_csv(known_stations_csv)