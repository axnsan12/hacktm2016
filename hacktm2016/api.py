from init import app
from flask import jsonify
import importer


@app.route("/api/get_stations")
def get_stations():
	stations = importer.parse_stations_from_csv("Lines Stations and Junctions - Timisoara Public Transport - Denumiri-20152012.csv")
	return jsonify({'stations': [station.__dict__ for station in stations]})

