import data
from init import app
from flask import jsonify, request


@app.route("/api/get_stations")
def get_stations():
	stations = data.get_stations().values()
	return jsonify({'stations': [station.__dict__ for station in stations]})


@app.route("/api/get_lines")
def get_lines():
	try:
		line_types = {line_type for line_type in request.args.get("line_types").split(',') if line_type}
		lines = [line for line in data.get_lines() if line.line_type in line_types]
	except (AttributeError, TypeError, ValueError):
		lines = data.get_lines()

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

	stations = [station for station in data.get_stations().values() if station.lat is not None and station.lng is not None]
	sorted_list = sorted(stations, key=lambda station: ((lat - station.lat) ** 2 + (lng - station.lng) ** 2) ** 0.5)

	return jsonify({'stations': [station.__dict__ for station in sorted_list[:count]]})


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


@app.route("/api/get_bike_stations")
def get_bike_stations():
	return jsonify({'bike_stations': [station.__dict__ for station in data.get_bike_stations()]})


@app.route("/api/get_closest_bike_station")
def get_closest_bike_station():
	try:
		lat = float(request.args.get('lat'))
		lng = float(request.args.get('lng'))
	except (ValueError, TypeError) as e:
		response = jsonify({'error': str(e)})
		response.status_code = 400
		return response

	sorted_list = sorted(data.get_bike_stations(), key=lambda station: ((lat - station.lat) ** 2 + (lng - station.lng) ** 2) ** 0.5)

	return jsonify(sorted_list[0].__dict__)
