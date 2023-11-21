import math
from datetime import datetime, timedelta
from collections import deque
import random
import heapq
from heapq import*
import json
import time
from base import* # importing base functions from base.py

def traversalTimes(array):
   return array[2:]

def closestNode(lon, lat, locationDict):
    minDistance = 999999
    closestNode = None
    for key in locationDict:
        distance = euclidean_distance(lon, lat, key[0], key[1])
        if distance < minDistance:
            minDistance = distance
            closestNode = locationDict[key]
    
    return closestNode

def djikstras(driver_node, passenger_node, current_time, adj):
    day_of_week = current_time.weekday() # between 0 - 6

    offset = 0
    if day_of_week == 5 or day_of_week == 6:
        offset = 24
    hour = current_time.hour # between 0 - 23
    shortest = {}
    minheap = [[0, driver_node]]
    heapq.heapify(minheap)

    while minheap:
        weight1, node1 = heapq.heappop(minheap)
        if node1 in shortest:
            continue
        shortest[node1] = weight1

        if node1 == passenger_node:
            break

        for edge in adj[node1]:
            node2 = edge[0]
            weight2 = edge[1][offset+hour]
            if node2 not in shortest:
                heapq.heappush(minheap, [weight1 + weight2, node2])
    
    # returns minutes
    return shortest[passenger_node]*60

#-----------------------------------------------#
# END OF FUNCTIONS, WHERE PROGRAM ACTUALLY STARTS
#-----------------------------------------------#


startTime = time.time()

date_format = "%m/%d/%Y %H:%M:%S"

