from math import sqrt

import data
from init import app
from flask import jsonify, request
import importer


@app.route("/api/get_stations")
def get_stations():
	stations = data.get_stations().values()
	return jsonify({'stations': [station.__dict__ for station in stations]})


@app.route("/api/get_lines")
def get_lines():
	lines = data.get_lines()
	return jsonify({'lines': [line.__dict__ for line in lines]})


@app.route("/api/get_nearby_stations")
def get_nearby_stations():
	lat = float(request.args.get('lat'))
	lng = float(request.args.get('lng'))
	count = int(request.args.get('count'))
	stations = data.get_stations().values()
	sorted_list = []

	for station in stations:
		try:
			dist = ((lat - station.lat) ** 2 + (lng - station.lng) ** 2) ** 0.5
			sorted_list.append((station, dist))
		except TypeError:
			pass

	sorted_list.sort(key=lambda tup: tup[1])

	return jsonify({'stations': [sorted_list[index][0].__dict__ for index in range(count)]})


@app.route("/api/get_arrival_times")
def get_arrival_times():
	line_id = int(request.args.get('line_id'))
	route_id = int(request.args.get('route_id'))
	return jsonify({'arrivals': [arrival.__dict__ for arrival in data.get_arrivals(line_id)[route_id]] })