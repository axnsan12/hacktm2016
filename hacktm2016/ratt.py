import re
from typing import List, Sequence
from datetime import datetime, time, timedelta
import pytz
import tzlocal
import traceback

import requests
import grequests

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
		self.lat = lat
		self.lng = lng
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
	def __init__(self, line_id: int, line_name: str, line_type: str, route_name_1: str, route_name_2: str):
		self.line_id = line_id
		self.line_name = line_name
		self.line_type = line_type
		self.route_name_1 = route_name_1
		self.route_name_2 = route_name_2

	def __str__(self):
		return self.line_name

	def __repr__(self):
		return "Line(line_id=%r, line_name=%r, line_type=%r, route_name_1=%r, route_name_2=%r)" % \
		       (self.line_id, self.line_name, self.line_type, self.route_name_1, self.route_name_2)

	def __eq__(self, other) -> bool:
		return self.line_id == other.line_id

	def __ne__(self, other) -> bool:
		return not self == other

	def __hash__(self):
		return hash(self.line_name)


def parse_arrival(now: datetime, line_id: int, station_id: int, arrival: str) -> Arrival:
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


def parse_arrival_from_response(now: datetime, line_id: int, station_id:int, response: requests.Response) -> Arrival:
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
	gets = []
	for station_id in station_ids:
		params = {'id_traseu': line_id, 'id_statie': station_id}
		gets.append(grequests.get(station_time_url, params=params, stream=False))

	arrivals = []
	responses = list(grequests.map(gets, exception_handler=exception_handler))
	tz = pytz.timezone("Europe/Bucharest")
	now = tzlocal.get_localzone().localize(datetime.now()).astimezone(tz).replace(second=0, microsecond=0)
	all_ok = True
	for index, response in enumerate(responses):
		try:
			arrivals.append(parse_arrival_from_response(now, line_id, station_ids[index], response))
		except Exception:
			traceback.print_exc()
			print(response.text)
			arrivals.append(Arrival(line_id, station_ids[index], "xx:xx", -1, False))
			all_ok = False
		finally:
			response.close()

	return arrivals