driversArr = []
with open('drivers.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    thing = False
    for row in spamreader:
      if thing:
        # [0] is the parameter for quitting
        newRow = [0,0,0,0]
        newRow[0] = datetime.strptime(row[0], date_format)
        newRow[1] = float(row[1])
        newRow[2] = float(row[2])
        driversArr.append(newRow)
      else:
        thing = True

passengersArr = []
with open('passengers.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    thing = False
    for row in spamreader:
      if thing:
        newRow = [0,0,0,0,0]
        newRow[0] = datetime.strptime(row[0], date_format)
        newRow[1] = float(row[1])
        newRow[2] = float(row[2])
        newRow[3] = float(row[3])
        newRow[4] = float(row[4])
        passengersArr.append(newRow)
      else:
        thing = True

# sort passengers by date/time
sortedPassengersArr = sorted(passengersArr)

#speed = 0.2/60 # 0.2 degrees per hour

date_string_start = "04/25/2014 00:00:00"
date_string_end = "04/27/2014 23:59:59"

# Convert the string to a datetime object
date_object_start = datetime.strptime(date_string_start, date_format)
date_object_end = datetime.strptime(date_string_end, date_format)

current_time = date_object_start

# Create doubly ended queue for passengers
# Left is earliest, right is latest
passengersQueue = deque(sortedPassengersArr)

# driversArr needs to be a heap because you need to add drivers back into the heap with the correct ordering

heapq.heapify(driversArr)
driversHeap = driversArr


# GRAPH STUFF

# Iterating through edges.csv to obtain dictionary

edges = []
with open('edges.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    thing = False
    for row in spamreader:
      if thing:
        arrayLength = len(row)
        roadLength = float(row[2])

        # you no longer need the roadLength in the new array
        newRow = [0] * (arrayLength-1)

        for i in range(arrayLength):
            if i == 0 or i == 1:
                # these are the startid and endid
                newRow[i] = int(row[i])
                continue

            if i>2:
                # these will be the time taken to travel road on a given hour/day of week
                # distance/speed
                newRow[i-1] = roadLength/float(row[i])

        edges.append(newRow)
      else:
        thing = True


# Creating the dictionary

edgesDict = {}

for i in range(len(edges)):
    currentElement = edges[i]
    startNode = currentElement[0]
    if startNode not in edgesDict:
        # This start node not in dictionary
        edgesDict[startNode] = []
    
    edgesDict[startNode].append([currentElement[1], traversalTimes(currentElement)])


# Creating dictionary of locations -> node id

json_file_path = "node_data.json"

# Open the JSON file and load its content
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

# Now 'data' contains the parsed JSON content as a Python dictionary
nodeID = []
location = []

# Iterate through the dictionary and append values to the list
for key, value in data.items():
    nodeID.append(int(key))
    coordinates = [0,0]

    # longitude/latitude
    coordinates[0] = value['lon']
    coordinates[1] = value['lat']
    location.append(tuple(coordinates))


locationDict = {}

for i in range(len(location)):
   locationDict[location[i]] = nodeID[i]


# Create array of drivers and passengers waiting idlly
idlePassengers = []
idleDrivers = []

# Set up initial distance as large number when computing min distance between idle driver/passenger pair
initialMinTime = 9999999

# Set up counter of 1) passengerTimeSpent - cumulative time from requesting ride to drop off for every passenger and 2) driverProfit - time spent driving passenger to destination MINUS time spent driving TO passenger
passengerTimeSpent = 0
driverProfit = 0

# INITIALIZATION COMPLETE, WHILE LOOP BEGINS
print("START OF WHILE")

while current_time < date_object_end and passengersQueue and driversHeap:

    print("there are ", str(len(driversHeap)), " drivers and ", str(len(passengersQueue)), "remaining passengers")
    # While the endtime has not been reached, and there are still passengers and drivers

    # 3 CASES

    # CASE 1
    if len(idlePassengers) == 0 and len(idleDrivers) == 0:
       # there are no idle drivers or passengers, find the first driver OR passenger (whichever comes first) and update the proper idle array

        if passengersQueue[0] <= driversHeap[0]:
          # next passenger arrives before/same time the next driver, so add the next passenger

            passengerToAdd = passengersQueue.popleft()
            idlePassengers.append(passengerToAdd)

            # update currentTime
            current_time = passengerToAdd[0]

        else:
            # next driver arrives before next passenger requests ride, add next driver
            driverToAdd = heappop(driversHeap)
            idleDrivers.append(driverToAdd)

            # update currentTime
            current_time = driverToAdd[0]
        
        continue

    # CASE 2
    if len(idlePassengers) > len(idleDrivers):
        # there are no idle drivers, but potentially many idle passengers. Find the next available driver (and all the new passengers that request rides by that time) and assign that driver to the idle passenger closest to him

        nextDriver = heappop(driversHeap)
        nextDriverArrivalTime = nextDriver[0]
 
        # Update current_time
        current_time = nextDriverArrivalTime

        # add all new passengers that would request rides by next Driver Arrival Time
        while passengersQueue:
            possibleIdlePassenger = passengersQueue[0]
            if possibleIdlePassenger[0] <= nextDriverArrivalTime:
                # add to idle passengers, popleft from passengersQueue
                idlePassengers.append(passengersQueue.popleft())
            else:
                break

        # Determine which idle passenger is closest to the new Driver

        minTime = initialMinTime
        closestIndex = 0

        # Finding closest node to driver

        driverNode = closestNode(nextDriver[1], nextDriver[2], locationDict)
        passengerNode = 0

        for i in range(len(idlePassengers)):
           
           currentConsideredPassenger = idlePassengers[i]
           # Finding closest node to passenger

           currentPassengerNode = closestNode(currentConsideredPassenger[1], currentConsideredPassenger[2], locationDict)

           travelTime = djikstras(driverNode, currentPassengerNode, current_time, edgesDict)
           if travelTime < minTime:
              minTime = travelTime
              closestIndex = i
              passengerNode = currentPassengerNode

        passengerToBePaired = idlePassengers[closestIndex]
        passengerTimeSpent += (current_time-passengerToBePaired[0]).total_seconds()/60

        
        # Passenger closestIndex is paired up with the driver, can be removed from idlePassengers
        idlePassengers.pop(closestIndex)

              
        #calculate distance between pickup and dropoff, we divide distance by speed

        # I think the simplest assumption is just to calculate time based on dijkstras, not time spent going from off-graph coordinate to node on graph
        pick_up_time = minTime
        driverProfit -= pick_up_time


        # Need to to djikstras on drop off time

        destinationNode = closestNode(passengerToBePaired[3], passengerToBePaired[4], locationDict)
        drop_off_time = djikstras(passengerNode, destinationNode, current_time, edgesDict)
        driverProfit += drop_off_time


        total_estimated_drive_time = pick_up_time + drop_off_time 
        passengerTimeSpent += total_estimated_drive_time


        #add total_estimated_drive_time to driver next available time
        nextDriver[0] = (nextDriverArrivalTime + timedelta(minutes=total_estimated_drive_time))

        #update driver's lat/long to passenger drop off
        nextDriver[1] = passengerToBePaired[3]
        nextDriver[2] = passengerToBePaired[4]

        # Add back into heap
        if not does_driver_exit(nextDriver):
            heapq.heappush(driversHeap, nextDriver)

        continue



    # CASE 3
    if len(idleDrivers) > len(idlePassengers):
        # like CASE 2 - there are no idle passengers, but potentially many idle drivers. Find the next available passenger (and all the new drivers that can service rides by that time) and assign that passenger to the idle driver closest to him

        nextPassenger = passengersQueue.popleft()
        nextPassengerArrivalTime = nextPassenger[0]

        # Update current_time
        current_time = nextPassengerArrivalTime

        # add all new drivers that can service rides by next Passenger Arrival Time
        while driversHeap:
            possibleIdleDriver = driversHeap[0]
            if possibleIdleDriver[0] <= nextPassengerArrivalTime:
                # add to idle drivers, pop from driversHeap
                idleDrivers.append(heappop(driversHeap))
            else:
                break

        # Determine which idle driver is closest to the new passenger

        minTime = initialMinTime
        closestIndex = 0

        # Finding closest node to passenger

        passengerNode = closestNode(nextPassenger[1], nextPassenger[2], locationDict)
        driverNode = 0

        for i in range(len(idleDrivers)):
           currentConsideredDriver = idleDrivers[i]
           # Finding closest node to driver

           currentDriverNode = closestNode(currentConsideredDriver[1], currentConsideredDriver[2], locationDict)

           travelTime = djikstras(passengerNode, currentDriverNode, current_time, edgesDict)
           if travelTime < minTime:
              minTime = travelTime
              closestIndex = i
              driverNode = currentDriverNode


        driverToBePaired = idleDrivers[closestIndex]
        
        # Driver closestIndex is paired up with the passenger, can be removed from idleDrivers
        idleDrivers.pop(closestIndex)



        #calculate distance between pickup and dropoff, we divide distance by speed

        # I think the simplest assumption is just to calculate time based on dijkstras, not time spent going from off-graph coordinate to node on graph
        pick_up_time = minTime
        driverProfit -= minTime

        # Need to to djikstras on drop off time

        destinationNode = closestNode(nextPassenger[3], nextPassenger[4], locationDict)
        drop_off_time = djikstras(passengerNode, destinationNode, current_time, edgesDict)
        driverProfit += drop_off_time

        total_estimated_drive_time = pick_up_time + drop_off_time 
        passengerTimeSpent += total_estimated_drive_time
        

        #add total_estimated_drive_time to driver next available time
        driverToBePaired[0] = (nextPassengerArrivalTime + timedelta(minutes=total_estimated_drive_time))

        #update driver's lat/long to passenger drop off
        driverToBePaired[1] = nextPassenger[3]
        driverToBePaired[2] = nextPassenger[4]

        # Add back into heap
        if not does_driver_exit(driverToBePaired):
            heapq.heappush(driversHeap, driverToBePaired)

        continue
endTime = time.time() - startTime
print("DONE")

print("D1: passenger time spent: ", passengerTimeSpent)
print("D2: driver profit: ", driverProfit)


print("Program took ", str(endTime), " seconds to run")
