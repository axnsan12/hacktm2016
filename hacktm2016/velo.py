from typing import Sequence

import requests
from flask import json


class Station:
	def __init__(self, station_id: int, station_name: str, lat: float, lng: float, total_spots: int,
	             empty_spots: int, is_online: bool):
		self.station_id = station_id
		self.station_name = station_name
		self.lat = float(lat) if lat is not None else None
		self.lng = float(lng) if lng is not None else None
		self.total_spots = total_spots
		self.empty_spots = empty_spots
		self.is_online = is_online

	def __str__(self):
		return self.station_name

	def __repr__(self):
		return "Station(station_id=%r, station_name=%r, lat=%r, lng=%r, total_spots=%r, empty_spots=%r, is_online=%r)" % \
		       (self.station_id, self.station_name, self.lat, self.lng, self.total_spots, self.empty_spots, self.is_online)

	def __eq__(self, other) -> bool:
		return self.station_id == other.station_id

	def __ne__(self, other) -> bool:
		return not self == other

	def __hash__(self):
		return hash(self.station_id)


def get_stations_from_velo() -> Sequence[Station]:
	response = requests.post("http://velotm.ro/Station/Read")
	response.raise_for_status()

	data = json.loads(response.text)
	data = data['Data']

	stations = []

	for station in data:
		if station['Latitude'] <= 0.1:
			continue
		stations.append(Station(station['Id'], station['StationName'], station['Latitude'], station['Longitude'],
		                        station['MaximumNumberOfBikes'], station['EmptySpots'], station['Status'] != 'Offline'))

	return stations
