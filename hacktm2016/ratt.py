import re
from typing import List, Sequence, Dict, Tuple, Union
from datetime import datetime, time, timedelta
import pytz
import tzlocal
import traceback
import bs4
import requests
import grequests

import importer

station_time_url = 'http://www.ratt.ro/txt/afis_msg.php'


class Arrival:
	def __init__(self, line_id: int, station_id: int, arrival: str, minutes_left: int, is_real_time: bool):
		self.line_id = line_id
		self.station_id = station_id
		self.arrival = arrival
		self.is_real_time = is_real_time
		self.minutes_left = minutes_left

	def __repr__(self):
		return "Arrival(line_id=%r, station_id=%r, arrival=%r, minutes_left=%r, is_real_time=%r)" % \
		       (self.line_id, self.station_id, self.arrival, self.minutes_left, self.is_real_time)

	def __str__(self):
		return self.arrival


class Station:
	def __init__(self, station_id: int, raw_name: str, friendly_name: str, junction_name: str, lat: float, lng: float, poi_url: str):
		self.station_id = station_id
		self.raw_name = raw_name
		self.friendly_name = friendly_name
		self.junction_name = junction_name
		self.lat = float(lat) if lat is not None else None
		self.lng = float(lng) if lng is not None else None
		self.poi_url = poi_url

	def __str__(self):
		return self.friendly_name

	def __repr__(self):
		return "Station(station_id=%r, raw_name=%r, friendly_name=%r, junction_name=%r, lat=%r, lng=%r, poi_url=%r)" % \
		       (self.station_id, self.raw_name, self.friendly_name, self.junction_name, self.lat, self.lng, self.poi_url)

	def __eq__(self, other) -> bool:
		return self.raw_name == other.raw_name

	def __ne__(self, other) -> bool:
		return not self == other

	def __hash__(self):
		return hash(self.raw_name)


class Line:
	def __init__(self, line_id: int, line_name: str, friendly_name: str, line_type: str, route_name_1: str, route_name_2: str):
		self.line_id = line_id
		self.line_name = line_name
		self.friendly_name = friendly_name
		self.line_type = line_type
		self.route_name_1 = route_name_1
		self.route_name_2 = route_name_2

	def __str__(self):
		return self.friendly_name

	def __repr__(self):
		return "Line(line_id=%r, line_name=%r, friendly_name=%r, line_type=%r, route_name_1=%r, route_name_2=%r)" % \
		       (self.line_id, self.line_name, self.friendly_name, self.line_type, self.route_name_1, self.route_name_2)

	def __eq__(self, other) -> bool:
		return self.line_id == other.line_id

	def __ne__(self, other) -> bool:
		return not self == other

	def __hash__(self):
		return hash(self.line_id)


class Route:
	def __init__(self, route_id: int, route_name: str, line_id: int, stations: Sequence[Station]):
		self.route_id = route_id
		self.route_name = route_name
		self.line_id = line_id
		self.stations = stations

	def __str__(self):
		return self.route_name

	def __repr__(self):
		return "Route(route_id=%r, route_name=%r, line_id=%r, stations=%r)" % \
		       (self.route_id, self.route_name, self.line_id, self.stations)

	def __eq__(self, other) -> bool:
		return self.line_id == other.line_id and self.route_id == other.route_id

	def __ne__(self, other) -> bool:
		return not self == other

	def __hash__(self):
		return hash(self.line_id) * 101 + hash(self.route_id)


