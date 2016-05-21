from init import app
from flask import jsonify
import importer


@app.route("/api/get_stations")
def get_stations():
	stations = importer.parse_stations_from_csv("Lines Stations and Junctions - Timisoara Public Transport - Denumiri-20152012.csv")
	return jsonify({'stations': [station.__dict__ for station in stations]})


@app.route("/api/get_lines")
def get_lines():
	lines = importer.parse_lines_from_csv("Lines Stations and Junctions - Timisoara Public Transport - Sheet1.csv")
	return jsonify({'lines': [line.__dict__ for line in lines]})