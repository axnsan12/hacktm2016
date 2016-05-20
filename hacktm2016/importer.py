from typing import List

from ratt import Station
import csv


def parse_stations_from_csv(filename: str) -> List[Station]:
	with open(filename, newline='') as csvfile:
		result = set()

		field_names = ['LineID', 'LineName', 'StationID', 'RawStationName', 'FriendlyStationName',
		               'ShortStationName', 'JunctionName', 'Lat', 'Long', 'Invalid', 'Verified',
		               'VerificationDate', 'GoogleMapsID', 'InfoComments']

		filereader = csv.DictReader(csvfile, field_names, delimiter = ',', quotechar = '"')
		for row in filereader:

			try:
				if row['Invalid'] != 'TRUE':
					station = Station(int(row['StationID']), row['RawStationName'], row['ShortStationName'],
					                  row['JunctionName'], float(row['Lat']), float(row['Long']), row['GoogleMapsID'])

					result.add(station)
			except ValueError:
				continue

	return list(result)

