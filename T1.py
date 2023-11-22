from datetime import datetime, timedelta
from collections import deque
import heapq
from heapq import*
import time
from base import*

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
        print(row)
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
        print(row)
      thing = True

sortedDriversArr = sorted(driversArr)
sortedPassengersArr = sorted(passengersArr)

date_string_start = "04/25/2014 00:00:00"
date_string_end = "04/27/2014 23:59:59"

# Convert the string to a datetime object
date_object_start = datetime.strptime(date_string_start, date_format)
date_object_end = datetime.strptime(date_string_end, date_format)

current_time = date_object_start
passengersQueue = deque(sortedPassengersArr)
driversHeap = sortedDriversArr
heapq.heapify(driversHeap)
cumulative_wait_time = 0
numPassengers = len(passengersQueue)
wait_times = []
driverProfit = 0

while current_time < date_object_end and passengersQueue and driversHeap:
    print("there are ", str(len(driversHeap)), " drivers and ", str(len(passengersQueue)), "remaining passengers")
    most_waited_passenger = passengersQueue.popleft()
    available_driver = heapq.heappop(driversHeap)

    #logic for driver exiting
    while does_driver_exit(available_driver): 
        available_driver = heapq.heappop(driversHeap) 
    
    most_waited_passenger_time = most_waited_passenger[0]
    current_available_driver_time = available_driver[0]

    wait_time = (current_available_driver_time - most_waited_passenger_time).total_seconds()/60
    if wait_time < 0:
        wait_time = 0
    current_time = max(most_waited_passenger_time, current_available_driver_time) 

    #calculate distance between pickup and dropoff, we divide distance by speed 
    pick_up_time = haversine_distance(available_driver[1], available_driver[2], most_waited_passenger[1], most_waited_passenger[2])/speed
    drop_off_time = haversine_distance(most_waited_passenger[1],most_waited_passenger[2], most_waited_passenger[3], most_waited_passenger[4])/speed
    total_estimated_drive_time = pick_up_time + drop_off_time 
    wait_time += total_estimated_drive_time
    driverProfit -= pick_up_time
    driverProfit += drop_off_time

    cumulative_wait_time+=wait_time
    wait_times.append((pick_up_time, drop_off_time))

    #add total_estimated_drive_time to driver next available time 
    available_driver[0] = current_available_driver_time + timedelta(minutes=total_estimated_drive_time)

    #update driver's lat/long to passenger drop off 
    available_driver[1] = most_waited_passenger[3] 
    available_driver[2] = most_waited_passenger[4] 

    heapq.heappush(driversHeap, available_driver)
endTime = time.time() - startTime
print("DONE")

waits = [t[0] for t in wait_times]
drives = [t[1] for t in wait_times]
total = [t[0]+t[1] for t in wait_times]
profitpertrip = [t[1]-t[0] for t in wait_times]

print("D1: total passenger time spent: ", cumulative_wait_time, " minutes")
print("D1: average time per passenger (wait): ", statistics.mean(waits), " minutes")
print("D1: median time per passenger (wait): ", statistics.median(waits), " minutes")
print("D1: average time per passenger (transit): ", statistics.mean(drives), " minutes")
print("D1: median time per passenger (transit): ", statistics.median(drives), " minutes")
print("D1: average time per passenger (wait + transit): ", statistics.mean(total), " minutes")
print("D1: median time per passenger (wait + transit): ", statistics.median(total), " minutes")
print("D2: total driver profit: ", driverProfit, " minutes")
print("D2: average driver profit per trip: ", statistics.mean(profitpertrip), " minutes")
print("D2: median driver profit per trip: ", statistics.median(profitpertrip), " minutes")

print("D3: Program took ", str(endTime), " seconds to run")

import matplotlib.pyplot as plt
plt.hist(total, bins=100)
plt.xlim(0, 80)
plt.title("Histogram of Total Times")
plt.xlabel("Total Time (minutes)")
plt.ylabel("Frequency")
plt.show()

plt.hist(profitpertrip, bins=100)
plt.xlim(0, 80)
plt.title("Histogram of Profit per Trip")
plt.xlabel("Profit (minutes)")
plt.ylabel("Frequency")
plt.show()
'''import matplotlib.pyplot as plt
plt.hist(wait_times, bins=100)
plt.title("Histogram of Wait Times")
plt.xlabel("Wait Time (minutes)")
plt.ylabel("Frequency")
plt.xlim(0, 200)
plt.show()'''