import heapq
import csv
from collections import deque
from datetime import datetime, timedelta
import random
import math

driversArr = []
with open('drivers.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    thing = False
    for row in spamreader:
      if thing:
        row[0] = datetime.strptime(row[0], "%m/%d/%Y %H:%M:%S")
        row[1] = float(row[1])
        row[2] = float(row[2])
        driversArr.append(row)
      else:
        print(row)
      thing = True

passengersArr = []
with open('passengers.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    thing = False
    for row in spamreader:
      if thing:
        row[0] = datetime.strptime(row[0], "%m/%d/%Y %H:%M:%S")
        row[1] = float(row[1])
        row[2] = float(row[2])
        row[3] = float(row[3])
        row[4] = float(row[4])
        passengersArr.append(row)
      else:
        print(row)
      thing = True

sortedPassengersArr = sorted(passengersArr)

date_string_start = "04/25/2014 00:00:00"
date_string_end = "04/27/2014 23:59:59"
date_format = "%m/%d/%Y %H:%M:%S"

# Convert the beginning and ending strings to a datetime object
date_object_start = datetime.strptime(date_string_start, date_format)
date_object_end = datetime.strptime(date_string_end, date_format)

# From Kevin
# dict 1: adj
    # node id => [node id, [speed0/time, ...speed23/time]]

# dict 2: nodes
    # node_id => (long, lat)

# locate_nearest_node fucntion

def does_driver_exit(available_driver):
    if len(available_driver) == 3:
        available_driver.append(0)

    weight = random.uniform(0, 0.10)
    available_driver[3] = available_driver[3] + weight
    if available_driver[3] >= 1:  
        return True
    
def euclidean_distance(lat1, lon1, lat2, lon2):
    distance = math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)
    return distance

speed = 0.2/60 # 0.2 degrees per hour

#weights should be time it takes to traverse edge
def djikstras(driver_node, passenger_node, current_time, adj):
    day_of_week = current_time.weekday() # between 0 - 6
    hour = current_time.hour # between 0 - 23
    shortest = {}
    minheap = [[0, driver_node]]

    while minheap:
        weight1, node1 = heapq.heappop(minheap)
        if node1 in shortest:
            continue
        shortest[node1] = weight1

        for edge in adj[node1]:
            node2 = edge[0]
            weight2 = edge[1][day_of_week][hour]
            if node2 not in shortest:
                heapq.heappush(minheap, [weight1 + weight2, node2])

    return shortest[passenger_node]*60

#T3 logic
current_time = date_object_start
passengersQueue = deque(sortedPassengersArr)
driversHeap = driversArr
heapq.heapify(driversHeap)

while current_time < date_object_end and passengersQueue and driversHeap:
    most_waited_passenger = passengersQueue.popleft()
    available_drivers = []
    current_available_driver = heapq.heappop(driversHeap)

    current_passenger_time = most_waited_passenger[0]
    current_available_driver_time = current_available_driver[0]

    current_time = max(current_passenger_time, current_available_driver_time) 

    # get all drivers that are available to current passenger
    while current_time >= current_available_driver_time:
        available_drivers.append(current_available_driver)
        current_available_driver = heapq.heappop(driversHeap)
        current_available_driver_time = current_available_driver[0]
    
    # calculate djikstras for each driver in available_drivers
    estimated_pickup_time = []
    passenger_node = locate_nearest_node(most_waited_passenger[1], most_waited_passenger[2])
    for driver in available_drivers:
        #get nearest node from driver
        driver_node = locate_nearest_node(driver[1], driver[2])

        #get shortest path
        pick_up_time = djikstras(driver_node, passenger_node, current_time) 

        #remember to add on time it takes for driver to get to the node
        day_of_week = current_time.weekday() # between 0 - 6
        hour = current_time.hour # between 0 - 23
        driver_to_node_time = euclidean_distance(driver[1], driver[2], nodes[driver_node][0], nodes[driver_node][1])/speed

        total_estimated_time = pick_up_time + driver_to_node_time
        estimated_pickup_time.append(total_estimated_time)
    
    minimum_time_index = -1
    minimum_time = math.inf
    for i in range(len(estimated_pickup_time)):
        if estimated_pickup_time[i] < minimum_time:
            minimum_time_index = i #corresponds to index of driver in available drivers
            minimum_time = estimated_pickup_time[i]
    
    #add other drivers back to the heap
    for i in range(len(available_drivers)):
        if i != minimum_time_index:
            heapq.heappush(driversHeap, available_drivers[i])
    
    matched_driver = available_drivers[minimum_time_index]

    #add total_estimated_drive_time to driver next available time 
    matched_driver[0] = current_available_driver_time + timedelta(minutes=minimum_time)

    #update driver's lat/long to passenger drop off 
    matched_driver[1] = most_waited_passenger[3] 
    matched_driver[2] = most_waited_passenger[4] 

    #logic for driver exiting
    if does_driver_exit(matched_driver): 
        continue
    heapq.heappush(driversHeap, matched_driver) 





