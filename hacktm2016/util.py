import csv
import re

def make_stations_type_from_csv(filename: str):
	with open (filename, newline='') as input_csv_file:

		field_names = ['LineID', 'LineName', 'StationID', 'RawStationName', 'FriendlyStationName',
		               'ShortStationName', 'JunctionName', 'Lat', 'Long', 'Invalid', 'Verified',
		               'VerificationDate', 'GoogleMapsID', 'InfoComments']

		filereader = csv.DictReader(input_csv_file, field_names, delimiter=',', quotechar='"')

		line = None
		regex = re.compile("[^\(]*\(([^\)]+)\)")

		for row in filereader:
			if row['Invalid'] == 'TRUE':
				continue

			if line == None:
				try:
					line_id = int(row['LineID'])
					line_name = row['LineName']
					if line_name.startswith('Tv'):
						line_type = 'tram'
					elif line_name.startswith('Tb'):
						line_type = 'trolley'
					else:
						line_type = 'bus'
					match = regex.search(row['FriendlyStationName'])
					if match:
						route_name_1 = match.group(1)
					line = row
					continue
				except ValueError:
					line = None
					continue

			try:
				int(row['LineID'])
				line = row
			except ValueError:
				match = regex.search(line['FriendlyStationName'])
				if match:
					route_name_2 = match.group(1)
				print(line_id,line_name,line_type,route_name_1,route_name_2,sep='\t')
				line = None

		match = regex.search(line['FriendlyStationName'])
		if match:
			route_name_2 = match.group(1)
		print(line_id, line_name, line_type, route_name_1, route_name_2, sep='\t')
