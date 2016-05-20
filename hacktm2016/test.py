import ratt
import requests

stations = [3106, 4464, 4502, 8080, 2810, 3620, 2920, 6040, 2923, 2924, 5962, 2926, 2928, 5961, 2947, 5960, 6260, 2948, 2946, 2929, 2927, 5963, 2925, 2922, 6041, 2921, 3602, 2821, 2822, 2889, 4501, 4465, 2768]

from time import time as clock
start = clock()
arrivals = ratt.parse_arrivals_from_infotrafic(1207, requests.get("http://86.122.170.105:61978/html/timpi/sens0.php?param1=1547"))
end = clock()
print("%f seconds" % (end - start))
print(arrivals)