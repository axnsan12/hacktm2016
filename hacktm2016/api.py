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
	line_types = {line_type for line_type in request.args.get("line_types").split(',') if line_type}
	lines = [line for line in data.get_lines() if line.line_type in line_types]
	return jsonify({'lines': [line.__dict__ for line in lines]})


@app.route("/api/get_nearby_stations")
def get_nearby_stations():
	try:
		lat = float(request.args.get('lat'))
		lng = float(request.args.get('lng'))
		count = int(request.args.get('count')) if 'count' in request.args else 10
	except (ValueError, TypeError) as e:
		response = jsonify({'error': str(e)})
		response.status_code = 400
		return response

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


@app.route("/api/get_routes")
def get_routes():
	line_id = int(request.args.get('line_id'))
	all_routes = data.get_routes()

	routes = all_routes[line_id]
	routes_list = []

	for route in routes:
		stations_dict = []
		for station in route.stations:
			stations_dict.append(station.__dict__)

		routes_list.append({'line_id': route.line_id, 'route_id': route.route_id, 'route_name': route.route_name, 'stations': stations_dict})

	return jsonify({'routes': routes_list})