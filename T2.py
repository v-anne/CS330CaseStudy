from datetime import datetime, timedelta
from collections import deque
import heapq
from heapq import*
import time
from base import* # importing base functions from base.py

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

speed = 15/60 # 15 miles per hour, converted to miles per minute

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
numPassengers = len(passengersQueue)
wait_times = []

# INITIALIZATION COMPLETE, WHILE LOOP BEGINS
print("START OF WHILE")

while current_time < date_object_end and passengersQueue and driversHeap:

    #print("there are ", str(len(driversHeap)), " drivers and ", str(len(passengersQueue)), "remaining passengers")
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

        minDistance = initialMinDistance
        closestIndex = 0

        for i in range(len(idlePassengers)):
           distance = haversine_distance(idlePassengers[i][1], idlePassengers[i][2], nextDriver[1], nextDriver[2])
           if distance < minDistance:
              minDistance = distance
              closestIndex = i

        passengerToBePaired = idlePassengers[closestIndex]
        passengerWaitTime = (current_time-passengerToBePaired[0]).total_seconds()/60
        passengerTimeSpent += passengerWaitTime
        
        # Passenger closestIndex is paired up with the driver, can be removed from idlePassengers
        idlePassengers.pop(closestIndex)

              
        #calculate distance between pickup and dropoff, we divide distance by speed
        pick_up_time = haversine_distance(nextDriver[1], nextDriver[2], passengerToBePaired[1], passengerToBePaired[2])/speed
        driverProfit -= pick_up_time


        drop_off_time = haversine_distance(passengerToBePaired[1], passengerToBePaired[2], passengerToBePaired[3], passengerToBePaired[4])/speed
        driverProfit += drop_off_time

        total_estimated_drive_time = pick_up_time + drop_off_time 
        passengerTimeSpent += total_estimated_drive_time
        wait_times.append((passengerWaitTime, total_estimated_drive_time))

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
           distance = haversine_distance(idleDrivers[i][1], idleDrivers[i][2], nextPassenger[1], nextPassenger[2])
           if distance < minDistance:
              minDistance = distance
              closestIndex = i


        driverToBePaired = idleDrivers[closestIndex]
        
        # Driver closestIndex is paired up with the passenger, can be removed from idleDrivers
        idleDrivers.pop(closestIndex)

        #calculate distance between pickup and dropoff, we divide distance by speed
        pick_up_time = minDistance/speed
        driverProfit -= pick_up_time

        drop_off_time = haversine_distance(nextPassenger[1], nextPassenger[2], nextPassenger[3], nextPassenger[4])/speed
        driverProfit += drop_off_time

        total_estimated_drive_time = pick_up_time + drop_off_time 
        passengerTimeSpent += total_estimated_drive_time
        wait_times.append((0, total_estimated_drive_time))

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

waits = [t[0] for t in wait_times]
drives = [t[1] for t in wait_times]
total = [t[0]+t[1] for t in wait_times]

print("D1: total passenger time spent: ", passengerTimeSpent, " minutes")
print("D1: average time per passenger (wait): ", statistics.mean(waits), " minutes")
print("D1: median time per passenger (wait): ", statistics.median(waits), " minutes")
print("D1: average time per passenger (transit): ", statistics.mean(drives), " minutes")
print("D1: median time per passenger (transit): ", statistics.median(drives), " minutes")
print("D1: average time per passenger (wait + transit): ", statistics.mean(total), " minutes")
print("D1: median time per passenger (wait + transit): ", statistics.median(total), " minutes")
print("D2: total driver profit: ", driverProfit, " minutes")
print("D2: average driver profit: ", driverProfit / len(driversArr), " minutes")

print("Program took ", str(endTime), " seconds to run")

'''
import matplotlib.pyplot as plt
plt.hist(waits, bins=100)
plt.xlim(0, 10)
plt.title("Histogram of Wait Times")
plt.xlabel("Wait Time (minutes)")
plt.ylabel("Frequency")
plt.show()

plt.hist(drives, bins=100)
plt.xlim(0, 70)
plt.title("Histogram of Drive Times")
plt.xlabel("Drive Time (minutes)")
plt.ylabel("Frequency")
plt.show()

plt.hist(total, bins=100)
plt.xlim(0, 80)
plt.title("Histogram of Total Times")
plt.xlabel("Total Time (minutes)")
plt.ylabel("Frequency")
plt.show()'''