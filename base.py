import math, random, statistics
import csv

def valueSort(row):
  # comparator for sorting
  date_time = row[0].split(" ")
  date = date_time[0]
  time = date_time[1]
  lat = row[1]
  lon = row[2]

    # map applies the first function (first parameter) to every element in the second parameter (array)
  month, day, year = map(int, date.split('/'))
  hour, minute, second = map(int, time.split(":"))
    # returns tuple
  return (month, day, year, hour, minute, second)

def euclidean_distance(lat1, lon1, lat2, lon2):
    distance = math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)
    return distance

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3959 # Radius of the Earth in miles

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in miles
    distance = R * c

    return distance

def does_driver_exit(available_driver):

    weight = random.uniform(0, 0.10)
    available_driver[3] = available_driver[3] + weight
    if available_driver[3] >= 1: 
        # Driver quit
        return True
    else:
       return False
    
speed = 15/60 # 15 miles per hour, converted to miles per minute for T1-T2