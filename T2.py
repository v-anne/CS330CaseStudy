import csv
import math
from datetime import datetime, timedelta
from collections import deque
import random
import heapq
from heapq import*
import time


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

def does_driver_exit(available_driver):

    weight = random.uniform(0, 0.10)
    available_driver[3] = available_driver[3] + weight
    if available_driver[3] >= 1: 
        # Driver quit
        return True
    else:
       return False

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

speed = 0.2/60 # 0.2 degrees per hour

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

# Create array of drivers and passengers waiting idlly
idlePassengers = []
idleDrivers = []

# Set up initial distance as large number when computing min distance between idle driver/passenger pair
initialMinDistance = 9999999


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

        if passengersQueue[0][0] <= driversHeap[0][0]:
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

        minDistance = initialMinDistance
        closestIndex = 0

        for i in range(len(idlePassengers)):
           distance = euclidean_distance(idlePassengers[i][1], idlePassengers[i][2], nextDriver[1], nextDriver[2])
           if distance < minDistance:
              minDistance = distance
              closestIndex = i

        passengerToBePaired = idlePassengers[closestIndex]
        passengerTimeSpent += (current_time-passengerToBePaired[0]).total_seconds()/60
        
        # Passenger closestIndex is paired up with the driver, can be removed from idlePassengers
        idlePassengers.pop(closestIndex)

              
        #calculate distance between pickup and dropoff, we divide distance by speed
        pick_up_time = euclidean_distance(nextDriver[1], nextDriver[2], passengerToBePaired[1], passengerToBePaired[2])/speed
        driverProfit -= pick_up_time


        drop_off_time = euclidean_distance(passengerToBePaired[1], passengerToBePaired[2], passengerToBePaired[3], passengerToBePaired[4])/speed
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

        minDistance = initialMinDistance
        closestIndex = 0

        for i in range(len(idleDrivers)):
           distance = euclidean_distance(idleDrivers[i][1], idleDrivers[i][2], nextPassenger[1], nextPassenger[2])
           if distance < minDistance:
              minDistance = distance
              closestIndex = i


        driverToBePaired = idleDrivers[closestIndex]
        
        # Driver closestIndex is paired up with the passenger, can be removed from idleDrivers
        idleDrivers.pop(closestIndex)



        #calculate distance between pickup and dropoff, we divide distance by speed
        pick_up_time = minDistance/speed
        driverProfit -= pick_up_time

        drop_off_time = euclidean_distance(nextPassenger[1], nextPassenger[2], nextPassenger[3], nextPassenger[4])/speed
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


print("DONE")
print("D1: passenger time spent: ", passengerTimeSpent)
print("D2: driver profit: ", driverProfit)

endTime = time.time() - startTime

print("Program took ", str(endTime), " seconds to run")
