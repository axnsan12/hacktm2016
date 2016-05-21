import ratt
import csv


def parse_stations_from_csv(filename: str):
	with open(filename, newline='') as csvfile:
		result = set()

		field_names = ['LineID', 'LineName', 'StationID', 'RawStationName', 'FriendlyStationName',
		               'ShortStationName', 'JunctionName', 'Lat', 'Long', 'Invalid', 'Verified',
		               'VerificationDate', 'GoogleMapsID', 'InfoComments']

		filereader = csv.DictReader(csvfile, field_names, delimiter=',', quotechar='"')
		for row in filereader:
			try:
				if row['Invalid'] != 'TRUE':
					try:
						lat, lng = float(row['Lat']), float(row['Long'])
					except ValueError:
						lat, lng = None, None
					station = ratt.Station(int(row['StationID']), row['RawStationName'], row['ShortStationName'],
					                       row['JunctionName'], lat, lng, row['GoogleMapsID'])

					result.add(station)
			except ValueError:
				continue

	return list(result)


def parse_lines_from_csv(filename: str):
	with open(filename, newline='') as csvfile:
		result = []
		filereader = csv.DictReader(csvfile, delimiter=',', quotechar ='"')

		for row in filereader:
			line = ratt.Line(int(row['LineID']), row['LineName'], row['FriendlyName'], row['LineType'], row['RouteName1'], row['RouteName2'])
			result.append(line)

		return result