def parse_arrival(now: datetime, line_id: int, station_id: int, arrival: str) -> Arrival:
	"""
	Parse arrival time from a string of the form "hh:mm", "mm min.", ">>".

	Parameters
	----------
	now current time in Europe/Bucharest timezone, for calculating minutes until arrival for absolute timestamps
	line_id line ID
	station_id station ID
	arrival arrival string

	Returns
	-------
	Parsed arrival time
	"""
	minutes_left = -1  # type: int
	real_time = False  # type: bool

	estimate = parse_arrival.estimate_re.match(arrival)
	if estimate:
		minutes_left, real_time = int(estimate.group(1)), True
		arrival = arrival.strip('.')
	else:
		scheduled = parse_arrival.schedule_re.match(arrival)
		if scheduled:
			scheduled = time(hour=int(scheduled.group(1)), minute=int(scheduled.group(2)))
			scheduled = now.tzinfo.localize(datetime.combine(now.date(), scheduled))
			if scheduled < now:
				scheduled = now.tzinfo.normalize(scheduled + timedelta(days=1))

			minutes_left, real_time = int((scheduled - now).total_seconds()) // 60, False
		else:
			if parse_arrival.in_station_re.match(arrival):
				minutes_left, real_time = 0, True
				arrival = arrival.strip()

	return Arrival(line_id, station_id, arrival, minutes_left, real_time)


def parse_arrival_from_response(now: datetime, line_id: int, station_id: int, response: requests.Response) -> Arrival:
	"""
	Parse a single arrival time from a html response from the http://www.ratt.ro/txt/ api.

	Parameters
	----------
	now current time in Europe/Bucharest timezone, for calculating minutes until arrival for absolute timestamps
	line_id line ID
	station_id station ID
	response HTML response from http://www.ratt.ro/txt/afis_msg.php?id_traseu={line_id}&id_statie={station_id}

	Returns
	-------
	Parsed arrival time
	"""
	response.raise_for_status()
	arrival = "xx:xx"  # type: str
	if response.status_code == requests.codes.ok:
		arrival = parse_arrival_from_response.arrival_re.search(response.text).group(1)

	return parse_arrival(now, line_id, station_id, arrival)


parse_arrival_from_response.arrival_re = re.compile("Sosire1:[\s]*([^\n\r<]+)")
parse_arrival.estimate_re = re.compile("^(\d*)\s*min\.?$")
parse_arrival.schedule_re = re.compile("^([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$")
parse_arrival.in_station_re = re.compile("^\s*>+\s*$")


def exception_handler(request: grequests.AsyncRequest, exception: Exception):
	print("Exception while handling request %s:\n%s" % (str(request.url), str(exception)))


def get_line_times(line_id: int, station_ids: List[int]) -> Sequence[Arrival]:
	"""
	Get all arrival times for a given line by individual requests to http://www.ratt.ro/txt/
	Parameters
	----------
	line_id
	station_ids

	Returns
	-------
	Station arrival times.
	"""
	gets = []
	for station_id in station_ids:
		params = {'id_traseu': line_id, 'id_statie': station_id}
		gets.append(grequests.get(station_time_url, params=params, stream=False))

	arrivals = []
	responses = list(grequests.map(gets, exception_handler=exception_handler, size=20))
	tz = pytz.timezone("Europe/Bucharest")
	now = tzlocal.get_localzone().localize(datetime.now()).astimezone(tz).replace(second=0, microsecond=0)
	for index, response in enumerate(responses):
		try:
			arrivals.append(parse_arrival_from_response(now, line_id, station_ids[index], response))
		except Exception:
			traceback.print_exc()
			print(response.text)
			arrivals.append(Arrival(line_id, station_ids[index], "xx:xx", -1, False))
		finally:
			response.close()

	return arrivals


def parse_arrivals_from_infotrafic(line_id: int, stations: Dict[str, Station], response: requests.Response, include_unknown_stations: bool = False) -> Tuple[List[Tuple[Union[Station,str], Arrival]]]:
	response.raise_for_status()
	if response.status_code == requests.codes.ok:
		bs = bs4.BeautifulSoup(response.text, "html.parser")
		prevcolor = None
		datacolor = '00BFFF'
		routes = []
		route = None
		tz = pytz.timezone("Europe/Bucharest")
		now = tzlocal.get_localzone().localize(datetime.now()).astimezone(tz).replace(second=0, microsecond=0)
		for row in bs.find_all("table"):
			if row['bgcolor'] == datacolor:
				if prevcolor != datacolor:
					route = []
					routes.append(route)

				cols = row.find_all("b")
				raw_station_name = cols[1].text.strip()
				station = stations.get(raw_station_name, None)
				arrival = parse_arrival(now, line_id, station.station_id if station else -1, cols[2].text)
				if station is not None or include_unknown_stations:
					route.append((station if station is not None else raw_station_name, arrival))

			prevcolor = row['bgcolor']

		return routes if route else None

	return None


def get_route_info_from_infotraffic(known_lines_csv: str, known_stations_csv: str)-> Dict[int, Tuple[Route, Route]]:
	root = 'http://86.122.170.105:61978/html/timpi/'
	urls = [grequests.get(root + 'tram.php', stream=False),
	        grequests.get(root + 'trol.php', stream=False),
	        grequests.get(root + 'auto.php', stream=False)]

	known_lines = { line.line_id: line for line in importer.parse_lines_from_csv(known_lines_csv) }
	known_lines = known_lines  # type: Dict[int, Line]
	known_stations = { station.raw_name: station for station in importer.parse_stations_from_csv(known_stations_csv) }
	known_stations = known_stations  # type: Dict[str, Station]
	line_id_re = re.compile("param1=(\d+)")
	line_id_to_routes = {}  # type: Dict[int, Tuple[Route, Route]]
	for page in grequests.imap(urls, size=len(urls), exception_handler=exception_handler):
		page.raise_for_status()
		if page.status_code == requests.codes.ok:
			soup = bs4.BeautifulSoup(page.text, "html.parser")
			unknown_lines = { }  # type: Dict[int, str]
			line_requests = []
			for a in soup.select("div p a"):
				line_id = int(line_id_re.search(a['href']).group(1))
				line = known_lines.get(line_id, None)
				if not line:
					line_name = a['title'] if a.has_attr('title') else None
					if line_name is None:
						img = a.select("img")[0]
						line_name = img['alt'] if img and img.has_attr('alt') else 'unknown'
					unknown_lines[line_id] = line_name
					print("WARNING: unknown line '{line_name}' (line ID: {line_id}) encountered at {url}"
					      .format(line_name=line_name, line_id=line_id, url=page.url))
				line_requests.append(grequests.get(root + a['href'], stream=False))

			for line_response in grequests.imap(line_requests, size=6, exception_handler=exception_handler):
				line_id = int(line_id_re.search(line_response.url).group(1))
				routes = parse_arrivals_from_infotrafic(line_id, known_stations, line_response, include_unknown_stations=True)
				line = known_lines.get(line_id, None)
				line_name = line.line_name if line is not None else unknown_lines.get(line_id, "unknown")
				route1 = route2 = None
				for route_id, route in enumerate(routes):
					valid_stations = []
					for station, arrival in route:
						if not isinstance(station, Station):
							print("WARNING: unknown station '{raw_station_name}' encountered in route {route_id} of line {line_name} (line ID: {line_id})"
							      .format(line_name=line_name, line_id=line_id, route_id=route_id, raw_station_name=station))
						else:
							if not station.lng or not station.lat:
								print("WARNING: station '{station_name}' (station ID: {station_id}) has no GPS coordinates defined"
								      .format(station_name=station.friendly_name, station_id=station.station_id))
							valid_stations.append(station)

					if valid_stations and line is not None:
						if route_id == 0:
							route1 = Route(route_id, line.route_name_1, line.line_id, valid_stations)
						elif route_id == 1:
							route2 = Route(route_id, line.route_name_2, line.line_id, valid_stations)

				if route1 is not None and route2 is not None:
					line_id_to_routes[line.line_id] = (route1, route2)

	return line_id_to_routes


def get_arrivals_from_infotrafic(line_id: int, stations: Dict[str, Station]) -> Tuple[Sequence[Arrival], Sequence[Arrival]]:
	response = requests.get('http://86.122.170.105:61978/html/timpi/sens0.php', params={'param1': line_id})
	routes = parse_arrivals_from_infotrafic(line_id, stations, response)
	return [arrival for station, arrival in routes[0]], [arrival for station, arrival in routes[1]]




